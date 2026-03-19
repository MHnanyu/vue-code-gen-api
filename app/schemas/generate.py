from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class Attachment(BaseModel):
    id: str
    url: str
    name: str
    type: Literal["image", "text", "markdown"]
    size: Optional[int] = None


class UploadResponseData(BaseModel):
    files: List[Attachment]


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
    attachments: Optional[List[Attachment]] = None
    fromStep: Optional[int] = Field(
        default=None,
        description="从指定步骤开始重试，跳过之前已成功的步骤（0=附件处理, 1=需求标准化, 2=代码生成, 3=UX优化）"
    )


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
    failedStep: Optional[int] = Field(
        default=None,
        description="失败的步骤编号，前端可直接作为 fromStep 重试（0=附件处理, 1=需求标准化, 2=代码生成, 3=UX优化），null 表示全部成功"
    )


class ImageAnalyzeRequest(BaseModel):
    imageUrl: Optional[str] = None
    imageBase64: Optional[str] = None
    prompt: Optional[str] = None


class ImageAnalyzeResponseData(BaseModel):
    description: str
    rawDescription: str
    success: bool
