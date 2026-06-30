from typing import Optional
from datetime import datetime
from ninja import Schema


class CommentCreate(Schema):
    content: str


class CommentUpdate(Schema):
    content: Optional[str] = None


class CommentOut(Schema):
    id: int
    content: str
    author_id: int
    author_name: str = ""
    article_id: int
    created_at: datetime
    updated_at: datetime


class ErrorOut(Schema):
    message: str
