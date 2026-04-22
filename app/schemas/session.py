from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from app.schemas.message import CodeFile
from app.schemas.generate import Attachment


ComponentLib = Literal['ElementUI', 'aui', 'ccui']
SessionMode = Literal['pipeline', 'agent']


class StepMessage(BaseModel):
    stage: int = Field(description="步骤编号（0=附件处理, 1=需求标准化, 2=代码生成, 3=UX优化）")
    stageName: str = Field(description="步骤名称")
    message: Optional[str] = Field(default=None, description="该步骤的摘要/说明")
    status: Optional[str] = Field(default=None, description="执行状态（success/failed/skipped/cached）")
    outputPaths: Optional[List[str]] = Field(default=None, description="产出文件相对路径列表")
    renderType: Optional[str] = Field(default=None, description="前端渲染方式（text=直接展示/code=代码预览）")
    duration: Optional[float] = Field(default=None, description="执行耗时（秒）")


class ToolCallMessage(BaseModel):
    toolName: str = Field(description="工具名称")
    arguments: Optional[str] = Field(default=None, description="调用参数（JSON字符串）")
    status: Optional[str] = Field(default=None, description="执行状态（success/failed）")
    result: Optional[dict] = Field(default=None, description="执行结果")
    message: Optional[str] = Field(default=None, description="用户展示的摘要说明")
    outputPaths: Optional[List[str]] = Field(default=None, description="产出文件相对路径列表")
    renderType: Optional[str] = Field(default=None, description="前端渲染方式（text=直接展示/code=代码预览）")
    duration: Optional[float] = Field(default=None, description="执行耗时（秒）")
    timestamp: Optional[str] = Field(default=None, description="调用时间")


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    role: str
    content: str
    attachments: Optional[List[Attachment]] = None
    failedStep: Optional[int] = Field(default=None, description="失败的步骤编号，前端可直接作为 fromStep 重试")
    stages: Optional[dict] = Field(default=None, description="各步骤执行状态")
    stepMessages: Optional[List[StepMessage]] = Field(default=None, description="各步骤的摘要信息，前端可逐步展示")
    toolCalls: Optional[List[ToolCallMessage]] = Field(default=None, description="所有工具调用的完整记录")
    files: Optional[List[dict]] = Field(default=None, description="该消息关联的文件快照，用于重试时回滚")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionCreate(BaseModel):
    title: Optional[str] = None
    componentLib: Optional[ComponentLib] = None
    mode: SessionMode


class SessionUpdate(BaseModel):
    title: str


class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    userId: Optional[str] = None
    title: Optional[str] = None
    componentLib: Optional[ComponentLib] = None
    mode: SessionMode
    messages: List[Message] = []
    files: Optional[List[CodeFile]] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


class SessionListItem(BaseModel):
    id: str
    userId: Optional[str] = None
    title: Optional[str] = None
    componentLib: Optional[ComponentLib] = None
    mode: SessionMode
    createdAt: datetime
    updatedAt: datetime


class SessionListResponse(BaseModel):
    total: int
    list: List[SessionListItem]


class SessionFilesUpdate(BaseModel):
    files: List[CodeFile]
