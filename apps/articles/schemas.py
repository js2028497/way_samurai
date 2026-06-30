from typing import Optional
from datetime import datetime
from ninja import Schema


class ArticleCreate(Schema):
    title: str
    content: str
    category_id: Optional[int] = None


class ArticleUpdate(Schema):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None


class ArticleOut(Schema):
    id: int
    title: str
    content: str
    author_id: int
    author_name: str = ""
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ArticleListOut(Schema):
    id: int
    title: str
    content_preview: str = ""
    author_id: int
    author_name: str = ""
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ErrorOut(Schema):
    message: str
