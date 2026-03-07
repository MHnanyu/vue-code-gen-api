from datetime import datetime
from pydantic import BaseModel


class MessageCreate(BaseModel):
    role: str
    content: str
