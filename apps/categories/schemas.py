from typing import Optional
from datetime import datetime
from ninja import Schema


class CategoryCreate(Schema):
    name: str
    description: Optional[str] = ""


class CategoryUpdate(Schema):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryOut(Schema):
    id: int
    name: str
    description: str
    created_at: datetime


class ErrorOut(Schema):
    message: str
