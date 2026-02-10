"""
Exemplo de como os testes ficariam mais simples com force_login
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from products.models import Product, Category
from products.tests.factories import UserFactory, CategoryFactory, ProductFactory


class SimpleProductTest(TestCase):
    """Exemplo de teste simplificado com force_login"""

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create_admin()
        self.client.force_login(self.user)  # ✅ Sem senha!

    def test_create_product_simple(self):
        """Teste simples de criação de produto"""
        # Dados válidos
        data = {
            "name": "Test Product",
            "price": "99.99",
            "stock": 10,
            "is_public": True,
        }

        # POST para criar
        response = self.client.post(reverse("product_create"), data)

        # Verificações
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name="Test Product").exists())

    def test_list_products_simple(self):
        """Teste simples de listagem de produtos"""
        # Criar produtos
        ProductFactory.create(user=self.user, name="Product 1")
        ProductFactory.create(user=self.user, name="Product 2")

        # GET para listar
        response = self.client.get(reverse("product_list"))

        # Verificações
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product 1")
        self.assertContains(response, "Product 2")


class UnauthenticatedProductTest(TestCase):
    """Teste sem autenticação - para verificar redirecionamentos"""

    def test_unauthenticated_redirected(self):
        """Verifica que usuário não autenticado é redirecionado"""
        response = self.client.get(reverse("product_list"))

        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
