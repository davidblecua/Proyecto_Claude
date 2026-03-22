from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class MessageCreate(BaseModel):
    receiver_id: int
    machinery_id: int
    content: str = Field(..., min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_name: str
    receiver_id: int
    machinery_id: int
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    other_user_id: int
    other_user_name: str
    machinery_id: int
    machinery_title: str
    last_message: str
    last_message_at: datetime
    unread_count: int
