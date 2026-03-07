from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    role: str
    content: str


class Message(MessageBase):
    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionCreate(BaseModel):
    title: Optional[str] = None


class SessionUpdate(BaseModel):
    title: str


class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    userId: Optional[str] = None
    title: Optional[str] = None
    messages: List[Message] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


class SessionListItem(BaseModel):
    id: str
    userId: Optional[str] = None
    title: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime


class SessionListResponse(BaseModel):
    total: int
    list: List[SessionListItem]
