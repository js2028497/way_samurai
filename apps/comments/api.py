from typing import List
import logging
from ninja import Router
from django.shortcuts import get_object_or_404
from apps.comments.models import Comment
from apps.articles.models import Article
from apps.comments.schemas import (
    CommentCreate, CommentUpdate, CommentOut, ErrorOut,
)
from apps.users.api import auth_bearer

logger = logging.getLogger("blog")
router = Router()


@router.get("/", response=List[CommentOut])
def list_comments(request):
    comments = Comment.objects.select_related("author", "article").all()
    result = []
    for c in comments:
        result.append(CommentOut(
            id=c.id,
            content=c.content,
            author_id=c.author_id,
            author_name=c.author.username,
            article_id=c.article_id,
            created_at=c.created_at,
            updated_at=c.updated_at,
        ))
    return result


@router.get("/{comment_id}/", response={200: CommentOut, 404: ErrorOut})
def get_comment(request, comment_id: int):
    comment = get_object_or_404(
        Comment.objects.select_related("author", "article"), id=comment_id
    )
    return 200, CommentOut(
        id=comment.id,
        content=comment.content,
        author_id=comment.author_id,
        author_name=comment.author.username,
        article_id=comment.article_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.get("/by-article/{article_id}/", response=List[CommentOut])
def list_comments_by_article(request, article_id: int):
    comments = Comment.objects.select_related("author").filter(article_id=article_id)
    result = []
    for c in comments:
        result.append(CommentOut(
            id=c.id,
            content=c.content,
            author_id=c.author_id,
            author_name=c.author.username,
            article_id=c.article_id,
            created_at=c.created_at,
            updated_at=c.updated_at,
        ))
    return result


@router.post(
    "/by-article/{article_id}/",
    response={201: CommentOut, 400: ErrorOut, 404: ErrorOut},
    auth=auth_bearer,
)
def create_comment(request, article_id: int, payload: CommentCreate):
    user = request.auth
    article = get_object_or_404(Article, id=article_id)
    if not payload.content:
        return 400, ErrorOut(message="Content is required")
    comment = Comment.objects.create(
        content=payload.content, author=user, article=article
    )
    return 201, CommentOut(
        id=comment.id,
        content=comment.content,
        author_id=comment.author_id,
        author_name=user.username,
        article_id=article.id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.put(
    "/{comment_id}/",
    response={200: CommentOut, 403: ErrorOut, 404: ErrorOut},
    auth=auth_bearer,
)
def update_comment(request, comment_id: int, payload: CommentUpdate):
    user = request.auth
    comment = get_object_or_404(
        Comment.objects.select_related("author", "article"), id=comment_id
    )
    if comment.author != user:
        return 403, ErrorOut(message="You can only edit your own comments")
    if payload.content is not None:
        comment.content = payload.content
    comment.save()
    return 200, CommentOut(
        id=comment.id,
        content=comment.content,
        author_id=comment.author_id,
        author_name=comment.author.username,
        article_id=comment.article_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.delete(
    "/{comment_id}/",
    response={204: None, 403: ErrorOut, 404: ErrorOut},
    auth=auth_bearer,
)
def delete_comment(request, comment_id: int):
    user = request.auth
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != user:
        return 403, ErrorOut(message="You can only delete your own comments")
    comment.delete()
    return 204, None
