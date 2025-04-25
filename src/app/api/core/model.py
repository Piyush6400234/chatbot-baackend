from pydantic import BaseModel, validator
from typing import Optional

class ChatQuestion(BaseModel):
    query: str