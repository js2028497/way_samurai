from typing import List
import logging
from ninja import Router
from django.shortcuts import get_object_or_404
from apps.categories.models import Category
from apps.categories.schemas import (
    CategoryCreate, CategoryUpdate, CategoryOut, ErrorOut,
)
from apps.users.api import auth_bearer

logger = logging.getLogger("blog")
router = Router()


@router.get("/", response=List[CategoryOut])
def list_categories(request):
    categories = Category.objects.all()
    result = []
    for c in categories:
        result.append(CategoryOut(
            id=c.id, name=c.name, description=c.description, created_at=c.created_at
        ))
    return result


@router.get("/{category_id}/", response={200: CategoryOut, 404: ErrorOut})
def get_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    return 200, CategoryOut(
        id=category.id,
        name=category.name,
        description=category.description,
        created_at=category.created_at,
    )


@router.post("/", response={201: CategoryOut, 400: ErrorOut, 401: ErrorOut}, auth=auth_bearer)
def create_category(request, payload: CategoryCreate):
    user = request.auth
    if not user.is_staff:
        return 401, ErrorOut(message="Only admins can create categories")
    if Category.objects.filter(name=payload.name).exists():
        return 400, ErrorOut(message="Category with this name already exists")
    category = Category.objects.create(
        name=payload.name, description=payload.description or ""
    )
    return 201, CategoryOut(
        id=category.id,
        name=category.name,
        description=category.description,
        created_at=category.created_at,
    )


@router.put(
    "/{category_id}/", response={200: CategoryOut, 401: ErrorOut, 404: ErrorOut}, auth=auth_bearer
)
def update_category(request, category_id: int, payload: CategoryUpdate):
    user = request.auth
    if not user.is_staff:
        return 401, ErrorOut(message="Only admins can update categories")
    category = get_object_or_404(Category, id=category_id)
    if payload.name is not None:
        category.name = payload.name
    if payload.description is not None:
        category.description = payload.description
    category.save()
    return 200, CategoryOut(
        id=category.id,
        name=category.name,
        description=category.description,
        created_at=category.created_at,
    )


@router.delete(
    "/{category_id}/", response={204: None, 401: ErrorOut, 404: ErrorOut}, auth=auth_bearer
)
def delete_category(request, category_id: int):
    user = request.auth
    if not user.is_staff:
        return 401, ErrorOut(message="Only admins can delete categories")
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return 204, None
