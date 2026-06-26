import os
import time
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

import google.generativeai as genai
from backend.app.core.config import settings
from backend.app.core.logger import logger

# --- Pydantic Output Schemas for AI Analysis ---

class SectionStructure(BaseModel):
    title: str = Field(..., description="Name/title of this section or subsection")
    content: str = Field(..., description="Raw text of this section")
    classification: str = Field(..., description="Label like Introduction, Scope, Requirements, Deliverables, Legal, Submission Instructions")
    confidence: float = Field(..., description="Confidence rating from 0.0 to 1.0", ge=0.0, le=1.0)
    page_start: int = Field(default=1)
    page_end: int = Field(default=1)
    subsections: List['SectionStructure'] = Field(default_factory=list, description="Child subsections under this section")

# Resolve forward references
SectionStructure.model_rebuild()

class ExtractedContact(BaseModel):
    organization: Optional[str] = None
    department: Optional[str] = None
    primary_contact: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ExtractionMetadataOutput(BaseModel):
    document_title: str
    client_name: str
    project_name: str
    rfp_number: str
    issue_date: str
    submission_deadline: str
    question_deadline: Optional[str] = None
    contacts: List[ExtractedContact] = Field(default_factory=list)
    quality_score: float = Field(default=1.0, description="Overall document structure quality from 0.0 to 1.0")
    missing_pages_detected: bool = False
    unreadable_sections_detected: bool = False
    corrupted_content_detected: bool = False
    duplicate_sections_detected: bool = False
    empty_sections_detected: bool = False

# --- Prompt Registry ---

PROMPT_REGISTRY = {
    "v1.0": {
        "system_instruction": (
            "You are a Principal AI Document Intelligence Engine. Analyze the following RFP text "
            "and extract its hierarchical structure, metadata, contacts, normalized deadlines, and "
            "document quality metrics. You must strictly validate your response according to the requested schemas."
        ),
        "segmentation_prompt": (
            "Analyze the document text and extract the table of contents and hierarchical sections. "
            "Return a list of structures containing Title, Content, Classification, and confidence scores. Text:\n\n{text}"
        ),
        "metadata_prompt": (
            "Extract rfp document details: client name, project name, rfp number, dates, primary contacts, "
            "and evaluate structural quality (missing pages, unreadable blocks). Text:\n\n{text}"
        )
    }
}


