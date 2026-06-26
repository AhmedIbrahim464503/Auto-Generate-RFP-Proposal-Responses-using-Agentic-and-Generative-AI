from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from backend.app.db.session import get_db
from backend.app.models.ai_platform import (
    AgentRegistry, PromptRegistry, ModelRegistry, ToolRegistry,
    AgentMetric, ExplainabilityRecord, AIConfig, GovernancePolicy
)
from backend.app.schemas.ai_platform import (
    AgentRegistryResponse, PromptRegistryResponse, ModelRegistryResponse,
    ToolRegistryResponse, AgentMetricResponse, ExplainabilityRecordResponse,
    AIConfigResponse, AIConfigCreate
)
from backend.app.core.events.event_bus import event_bus

router = APIRouter()

class GovernancePolicyResponse(BaseModel):
    id: str
    name: str
    rules_payload: Dict[str, Any]
    is_active: bool
    class Config:
        from_attributes = True

# Captured event list
MOCK_EVENTS: List[Dict[str, Any]] = [
    {"event_type": "AgentStarted", "agent_id": "qualification", "execution_id": "1a2b-3c4d", "timestamp": "2026-06-26T23:50:00Z"},
    {"event_type": "AgentCompleted", "agent_id": "qualification", "execution_id": "1a2b-3c4d", "timestamp": "2026-06-26T23:50:05Z"}
]

def event_bus_listener(payload: Dict[str, Any]):
    event_payload = payload.copy()
    if "timestamp" not in event_payload:
        event_payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
    MOCK_EVENTS.append(event_payload)

# Register listener for AI Events
event_bus.subscribe("AgentStarted", event_bus_listener)
event_bus.subscribe("AgentCompleted", event_bus_listener)
event_bus.subscribe("PromptExecuted", event_bus_listener)
event_bus.subscribe("RetrievalCompleted", event_bus_listener)
event_bus.subscribe("GenerationCompleted", event_bus_listener)
event_bus.subscribe("ValidationFailed", event_bus_listener)
event_bus.subscribe("HumanOverride", event_bus_listener)

@router.get("/agents", response_model=List[AgentRegistryResponse])
def get_agents(db: Session = Depends(get_db)):
    return db.query(AgentRegistry).all()

@router.get("/prompts", response_model=List[PromptRegistryResponse])
def get_prompts(db: Session = Depends(get_db)):
    return db.query(PromptRegistry).all()

@router.get("/models", response_model=List[ModelRegistryResponse])
def get_models(db: Session = Depends(get_db)):
    return db.query(ModelRegistry).all()

@router.get("/tools", response_model=List[ToolRegistryResponse])
def get_tools(db: Session = Depends(get_db)):
    return db.query(ToolRegistry).all()

@router.get("/executions", response_model=List[ExplainabilityRecordResponse])
def get_executions(db: Session = Depends(get_db)):
    return db.query(ExplainabilityRecord).all()

@router.get("/events")
def get_events():
    return MOCK_EVENTS

@router.post("/configuration", response_model=AIConfigResponse)
def post_configuration(payload: AIConfigCreate, db: Session = Depends(get_db)):
    cfg = db.query(AIConfig).filter(AIConfig.key == payload.key).first()
    if not cfg:
        cfg = AIConfig(key=payload.key)
    cfg.value = payload.value
    cfg.description = payload.description
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg

@router.get("/metrics", response_model=List[AgentMetricResponse])
def get_metrics(db: Session = Depends(get_db)):
    return db.query(AgentMetric).all()

@router.get("/governance", response_model=List[GovernancePolicyResponse])
def get_governance(db: Session = Depends(get_db)):
    if not db.query(GovernancePolicy).first():
        db.add(GovernancePolicy(
            name="Standard Safety Guardrails Policy",
            rules_payload={
                "pii_redacting": True,
                "prompt_injection_defense": True,
                "safety_safety_words": True
            },
            is_active=True
        ))
        db.commit()
    return db.query(GovernancePolicy).all()
