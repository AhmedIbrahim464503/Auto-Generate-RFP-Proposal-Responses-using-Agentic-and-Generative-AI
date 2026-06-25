from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentOutput(BaseModel):
    decision: str = Field(..., description="Actionable decision or outcome determined by the agent")
    confidence: float = Field(..., description="Numeric confidence rating from 0.0 to 1.0", ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Step-by-step logic supporting the decision")
    evidence: List[str] = Field(..., description="Specific references, citations, or data points extracted")
    risks: List[str] = Field(..., description="Potential bottlenecks, compliancy concerns, or technical risks")
    recommendations: List[str] = Field(..., description="Actionable recommendations or next steps")
    processing_time_ms: float = Field(..., description="Time taken to execute the agent prompt cycle")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="LLM settings, prompt version, or audit metadata")
