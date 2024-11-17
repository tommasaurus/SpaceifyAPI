# app/schemas/chat.py

from pydantic import BaseModel

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
