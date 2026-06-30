from django.test import TestCase
from django.contrib.auth.models import User
from apps.articles.models import Article
from apps.users.models import Token
from apps.categories.models import Category


class ArticlesAPITestCase(TestCase):
    def setUp(self):
        self.client = self.client_class()
        self.user = User.objects.create_user(
            username="author", password="authorpass123"
        )
        self.token, _ = Token.objects.get_or_create(
            user=self.user, defaults={"key": Token.generate_key()}
        )
        self.article = Article.objects.create(
            title="Test Article",
            content="This is test content for the article.",
            author=self.user,
        )
        self.other_user = User.objects.create_user(
            username="other", password="otherpass123"
        )
        self.other_token, _ = Token.objects.get_or_create(
            user=self.other_user, defaults={"key": Token.generate_key()}
        )
        self.category = Category.objects.create(name="Tech")

    def get_url(self, path: str) -> str:
        return f"/api/articles{path}"


class ListArticlesTests(ArticlesAPITestCase):
    def test_list_articles_success(self):
        response = self.client.get(self.get_url("/"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)
        titles = [a["title"] for a in data]
        self.assertIn("Test Article", titles)

    def test_list_articles_empty(self):
        Article.objects.all().delete()
        response = self.client.get(self.get_url("/"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


class GetArticleTests(ArticlesAPITestCase):
    def test_get_article_success(self):
        response = self.client.get(self.get_url(f"/{self.article.id}/"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Test Article")
        self.assertEqual(data["author_name"], "author")

    def test_get_article_not_found(self):
        response = self.client.get(self.get_url("/99999/"))
        self.assertEqual(response.status_code, 404)


class CreateArticleTests(ArticlesAPITestCase):
    def test_create_article_success(self):
        response = self.client.post(
            self.get_url("/"),
            {
                "title": "New Article",
                "content": "Brand new article content",
                "category_id": self.category.id,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "New Article")
        self.assertEqual(data["author_name"], "author")

    def test_create_article_without_auth(self):
        response = self.client.post(
            self.get_url("/"),
            {"title": "No Auth", "content": "Should fail"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_create_article_empty_title(self):
        response = self.client.post(
            self.get_url("/"),
            {"title": "", "content": "Content without title"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 400)


class UpdateArticleTests(ArticlesAPITestCase):
    def test_update_article_success(self):
        response = self.client.put(
            self.get_url(f"/{self.article.id}/"),
            {"title": "Updated Title"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Updated Title")

    def test_update_article_not_owner(self):
        response = self.client.put(
            self.get_url(f"/{self.article.id}/"),
            {"title": "Hacked Title"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.other_token.key}",
        )
        self.assertEqual(response.status_code, 403)

    def test_update_article_not_found(self):
        response = self.client.put(
            self.get_url("/99999/"),
            {"title": "Ghost"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 404)


class DeleteArticleTests(ArticlesAPITestCase):
    def test_delete_article_success(self):
        response = self.client.delete(
            self.get_url(f"/{self.article.id}/"),
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())

    def test_delete_article_not_owner(self):
        response = self.client.delete(
            self.get_url(f"/{self.article.id}/"),
            HTTP_AUTHORIZATION=f"Bearer {self.other_token.key}",
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_article_not_found(self):
        response = self.client.delete(
            self.get_url("/99999/"),
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 404)
