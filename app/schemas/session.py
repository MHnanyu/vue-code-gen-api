from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from app.schemas.message import CodeFile
from app.schemas.generate import Attachment


ComponentLib = Literal['ElementUI', 'aui', 'ccui']


class StepMessage(BaseModel):
    stage: int = Field(description="步骤编号（0=附件处理, 1=需求标准化, 2=代码生成, 3=UX优化）")
    stageName: str = Field(description="步骤名称")
    message: str = Field(description="该步骤的摘要/说明")
    outputPreview: Optional[str] = Field(default=None, description="产出预览（截断）")
    duration: Optional[float] = Field(default=None, description="执行耗时（秒）")


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    role: str
    content: str
    attachments: Optional[List[Attachment]] = None
    failedStep: Optional[int] = Field(default=None, description="失败的步骤编号，前端可直接作为 fromStep 重试")
    stages: Optional[dict] = Field(default=None, description="各步骤执行状态")
    stageOutputs: Optional[List[dict]] = Field(default=None, description="各步骤产出文件路径元数据")
    stepMessages: Optional[List[StepMessage]] = Field(default=None, description="各步骤的摘要信息，前端可逐步展示")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionCreate(BaseModel):
    title: Optional[str] = None
    componentLib: Optional[ComponentLib] = None


class SessionUpdate(BaseModel):
    title: str


class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    userId: Optional[str] = None
    title: Optional[str] = None
    componentLib: Optional[ComponentLib] = None
    messages: List[Message] = []
    files: Optional[List[CodeFile]] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


class SessionListItem(BaseModel):
    id: str
    userId: Optional[str] = None
    title: Optional[str] = None
    componentLib: Optional[ComponentLib] = None
    createdAt: datetime
    updatedAt: datetime


class SessionListResponse(BaseModel):
    total: int
    list: List[SessionListItem]


class SessionFilesUpdate(BaseModel):
    files: List[CodeFile]
