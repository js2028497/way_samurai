import logging
from datetime import datetime, timedelta
from ninja import Router
from ninja.security import HttpBearer
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings
import jwt
from apps.users.models import Token
from apps.users.schemas import (
    RegisterInput, LoginInput, TokenOut, UserOut, ErrorOut, MessageOut,
    JwtTokenOut, JwtRefreshInput,
)

logger = logging.getLogger("blog")
router = Router()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            token_obj = Token.objects.select_related("user").get(key=token)
            return token_obj.user
        except Token.DoesNotExist:
            return None


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            user = User.objects.get(id=payload["user_id"])
            return user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return None


auth_bearer = AuthBearer()
jwt_auth = JWTAuth()


@router.post("/register/", response={201: TokenOut, 400: ErrorOut})
def register(request, payload: RegisterInput):
    if User.objects.filter(username=payload.username).exists():
        logger.warning(f"Registration failed: username '{payload.username}' already exists")
        return 400, ErrorOut(message="Username already exists")
    user = User.objects.create_user(
        username=payload.username, password=payload.password
    )
    token = Token.objects.create(user=user, key=Token.generate_key())
    logger.info(f"User registered: '{user.username}' (id={user.id})")
    return 201, TokenOut(token=token.key, user_id=user.id, username=user.username)


@router.post("/login/", response={200: TokenOut, 401: ErrorOut})
def login(request, payload: LoginInput):
    user = authenticate(username=payload.username, password=payload.password)
    if user is None:
        logger.warning(f"Failed login attempt for username: '{payload.username}'")
        return 401, ErrorOut(message="Invalid credentials")
    token, created = Token.objects.get_or_create(
        user=user, defaults={"key": Token.generate_key()}
    )
    if not created:
        token.key = Token.generate_key()
        token.save()
    logger.info(f"User '{user.username}' logged in")
    return 200, TokenOut(token=token.key, user_id=user.id, username=user.username)


@router.post("/logout/", response={200: MessageOut, 401: ErrorOut}, auth=auth_bearer)
def logout(request):
    user = request.auth
    Token.objects.filter(user=user).delete()
    logger.info(f"User '{user.username}' logged out")
    return 200, MessageOut(message="Logged out successfully")


@router.get("/me/", response=UserOut, auth=auth_bearer)
def get_me(request):
    user = request.auth
    return UserOut(id=user.id, username=user.username)


@router.post("/token/", response={200: JwtTokenOut, 401: ErrorOut})
def obtain_jwt_token(request, payload: LoginInput):
    user = authenticate(username=payload.username, password=payload.password)
    if user is None:
        return 401, ErrorOut(message="Invalid credentials")
    access_token = jwt.encode(
        {
            "user_id": user.id,
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
            "type": "access",
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    refresh_token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow(),
            "type": "refresh",
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return 200, JwtTokenOut(
        access=access_token, refresh=refresh_token, username=user.username
    )


@router.post("/token/refresh/", response={200: JwtTokenOut, 401: ErrorOut})
def refresh_jwt_token(request, payload: JwtRefreshInput):
    try:
        payload_data = jwt.decode(
            payload.refresh, settings.SECRET_KEY, algorithms=["HS256"]
        )
        if payload_data.get("type") != "refresh":
            return 401, ErrorOut(message="Invalid token type")
        user = User.objects.get(id=payload_data["user_id"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return 401, ErrorOut(message="Invalid or expired refresh token")
    access_token = jwt.encode(
        {
            "user_id": user.id,
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
            "type": "access",
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    refresh_token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow(),
            "type": "refresh",
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return 200, JwtTokenOut(
        access=access_token, refresh=refresh_token, username=user.username
    )
