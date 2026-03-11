from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class GeneratedFile(BaseModel):
    id: str
    name: str
    path: str
    type: str
    language: Optional[str] = None
    content: Optional[str] = None
    children: Optional[List["GeneratedFile"]] = None


class GenerateInitialRequest(BaseModel):
    prompt: str
    sessionId: Optional[str] = None
    debug: bool = False
    componentLib: str = "ElementUI"


class GenerateIterateRequest(BaseModel):
    prompt: str
    sessionId: Optional[str] = None
    files: List[GeneratedFile]


class GenerateResponseData(BaseModel):
    files: List[GeneratedFile]
    message: str


class StageResult(BaseModel):
    status: str
    duration: Optional[float] = None
    output: Optional[str] = None
    error: Optional[str] = None


class GenerateInitialResponseData(BaseModel):
    files: List[GeneratedFile]
    message: str
    stages: Optional[Dict[str, StageResult]] = None
