from django.test import TestCase
from django.contrib.auth.models import User
from apps.categories.models import Category
from apps.users.models import Token


class CategoriesAPITestCase(TestCase):
    def setUp(self):
        self.client = self.client_class()
        self.admin_user = User.objects.create_user(
            username="admin", password="adminpass123", is_staff=True
        )
        self.admin_token, _ = Token.objects.get_or_create(
            user=self.admin_user, defaults={"key": Token.generate_key()}
        )
        self.regular_user = User.objects.create_user(
            username="regular", password="regularpass123"
        )
        self.regular_token, _ = Token.objects.get_or_create(
            user=self.regular_user, defaults={"key": Token.generate_key()}
        )
        self.category = Category.objects.create(
            name="Science", description="Science category"
        )

    def get_url(self, path: str) -> str:
        return f"/api/categories{path}"


class ListCategoriesTests(CategoriesAPITestCase):
    def test_list_categories_success(self):
        response = self.client.get(self.get_url("/"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        names = [c["name"] for c in data]
        self.assertIn("Science", names)

    def test_list_categories_empty(self):
        Category.objects.all().delete()
        response = self.client.get(self.get_url("/"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


class GetCategoryTests(CategoriesAPITestCase):
    def test_get_category_success(self):
        response = self.client.get(self.get_url(f"/{self.category.id}/"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Science")

    def test_get_category_not_found(self):
        response = self.client.get(self.get_url("/99999/"))
        self.assertEqual(response.status_code, 404)


class CreateCategoryTests(CategoriesAPITestCase):
    def test_create_category_as_admin(self):
        response = self.client.post(
            self.get_url("/"),
            {"name": "Technology", "description": "Tech category"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token.key}",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "Technology")

    def test_create_category_as_regular_user(self):
        response = self.client.post(
            self.get_url("/"),
            {"name": "Hacked Category"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.regular_token.key}",
        )
        self.assertEqual(response.status_code, 401)

    def test_create_category_duplicate(self):
        response = self.client.post(
            self.get_url("/"),
            {"name": "Science"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token.key}",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_category_without_auth(self):
        response = self.client.post(
            self.get_url("/"),
            {"name": "Unauthorized"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)


class UpdateCategoryTests(CategoriesAPITestCase):
    def test_update_category_as_admin(self):
        response = self.client.put(
            self.get_url(f"/{self.category.id}/"),
            {"name": "Natural Sciences"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token.key}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Natural Sciences")

    def test_update_category_as_regular_user(self):
        response = self.client.put(
            self.get_url(f"/{self.category.id}/"),
            {"name": "Hacked"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.regular_token.key}",
        )
        self.assertEqual(response.status_code, 401)

    def test_update_category_not_found(self):
        response = self.client.put(
            self.get_url("/99999/"),
            {"name": "Ghost"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token.key}",
        )
        self.assertEqual(response.status_code, 404)


class DeleteCategoryTests(CategoriesAPITestCase):
    def test_delete_category_as_admin(self):
        response = self.client.delete(
            self.get_url(f"/{self.category.id}/"),
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token.key}",
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_delete_category_as_regular_user(self):
        response = self.client.delete(
            self.get_url(f"/{self.category.id}/"),
            HTTP_AUTHORIZATION=f"Bearer {self.regular_token.key}",
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_category_not_found(self):
        response = self.client.delete(
            self.get_url("/99999/"),
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token.key}",
        )
        self.assertEqual(response.status_code, 404)
