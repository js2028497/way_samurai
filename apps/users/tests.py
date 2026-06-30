from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from apps.users.models import Token


class UsersAPITestCase(TestCase):
    def setUp(self):
        self.client = self.client_class()

    def get_url(self, path: str) -> str:
        return f"/api/users{path}"

    def _create_user(self):
        return User.objects.create_user(username="testuser", password="testpass123")

    def _get_token(self, user):
        token, _ = Token.objects.get_or_create(
            user=user, defaults={"key": Token.generate_key()}
        )
        return token.key


class RegisterTests(UsersAPITestCase):
    def test_register_success(self):
        response = self.client.post(
            self.get_url("/register/"),
            {"username": "newuser", "password": "newpass123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("token", data)
        self.assertEqual(data["username"], "newuser")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_duplicate_username(self):
        self._create_user()
        response = self.client.post(
            self.get_url("/register/"),
            {"username": "testuser", "password": "testpass123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json())


class LoginTests(UsersAPITestCase):
    def test_login_success(self):
        self._create_user()
        response = self.client.post(
            self.get_url("/login/"),
            {"username": "testuser", "password": "testpass123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertEqual(data["username"], "testuser")

    def test_login_invalid_credentials(self):
        self._create_user()
        response = self.client.post(
            self.get_url("/login/"),
            {"username": "testuser", "password": "wrongpass"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("message", response.json())


class LogoutTests(UsersAPITestCase):
    def test_logout_success(self):
        user = self._create_user()
        token = self._get_token(user)
        response = self.client.post(
            self.get_url("/logout/"),
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Token.objects.filter(user=user).exists())

    def test_logout_without_auth(self):
        response = self.client.post(self.get_url("/logout/"))
        self.assertEqual(response.status_code, 401)


class MeTests(UsersAPITestCase):
    def test_me_authenticated(self):
        user = self._create_user()
        token = self._get_token(user)
        response = self.client.get(
            self.get_url("/me/"),
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "testuser")

    def test_me_unauthenticated(self):
        response = self.client.get(self.get_url("/me/"))
        self.assertEqual(response.status_code, 401)


class JwtTokenTests(UsersAPITestCase):
    def test_jwt_token_obtain_success(self):
        self._create_user()
        response = self.client.post(
            self.get_url("/token/"),
            {"username": "testuser", "password": "testpass123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertEqual(data["username"], "testuser")

    def test_jwt_token_obtain_invalid(self):
        response = self.client.post(
            self.get_url("/token/"),
            {"username": "nobody", "password": "wrong"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_jwt_token_refresh_success(self):
        self._create_user()
        resp = self.client.post(
            self.get_url("/token/"),
            {"username": "testuser", "password": "testpass123"},
            content_type="application/json",
        )
        refresh_token = resp.json()["refresh"]
        response = self.client.post(
            self.get_url("/token/refresh/"),
            {"refresh": refresh_token},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_jwt_token_refresh_invalid(self):
        response = self.client.post(
            self.get_url("/token/refresh/"),
            {"refresh": "invalid.token.here"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
