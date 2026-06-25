from typing import List, Optional
from pydantic import BaseModel

class ErrorDetail(BaseModel):
    loc: Optional[List[str]] = None
    msg: str
    type: str

class APIErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    details: Optional[List[ErrorDetail]] = None
