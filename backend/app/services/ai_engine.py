import os
import time
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from groq import Groq
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
        self.api_key = settings.GROQ_API_KEY
        self.model_name = "llama-3.3-70b-versatile"  # Groq's high-performance model
        self.prompt_version = "v1.0"
        
        if self.api_key and self.api_key != "your-api-key-here":
            self.client = Groq(api_key=self.api_key)
            logger.info(f"AIEngineService initialized with Groq Model: {self.model_name}")
        else:
            self.client = None
            logger.warn("AIEngineService: GROQ_API_KEY not found. Fallback mockup engine active.")

    def _clean_json(self, text: str) -> str:
        if not text:
            return ""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        first_brace = text.find('{')
        first_bracket = text.find('[')
        if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
            last_brace = text.rfind('}')
            if last_brace != -1:
                text = text[first_brace:last_brace+1]
        elif first_bracket != -1:
            last_bracket = text.rfind(']')
            if last_bracket != -1:
                text = text[first_bracket:last_bracket+1]
        return text

    def run_inference_with_retry(self, prompt: str, schema: Any = None, retries: int = 3) -> Optional[str]:
        if not self.client:
            logger.warn("No Groq client available. Returning mock response.")
            return json.dumps({"mock": True})

        models_to_try = [self.model_name, "llama-3.1-8b-instant", "qwen/qwen3-32b"]
        for model in models_to_try:
            for attempt in range(retries):
                try:
                    kwargs = {
                        "messages": [
                            {"role": "system", "content": PROMPT_REGISTRY[self.prompt_version]["system_instruction"] + "\nReturn ONLY valid JSON format."},
                            {"role": "user", "content": prompt}
                        ],
                        "model": model,
                        "temperature": 0.3,
                        "max_tokens": 4096
                    }
                    if schema and not (hasattr(schema, "__origin__") and str(schema.__origin__).endswith("list")):
                        kwargs["response_format"] = {"type": "json_object"}
                    response = self.client.chat.completions.create(**kwargs)
                    return self._clean_json(response.choices[0].message.content)
                except Exception as e:
                    err_str = str(e)
                    logger.warn(f"Groq API attempt {attempt+1} with model {model} failed: {err_str}")
                    if "429" in err_str or "rate_limit" in err_str.lower() or "413" in err_str:
                        logger.warn(f"Rate limit hit on {model}, falling back to next available Groq model.")
                        break
                    if attempt == retries - 1 and model == models_to_try[-1]:
                        logger.error(f"All Groq API retries exhausted. Returning mock.")
                        return json.dumps({"mock": True})
                    time.sleep(1)
        return json.dumps({"mock": True})

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 3000, temperature: float = 0.3, retries: int = 3) -> Optional[str]:
        if not self.client:
            return None

        sys_content = system_prompt or "You are an expert AI Assistant and enterprise proposal specialist. Output clean, publication-grade Markdown."
        models_to_try = [self.model_name, "llama-3.1-8b-instant", "qwen/qwen3-32b"]
        for model in models_to_try:
            for attempt in range(retries):
                try:
                    res = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": sys_content},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    content = res.choices[0].message.content
                    if content:
                        return content.strip()
                except Exception as e:
                    err_str = str(e)
                    logger.warning(f"Groq text generation attempt {attempt+1} on model {model} failed: {err_str}")
                    if "429" in err_str or "rate_limit" in err_str.lower() or "413" in err_str:
                        logger.warning(f"Rate limit on {model}, falling back to next available model.")
                        break
                    time.sleep(1)
        return None

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
            prompt = user_template.format(text=doc_text[:16000])

            t0 = time.time()
            response_text = self.run_inference_with_retry(prompt, List[SectionStructure])
            latency_ms = (time.time() - t0) * 1000

            if response_text and "mock" not in response_text:
                try:
                    data = json.loads(response_text)
                    logger.info(f"Document structure successfully analyzed via Groq. Latency: {latency_ms:.2f}ms")
                    return [SectionStructure(**item) for item in data] if isinstance(data, list) else self._mock_document_structure()
                except (json.JSONDecodeError, TypeError):
                    logger.warning("Could not parse Groq JSON response. Using mock.")
                    return self._mock_document_structure()
            
            return self._mock_document_structure()
        except Exception as e:
            logger.error(f"Failed to analyze document structure: {str(e)}")
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
            prompt = user_template.format(text=doc_text[:16000])

            t0 = time.time()
            response_text = self.run_inference_with_retry(prompt, ExtractionMetadataOutput)
            latency_ms = (time.time() - t0) * 1000

            if response_text and "mock" not in response_text:
                try:
                    data = json.loads(response_text)
                    logger.info(f"Document metadata successfully analyzed via Groq. Latency: {latency_ms:.2f}ms")
                    return ExtractionMetadataOutput(**data)
                except (json.JSONDecodeError, TypeError, ValueError):
                    logger.warning("Could not parse Groq metadata response. Using mock.")
                    return self._mock_document_metadata()
            
            return self._mock_document_metadata()
        except Exception as e:
            logger.error(f"Failed to analyze document metadata: {str(e)}")
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
