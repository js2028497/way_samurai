from django.urls import path
from apps.pages import views

urlpatterns = [
    path("", views.index, name="index"),
    path("article/<int:article_id>/", views.article_detail, name="article_detail"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("create/", views.create_article, name="create_article"),
    path("edit/<int:article_id>/", views.edit_article, name="edit_article"),
    path("delete/<int:article_id>/", views.delete_article, name="delete_article"),
    path(
        "comment/<int:article_id>/",
        views.create_comment,
        name="create_comment",
    ),
    path(
        "comment/delete/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment",
    ),
]
