from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ModelRegistryBase(BaseModel):
    provider: str
    model_name: str
    api_endpoint: Optional[str] = None
    is_active: Optional[bool] = True
    config: Optional[Dict[str, Any]] = None

class ModelRegistryCreate(ModelRegistryBase):
    pass

class ModelRegistryResponse(ModelRegistryBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class AgentRegistryBase(BaseModel):
    name: str
    version: Optional[str] = "1.0.0"
    description: Optional[str] = None
    status: Optional[str] = "active"
    capabilities: Optional[List[str]] = None
    supported_tools: Optional[List[str]] = None
    supported_models: Optional[List[str]] = None
    prompt_versions: Optional[Dict[str, str]] = None
    metrics: Optional[Dict[str, Any]] = None

class AgentRegistryCreate(AgentRegistryBase):
    pass

class AgentRegistryResponse(AgentRegistryBase):
    id: str

    class Config:
        from_attributes = True

class PromptRegistryBase(BaseModel):
    agent_id: Optional[str] = None
    prompt_name: str
    system_prompt: Optional[str] = None
    developer_prompt: Optional[str] = None
    user_template: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    version: Optional[str] = "1.0.0"
    is_approved: Optional[bool] = True
    rollback_version: Optional[str] = None

class PromptRegistryCreate(PromptRegistryBase):
    pass

class PromptRegistryResponse(PromptRegistryBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ToolRegistryBase(BaseModel):
    name: str
    description: Optional[str] = None
    tool_type: str
    config: Optional[Dict[str, Any]] = None

class ToolRegistryCreate(ToolRegistryBase):
    pass

class ToolRegistryResponse(ToolRegistryBase):
    id: str

    class Config:
        from_attributes = True

class WorkflowRegistryBase(BaseModel):
    name: str
    description: Optional[str] = None
    definition: Dict[str, Any]

class WorkflowRegistryCreate(WorkflowRegistryBase):
    pass

class WorkflowRegistryResponse(WorkflowRegistryBase):
    id: str

    class Config:
        from_attributes = True

class CapabilityRegistryBase(BaseModel):
    name: str
    description: Optional[str] = None
    agent_id: str

class CapabilityRegistryCreate(CapabilityRegistryBase):
    pass

class CapabilityRegistryResponse(CapabilityRegistryBase):
    id: str

    class Config:
        from_attributes = True

class AgentMemoryBase(BaseModel):
    agent_id: str
    session_id: str
    memory_type: str
    key: str
    value: Dict[str, Any]

class AgentMemoryCreate(AgentMemoryBase):
    pass

class AgentMemoryResponse(AgentMemoryBase):
    id: str
    updated_at: datetime

    class Config:
        from_attributes = True

class AgentMetricBase(BaseModel):
    agent_id: str
    execution_id: Optional[str] = None
    latency_ms: Optional[float] = 0.0
    input_tokens: Optional[int] = 0
    output_tokens: Optional[int] = 0
    cost: Optional[float] = 0.0
    status: Optional[str] = "success"
    quality_score: Optional[float] = None
    human_override: Optional[bool] = False

class AgentMetricCreate(AgentMetricBase):
    pass

class AgentMetricResponse(AgentMetricBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ExplainabilityRecordResponse(BaseModel):
    id: str
    execution_id: Optional[str] = None
    inputs: Dict[str, Any]
    retrieved_evidence: Dict[str, Any]
    rules_used: Dict[str, Any]
    prompt_version: Optional[str] = None
    model_version: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class AIConfigBase(BaseModel):
    key: str
    value: Dict[str, Any]
    description: Optional[str] = None

class AIConfigCreate(AIConfigBase):
    pass

class AIConfigResponse(AIConfigBase):
    id: str

    class Config:
        from_attributes = True
