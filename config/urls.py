from django.contrib import admin
from django.urls import path, include
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

api = NinjaExtraAPI(title="Blog API", version="1.0.0")
api.register_controllers(NinjaJWTDefaultController)

from apps.users.api import router as users_router
from apps.articles.api import router as articles_router
from apps.comments.api import router as comments_router
from apps.categories.api import router as categories_router

api.add_router("/users/", users_router, tags=["Users"])
api.add_router("/articles/", articles_router, tags=["Articles"])
api.add_router("/comments/", comments_router, tags=["Comments"])
api.add_router("/categories/", categories_router, tags=["Categories"])

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("", include("apps.pages.urls")),
]
