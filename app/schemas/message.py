from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class MessageCreate(BaseModel):
    role: str
    content: str


class CodeFile(BaseModel):
    id: str
    name: str
    path: str
    type: str
    language: Optional[str] = None
    content: Optional[str] = None
    children: Optional[List["CodeFile"]] = None


class MessageWithFiles(BaseModel):
    role: str
    content: str
    files: Optional[List[CodeFile]] = None
