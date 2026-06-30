from django.test import TestCase
from django.contrib.auth.models import User
from apps.articles.models import Article
from apps.comments.models import Comment
from apps.users.models import Token


class CommentsAPITestCase(TestCase):
    def setUp(self):
        self.client = self.client_class()
        self.user = User.objects.create_user(
            username="commenter", password="commentpass123"
        )
        self.token, _ = Token.objects.get_or_create(
            user=self.user, defaults={"key": Token.generate_key()}
        )
        self.other_user = User.objects.create_user(
            username="other", password="otherpass123"
        )
        self.other_token, _ = Token.objects.get_or_create(
            user=self.other_user, defaults={"key": Token.generate_key()}
        )
        self.article = Article.objects.create(
            title="Commentable Article",
            content="Some content",
            author=self.user,
        )
        self.comment = Comment.objects.create(
            content="Great article!",
            author=self.user,
            article=self.article,
        )

    def get_url(self, path: str) -> str:
        return f"/api/comments{path}"


class ListCommentsTests(CommentsAPITestCase):
    def test_list_all_comments(self):
        response = self.client.get(self.get_url("/"))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_list_comments_empty(self):
        Comment.objects.all().delete()
        response = self.client.get(self.get_url("/"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


class ListCommentsByArticleTests(CommentsAPITestCase):
    def test_list_by_article_success(self):
        response = self.client.get(
            self.get_url(f"/by-article/{self.article.id}/")
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]["author_name"], "commenter")

    def test_list_by_article_empty(self):
        Comment.objects.all().delete()
        response = self.client.get(
            self.get_url(f"/by-article/{self.article.id}/")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


class GetCommentTests(CommentsAPITestCase):
    def test_get_comment_success(self):
        response = self.client.get(self.get_url(f"/{self.comment.id}/"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "Great article!")

    def test_get_comment_not_found(self):
        response = self.client.get(self.get_url("/99999/"))
        self.assertEqual(response.status_code, 404)


class CreateCommentTests(CommentsAPITestCase):
    def test_create_comment_success(self):
        response = self.client.post(
            self.get_url(f"/by-article/{self.article.id}/"),
            {"content": "Nice post!"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["content"], "Nice post!")

    def test_create_comment_without_auth(self):
        response = self.client.post(
            self.get_url(f"/by-article/{self.article.id}/"),
            {"content": "Anonymous comment"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_create_comment_empty_content(self):
        response = self.client.post(
            self.get_url(f"/by-article/{self.article.id}/"),
            {"content": ""},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_comment_article_not_found(self):
        response = self.client.post(
            self.get_url("/by-article/99999/"),
            {"content": "Comment on ghost article"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 404)


class UpdateCommentTests(CommentsAPITestCase):
    def test_update_comment_success(self):
        response = self.client.put(
            self.get_url(f"/{self.comment.id}/"),
            {"content": "Updated comment"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "Updated comment")

    def test_update_comment_not_owner(self):
        response = self.client.put(
            self.get_url(f"/{self.comment.id}/"),
            {"content": "Malicious edit"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.other_token.key}",
        )
        self.assertEqual(response.status_code, 403)

    def test_update_comment_not_found(self):
        response = self.client.put(
            self.get_url("/99999/"),
            {"content": "Ghost comment"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 404)


class DeleteCommentTests(CommentsAPITestCase):
    def test_delete_comment_success(self):
        response = self.client.delete(
            self.get_url(f"/{self.comment.id}/"),
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_not_owner(self):
        response = self.client.delete(
            self.get_url(f"/{self.comment.id}/"),
            HTTP_AUTHORIZATION=f"Bearer {self.other_token.key}",
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_comment_not_found(self):
        response = self.client.delete(
            self.get_url("/99999/"),
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )
        self.assertEqual(response.status_code, 404)
