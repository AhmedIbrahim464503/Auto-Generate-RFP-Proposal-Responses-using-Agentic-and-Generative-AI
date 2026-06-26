from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.ai_platform import (
    ModelRegistry, AgentRegistry, PromptRegistry, AgentMetric, ExplainabilityRecord
)
from backend.app.schemas.ai_platform import (
    ModelRegistryResponse, ModelRegistryCreate,
    AgentRegistryResponse,
    PromptRegistryResponse, PromptRegistryCreate,
    AgentMetricResponse,
    ExplainabilityRecordResponse
)

router = APIRouter()

@router.get("/models", response_model=List[ModelRegistryResponse])
def get_models(db: Session = Depends(get_db)):
    return db.query(ModelRegistry).all()

@router.post("/models", response_model=ModelRegistryResponse)
def create_model(payload: ModelRegistryCreate, db: Session = Depends(get_db)):
    db_model = ModelRegistry(**payload.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

@router.get("/agents", response_model=List[AgentRegistryResponse])
def get_agents(db: Session = Depends(get_db)):
    return db.query(AgentRegistry).all()

@router.get("/prompts", response_model=List[PromptRegistryResponse])
def get_prompts(db: Session = Depends(get_db)):
    return db.query(PromptRegistry).all()

@router.post("/prompts", response_model=PromptRegistryResponse)
def create_prompt(payload: PromptRegistryCreate, db: Session = Depends(get_db)):
    db_prompt = PromptRegistry(**payload.model_dump())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@router.get("/metrics", response_model=List[AgentMetricResponse])
def get_metrics(agent_id: str = None, db: Session = Depends(get_db)):
    query = db.query(AgentMetric)
    if agent_id:
        query = query.filter(AgentMetric.agent_id == agent_id)
    return query.all()

@router.get("/explainability", response_model=List[ExplainabilityRecordResponse])
def get_explainability(execution_id: str = None, db: Session = Depends(get_db)):
    query = db.query(ExplainabilityRecord)
    if execution_id:
        query = query.filter(ExplainabilityRecord.execution_id == execution_id)
    return query.all()