class AIEngineService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-2.5-flash"
        self.prompt_version = "v1.0"
        
        if self.api_key and self.api_key != "your-api-key-here":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"AIEngineService initialized with Gemini Model: {self.model_name}")
        else:
            self.model = None
            logger.warn("AIEngineService: GEMINI_API_KEY not found. Fallback mockup engine active.")

    def run_inference_with_retry(self, prompt: str, schema: Any, retries: int = 3, model_override: Any = None) -> Any:
        active_model = model_override or self.model
        if not active_model:
            return None

        # Exp backoff
        for attempt in range(retries):
            try:
                # Configuring structured outputs using Gemini API Schema
                response = active_model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=schema
                    )
                )
                return response
            except Exception as e:
                logger.warn(f"Gemini API attempt {attempt+1} failed: {str(e)}")
                if attempt == retries - 1:
                    raise e
                time.sleep(2 ** attempt)

    def analyze_document_structure(self, doc_text: str, db: Session = None) -> List[SectionStructure]:
        from backend.app.db.session import SessionLocal
        from backend.app.services.ai_platform import ai_platform_service

        own_db = False
        if not db:
            db = SessionLocal()
            own_db = True

        try:
            ai_platform_service.seed_ai_platform_defaults(db)
            prompt_reg = ai_platform_service.get_prompt(db, "segmentation_prompt", self.prompt_version)
            user_template = prompt_reg.user_template if prompt_reg else PROMPT_REGISTRY[self.prompt_version]["segmentation_prompt"]
            prompt = user_template.format(text=doc_text[:50000])

            active_model_reg = ai_platform_service.get_active_model(db, "gemini")
            model_name = active_model_reg.model_name if active_model_reg else self.model_name

            model_obj = None
            if self.api_key and self.api_key != "your-api-key-here":
                model_obj = genai.GenerativeModel(model_name)

            t0 = time.time()
            response = self.run_inference_with_retry(prompt, List[SectionStructure], model_override=model_obj)
            latency_ms = (time.time() - t0) * 1000

            if not response:
                return self._mock_document_structure()

            data = json.loads(response.text)
            logger.info(f"Document structure successfully analyzed via Gemini. Latency: {latency_ms:.2f}ms")

            ai_platform_service.log_agent_execution(
                db=db,
                agent_id="parser",
                execution_id=None,
                latency_ms=latency_ms,
                input_tokens=len(prompt) // 4,
                output_tokens=len(response.text) // 4,
                cost=0.0,
                status="success"
            )
            ai_platform_service.log_explainability(
                db=db,
                execution_id=None,
                inputs={"text_len": len(doc_text)},
                retrieved_evidence={},
                rules_used={},
                prompt_version=self.prompt_version,
                model_version=model_name,
                confidence=0.9,
                reasoning="Segmented document headings and content",
                output_schema=None
            )
            return [SectionStructure(**item) for item in data]
        except Exception as e:
            logger.error(f"Failed to parse model structure output: {str(e)}")
            return self._mock_document_structure()
        finally:
            if own_db:
                db.close()

    def analyze_document_metadata(self, doc_text: str, db: Session = None) -> ExtractionMetadataOutput:
        from backend.app.db.session import SessionLocal
        from backend.app.services.ai_platform import ai_platform_service

        own_db = False
        if not db:
            db = SessionLocal()
            own_db = True

        try:
            ai_platform_service.seed_ai_platform_defaults(db)
            prompt_reg = ai_platform_service.get_prompt(db, "metadata_prompt", self.prompt_version)
            user_template = prompt_reg.user_template if prompt_reg else PROMPT_REGISTRY[self.prompt_version]["metadata_prompt"]
            prompt = user_template.format(text=doc_text[:50000])

            active_model_reg = ai_platform_service.get_active_model(db, "gemini")
            model_name = active_model_reg.model_name if active_model_reg else self.model_name

            model_obj = None
            if self.api_key and self.api_key != "your-api-key-here":
                model_obj = genai.GenerativeModel(model_name)

            t0 = time.time()
            response = self.run_inference_with_retry(prompt, ExtractionMetadataOutput, model_override=model_obj)
            latency_ms = (time.time() - t0) * 1000

            if not response:
                return self._mock_document_metadata()

            data = json.loads(response.text)
            logger.info(f"Document metadata successfully analyzed via Gemini. Latency: {latency_ms:.2f}ms")

            ai_platform_service.log_agent_execution(
                db=db,
                agent_id="parser",
                execution_id=None,
                latency_ms=latency_ms,
                input_tokens=len(prompt) // 4,
                output_tokens=len(response.text) // 4,
                cost=0.0,
                status="success"
            )
            ai_platform_service.log_explainability(
                db=db,
                execution_id=None,
                inputs={"text_len": len(doc_text)},
                retrieved_evidence={},
                rules_used={},
                prompt_version=self.prompt_version,
                model_version=model_name,
                confidence=0.95,
                reasoning="Extracted metadata fields and quality scores",
                output_schema=None
            )
            return ExtractionMetadataOutput(**data)
        except Exception as e:
            logger.error(f"Failed to parse model metadata output: {str(e)}")
            return self._mock_document_metadata()
        finally:
            if own_db:
                db.close()


    # Mock fallbacks for testing and local environments when API key is missing
    def _mock_document_structure(self) -> List[SectionStructure]:
        return [
            SectionStructure(
                title="1. Introduction and Project Overview",
                content="This is the introduction section detailing the corporate profile and objectives.",
                classification="Introduction",
                confidence=0.95,
                page_start=1,
                page_end=3,
                subsections=[
                    SectionStructure(
                        title="1.1 Scope of Work",
                        content="Detailing the scope parameters of the capture platform.",
                        classification="Scope",
                        confidence=0.90,
                        page_start=2,
                        page_end=3
                    )
                ]
            ),
            SectionStructure(
                title="2. Deliverables & Schedule",
                content="Submission must contain design layout drawings, compliance matrix review sheets.",
                classification="Deliverables",
                confidence=0.88,
                page_start=4,
                page_end=6
            )
        ]

    def _mock_document_metadata(self) -> ExtractionMetadataOutput:
        return ExtractionMetadataOutput(
            document_title="RFP Proposal Capture Manager System Request",
            client_name="SPS Enterprise Solutions",
            project_name="AI Integration Operations Hub",
            rfp_number="RFP-2026-X49",
            issue_date="2026-06-01",
            submission_deadline="2026-07-15",
            question_deadline="2026-06-25",
            contacts=[
                ExtractedContact(
                    organization="SPS",
                    department="Procurement Office",
                    primary_contact="Sarah Jenkins",
                    email="sjenkins@sps-enterprise.com",
                    phone="+1-555-0199"
                )
            ],
            quality_score=0.98
        )

# Global service instance
ai_engine_service = AIEngineService()
