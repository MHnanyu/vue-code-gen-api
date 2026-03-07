from typing import Optional, List
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    prompt: str
    componentLib: Optional[str] = "ElementUI"
    sessionId: Optional[str] = None


class GeneratedFile(BaseModel):
    id: str
    name: str
    path: str
    type: str
    language: Optional[str] = None
    content: Optional[str] = None
    children: Optional[List["GeneratedFile"]] = None


class GenerateResponseData(BaseModel):
    files: List[GeneratedFile]
    message: str
