from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from apps.articles.models import Article
from apps.comments.models import Comment
from apps.categories.models import Category
from apps.users.models import Token
import secrets
import logging

logger = logging.getLogger("blog")


def index(request):
    articles = Article.objects.select_related("author", "category").all()
    categories = Category.objects.all()
    return render(request, "index.html", {
        "articles": articles,
        "categories": categories,
    })


def article_detail(request, article_id):
    article = get_object_or_404(
        Article.objects.select_related("author", "category"), id=article_id
    )
    comments = Comment.objects.select_related("author").filter(article=article)
    return render(request, "article_detail.html", {
        "article": article,
        "comments": comments,
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"User '{username}' logged in via web UI")
            return redirect("index")
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})
        user = User.objects.create_user(username=username, password=password)
        Token.objects.create(user=user, key=Token.generate_key())
        login(request, user)
        logger.info(f"User '{username}' registered via web UI")
        return redirect("index")
    return render(request, "register.html")


def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def create_article(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        category_id = request.POST.get("category_id")
        if not title:
            categories = Category.objects.all()
            return render(request, "create_article.html", {
                "categories": categories,
                "error": "Title is required",
            })
        article = Article.objects.create(
            title=title,
            content=content,
            author=request.user,
            category_id=category_id or None,
        )
        logger.info(f"Article created via web UI: '{title}' by '{request.user.username}'")
        return redirect("article_detail", article_id=article.id)
    categories = Category.objects.all()
    return render(request, "create_article.html", {"categories": categories})


@login_required
def edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if article.author != request.user:
        return redirect("article_detail", article_id=article.id)
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        category_id = request.POST.get("category_id")
        if title:
            article.title = title
        if content:
            article.content = content
        if category_id:
            article.category_id = category_id
        article.save()
        logger.info(f"Article updated via web UI: '{article.title}' by '{request.user.username}'")
        return redirect("article_detail", article_id=article.id)
    categories = Category.objects.all()
    return render(request, "create_article.html", {
        "article": article,
        "categories": categories,
        "is_edit": True,
    })


@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if article.author == request.user:
        article.delete()
        logger.warning(f"Article deleted via web UI: '{article.title}' by '{request.user.username}'")
    return redirect("index")


@login_required
def create_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Comment.objects.create(content=content, author=request.user, article=article)
            logger.info(f"Comment created via web UI by '{request.user.username}'")
    return redirect("article_detail", article_id=article.id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    article_id = comment.article_id
    if comment.author == request.user:
        comment.delete()
        logger.warning(f"Comment deleted via web UI by '{request.user.username}'")
    return redirect("article_detail", article_id=article_id)
