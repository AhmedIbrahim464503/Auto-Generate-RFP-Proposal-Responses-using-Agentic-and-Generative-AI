import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.ai_platform import (
    ModelRegistry, AgentRegistry, PromptRegistry, ToolRegistry,
    WorkflowRegistry, CapabilityRegistry, AgentMemory, AgentMetric,
    ExplainabilityRecord, AIConfig
)
from backend.app.core.events.event_bus import event_bus
from backend.app.services.ai_governance import ai_governance_service
from backend.app.core.logger import logger

class AIPlatformService:
    def get_active_model(self, db: Session, provider: str = None) -> Optional[ModelRegistry]:
        query = db.query(ModelRegistry).filter(ModelRegistry.is_active == True)
        if provider:
            query = query.filter(ModelRegistry.provider == provider)
        return query.first()

    def get_prompt(self, db: Session, prompt_name: str, version: str = None) -> Optional[PromptRegistry]:
        query = db.query(PromptRegistry).filter(PromptRegistry.prompt_name == prompt_name)
        if version:
            query = query.filter(PromptRegistry.version == version)
        else:
            query = query.order_by(PromptRegistry.version.desc())
        return query.first()

    def resolve_capability(self, db: Session, capability_name: str) -> Optional[str]:
        cap = db.query(CapabilityRegistry).filter(CapabilityRegistry.name == capability_name).first()
        if cap:
            return cap.agent_id
        return None

    def log_agent_execution(
        self,
        db: Session,
        agent_id: str,
        execution_id: Optional[str],
        latency_ms: float,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        status: str,
        quality_score: Optional[float] = None,
        human_override: bool = False
    ) -> AgentMetric:
        metric = AgentMetric(
            agent_id=agent_id,
            execution_id=execution_id,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            status=status,
            quality_score=quality_score,
            human_override=human_override
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

    def log_explainability(
        self,
        db: Session,
        execution_id: Optional[str],
        inputs: Dict[str, Any],
        retrieved_evidence: Dict[str, Any],
        rules_used: Dict[str, Any],
        prompt_version: Optional[str],
        model_version: Optional[str],
        confidence: Optional[float],
        reasoning: Optional[str],
        output_schema: Optional[Dict[str, Any]]
    ) -> ExplainabilityRecord:
        record = ExplainabilityRecord(
            execution_id=execution_id,
            inputs=inputs,
            retrieved_evidence=retrieved_evidence,
            rules_used=rules_used,
            prompt_version=prompt_version,
            model_version=model_version,
            confidence=confidence,
            reasoning=reasoning,
            output_schema=output_schema
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def save_memory(self, db: Session, agent_id: str, session_id: str, memory_type: str, key: str, value: Dict[str, Any]):
        mem = db.query(AgentMemory).filter(
            AgentMemory.agent_id == agent_id,
            AgentMemory.session_id == session_id,
            AgentMemory.memory_type == memory_type,
            AgentMemory.key == key
        ).first()
        if not mem:
            mem = AgentMemory(
                agent_id=agent_id,
                session_id=session_id,
                memory_type=memory_type,
                key=key
            )
        mem.value = value
        db.add(mem)
        db.commit()

    def get_memory(self, db: Session, agent_id: str, session_id: str, memory_type: str, key: str) -> Optional[Dict[str, Any]]:
        mem = db.query(AgentMemory).filter(
            AgentMemory.agent_id == agent_id,
            AgentMemory.session_id == session_id,
            AgentMemory.memory_type == memory_type,
            AgentMemory.key == key
        ).first()
        if mem:
            return mem.value
        return None

    def seed_ai_platform_defaults(self, db: Session):
        # 1. Models
        if not db.query(ModelRegistry).first():
            db.add(ModelRegistry(
                provider="gemini",
                model_name="gemini-2.5-flash",
                is_active=True,
                config={"temperature": 0.2, "max_tokens": 8192}
            ))
        
        # 2. Agents
        agents = [
            ("qualification", "Qualification Agent", "Determines proposal qualification GO/NO_GO"),
            ("planning", "Planning Agent", "Generates outlines, compliance matrices, WBS tasks"),
            ("financial_review", "Financial Review Agent", "Performs financial review checks"),
            ("legal_review", "Legal Review Agent", "Performs legal review checks"),
            ("operations_review", "Operations Review Agent", "Performs operations feasibility checks"),
            ("technical_review", "Technical Review Agent", "Performs technical readiness reviews"),
            ("writer", "Writer Agent", "Generates draft answers for outline sections"),
        ]
        for aid, name, desc in agents:
            if not db.query(AgentRegistry).filter(AgentRegistry.id == aid).first():
                db.add(AgentRegistry(id=aid, name=name, description=desc, capabilities=[aid]))

        # 3. Capabilities
        caps = [
            ("RFP Qualification", "qualification"),
            ("Proposal Planning", "planning"),
            ("Financial Review", "financial_review"),
            ("Legal Review", "legal_review"),
            ("Operations Review", "operations_review"),
            ("Technical Review", "technical_review"),
            ("Proposal Writing", "writer"),
        ]
        for cname, aid in caps:
            if not db.query(CapabilityRegistry).filter(CapabilityRegistry.name == cname).first():
                db.add(CapabilityRegistry(name=cname, agent_id=aid))

        # 4. Prompts
        prompts = [
            ("segmentation_prompt", "segmentation_prompt", "Analyze the document text and extract the table of contents and hierarchical sections. Text:\n\n{text}", "v1.0"),
            ("metadata_prompt", "metadata_prompt", "Extract rfp document details: client name, project name, rfp number, dates, primary contacts, and evaluate structural quality. Text:\n\n{text}", "v1.0"),
        ]
        for name, pkey, template, version in prompts:
            if not db.query(PromptRegistry).filter(PromptRegistry.prompt_name == name, PromptRegistry.version == version).first():
                db.add(PromptRegistry(prompt_name=name, user_template=template, version=version))

        db.commit()

# Global service instance
ai_platform_service = AIPlatformService()

