from ninja import Schema


class RegisterInput(Schema):
    username: str
    password: str


class LoginInput(Schema):
    username: str
    password: str


class TokenOut(Schema):
    token: str
    user_id: int
    username: str


class UserOut(Schema):
    id: int
    username: str


class ErrorOut(Schema):
    message: str


class MessageOut(Schema):
    message: str


class JwtTokenOut(Schema):
    access: str
    refresh: str
    username: str


class JwtRefreshInput(Schema):
    refresh: str
