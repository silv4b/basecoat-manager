"""
Test utilities and helper functions for the products app.
"""

from django.test import TestCase
from products.tests.factories import (
    UserFactory,
)


class BaseTestCase(TestCase):
    """Base test case with common setup and utilities"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create()
        self.other_user = UserFactory.create(username="otheruser")
        self.client.login(username="testuser", password="testpass123")
        """Get form errors from response context"""
        if "form" in response.context:
            return response.context["form"].errors
        return {}

    def clear_session_key(self, key):
        """Limpa uma chave específica da sessão do Django"""
        session = self.client.session
        session[key] = {}
        session.save()
