from typing import List
import logging
from ninja import Router
from django.shortcuts import get_object_or_404
from apps.articles.models import Article
from apps.articles.schemas import (
    ArticleCreate, ArticleUpdate, ArticleOut, ArticleListOut, ErrorOut,
)
from apps.users.api import auth_bearer

logger = logging.getLogger("blog")
router = Router()


@router.get("/", response=List[ArticleListOut])
def list_articles(request):
    articles = Article.objects.select_related("author", "category").all()
    result = []
    for a in articles:
        result.append(ArticleListOut(
            id=a.id,
            title=a.title,
            content_preview=a.content[:200] if a.content else "",
            author_id=a.author_id,
            author_name=a.author.username,
            category_name=a.category.name if a.category else None,
            created_at=a.created_at,
            updated_at=a.updated_at,
        ))
    return result


@router.get("/{article_id}/", response={200: ArticleOut, 404: ErrorOut})
def get_article(request, article_id: int):
    article = get_object_or_404(
        Article.objects.select_related("author", "category"), id=article_id
    )
    return 200, ArticleOut(
        id=article.id,
        title=article.title,
        content=article.content,
        author_id=article.author_id,
        author_name=article.author.username,
        category_id=article.category_id,
        category_name=article.category.name if article.category else None,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


@router.post("/", response={201: ArticleOut, 400: ErrorOut, 401: ErrorOut}, auth=auth_bearer)
def create_article(request, payload: ArticleCreate):
    user = request.auth
    if not payload.title:
        return 400, ErrorOut(message="Title is required")
    article = Article.objects.create(
        title=payload.title,
        content=payload.content,
        author=user,
        category_id=payload.category_id,
    )
    return 201, ArticleOut(
        id=article.id,
        title=article.title,
        content=article.content,
        author_id=article.author_id,
        author_name=user.username,
        category_id=article.category_id,
        category_name=article.category.name if article.category else None,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


@router.put("/{article_id}/", response={200: ArticleOut, 403: ErrorOut, 404: ErrorOut}, auth=auth_bearer)
def update_article(request, article_id: int, payload: ArticleUpdate):
    user = request.auth
    article = get_object_or_404(Article, id=article_id)
    if article.author != user:
        return 403, ErrorOut(message="You can only edit your own articles")
    if payload.title is not None:
        article.title = payload.title
    if payload.content is not None:
        article.content = payload.content
    if payload.category_id is not None:
        article.category_id = payload.category_id
    article.save()
    article = Article.objects.select_related("author", "category").get(id=article_id)
    return 200, ArticleOut(
        id=article.id,
        title=article.title,
        content=article.content,
        author_id=article.author_id,
        author_name=article.author.username,
        category_id=article.category_id,
        category_name=article.category.name if article.category else None,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


@router.delete("/{article_id}/", response={204: None, 403: ErrorOut, 404: ErrorOut}, auth=auth_bearer)
def delete_article(request, article_id: int):
    user = request.auth
    article = get_object_or_404(Article, id=article_id)
    if article.author != user:
        return 403, ErrorOut(message="You can only delete your own articles")
    article.delete()
    return 204, None
