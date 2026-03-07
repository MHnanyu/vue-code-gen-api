from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    code: int = 0
    data: Optional[T] = None
    message: str = "success"


class ErrorResponse(BaseModel):
    code: int
    data: None = None
    message: str


class ErrorCode:
    SUCCESS = 0
    PARAM_ERROR = 1001
    SESSION_NOT_FOUND = 1002
    AI_GENERATE_FAILED = 1003
    REQUEST_TIMEOUT = 1004
    UNAUTHORIZED = 2001
    TOKEN_EXPIRED = 2002
    INTERNAL_ERROR = 5000
