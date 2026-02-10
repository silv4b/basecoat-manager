from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Product, Category
from products.tests.factories import UserFactory, CategoryFactory, ProductFactory
from products.tests.test_utils import BaseTestCase


class ProductWorkflowTest(BaseTestCase):
    """Test complete user workflows for product management"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create_admin()
        # Force login - não precisa de senha!
        self.client.force_login(self.user)

    def test_complete_product_lifecycle(self):
        """Test complete product lifecycle from creation to deletion"""
        category = CategoryFactory.create(name="Electronics")

        # 1. Create product
        create_data = {
            "name": "Test Laptop",
            "description": "High performance laptop",
            "price": "1299,99",  # Changed from "1.299,99" to "1299.99"
            "stock": 5,
            "is_public": True,
            "categories": [category.pk],
        }

        response = self.client.post(reverse("product_create"), data=create_data)
        self.assertEqual(response.status_code, 302)

        product = Product.objects.get(name="Test Laptop")
        self.assertEqual(product.user, self.user)
        self.assertEqual(product.price, Decimal("1299.99"))
        self.assertIn(category, product.categories.all())

        # Verify price history was created
        self.assertEqual(product.price_history.count(), 1)

        # 2. View product list
        response = self.client.get(reverse("product_list"))
        self.assertContains(response, "Test Laptop")

        # 3. View product details
        response = self.client.get(reverse("product_detail", kwargs={"pk": product.pk}))
        self.assertContains(response, "Test Laptop")
        self.assertContains(response, "High performance laptop")

        # 4. Update product
        update_data = {
            "name": "Updated Laptop",
            "description": "Updated description",
            "price": "999,99",
            "stock": 3,
            "is_public": False,
        }

        response = self.client.post(
            reverse("product_update", kwargs={"pk": product.pk}), data=update_data
        )
        self.assertEqual(response.status_code, 302)

        product.refresh_from_db()

        self.assertEqual(product.name, "Updated Laptop")
        self.assertEqual(product.price, Decimal("999.99"))
        self.assertFalse(product.is_public)

        # Verify price history was updated
        self.assertEqual(product.price_history.count(), 2)

        # 5. View price history
        response = self.client.get(reverse("price_history", kwargs={"pk": product.pk}))
        self.assertContains(response, "1.299,99")
        self.assertContains(response, "999,99")

        # 6. Delete product
        response = self.client.post(
            reverse("product_delete", kwargs={"pk": product.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())

    def test_product_filtering_workflow(self):
        """Test product filtering and sorting workflow with multiple criteria"""

        category_electronics = CategoryFactory.create(name="Electronics")
        category_books = CategoryFactory.create(name="Books")

        # Criamos os produtos e capturamos as instâncias retornadas
        laptop = ProductFactory.create(
            user=self.user,
            name="Laptop",
            price=Decimal("1000.00"),
            stock=5,
            is_public=True,
        )
        phone = ProductFactory.create(
            user=self.user,
            name="Phone",
            price=Decimal("500.00"),
            stock=10,
            is_public=False,
        )
        book = ProductFactory.create(
            user=self.user,
            name="Book",
            price=Decimal("20.00"),
            stock=50,
            is_public=True,
        )

        # Atribuindo categorias
        laptop.categories.add(category_electronics)
        phone.categories.add(category_electronics)
        book.categories.add(category_books)

        # 1. Teste de busca por texto (parâmetro 'q')
        response = self.client.get(reverse("product_list"), {"q": "Book"})
        self.assertEqual(response.status_code, 200)
        products = response.context["products"]
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0], book)

        self.clear_session_key("filters_dashboard")

        # 2. Teste de filtro por categoria
        response = self.client.get(
            reverse("product_list"), {"category": category_electronics.pk, "q": ""}
        )
        self.assertEqual(response.status_code, 200)
        products = response.context["products"]
        self.assertEqual(len(products), 2)

        # Verificando se os itens corretos estão presentes e o incorreto está ausente
        product_ids = [p.pk for p in products]
        self.assertIn(laptop.pk, product_ids)
        self.assertIn(phone.pk, product_ids)
        self.assertNotIn(book.pk, product_ids)

        self.clear_session_key("filters_dashboard")

        # 3. Teste de faixa de preço (min_price e max_price)
        response = self.client.get(
            reverse("product_list"), {"min_price": "200", "max_price": "800"}
        )
        products = response.context["products"]
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0], phone)

        self.clear_session_key("filters_dashboard")

        # 4. Teste de estoque mínimo (min_stock)
        response = self.client.get(reverse("product_list"), {"min_stock": "20"})
        products = response.context["products"]
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0], book)

        self.clear_session_key("filters_dashboard")

        # 5. Teste de ordenação por preço ascendente
        response = self.client.get(
            reverse("product_list"), {"sort": "price", "dir": "asc"}
        )
        self.assertEqual(response.status_code, 200)

        # Extraindo apenas os preços para validar a ordem numérica
        prices = [p.price for p in response.context["products"]]
        expected_prices = [Decimal("20.00"), Decimal("500.00"), Decimal("1000.00")]
        self.assertEqual(prices, expected_prices)

    def test_public_catalog_workflow(self):
        """Test public catalog viewing workflow"""
        other_user = UserFactory.create(username="seller")
        category = CategoryFactory.create(name="Gadgets")

        # Create products for other user
        public_product = ProductFactory.create(
            user=other_user,
            name="Public Gadget",
            price=Decimal("100.00"),
            is_public=True,
        )
        public_product.categories.add(category)

        private_product = ProductFactory.create(
            user=other_user,
            name="Private Gadget",
            price=Decimal("200.00"),
            is_public=False,
        )

        # Create own products
        own_product = ProductFactory.create(
            user=self.user, name="My Product", price=Decimal("150.00"), is_public=True
        )

        # Test public catalog view
        response = self.client.get(reverse("public_product_list"))
        self.assertContains(response, "Public Gadget")
        self.assertContains(response, "My Product")
        self.assertNotContains(response, "Private Gadget")

        # Test user-specific catalog
        response = self.client.get(
            reverse("user_public_catalog", kwargs={"username": "seller"})
        )
        self.assertContains(response, "Public Gadget")
        self.assertNotContains(response, "My Product")
        self.assertNotContains(response, "Private Gadget")

        # Test category filtering in public catalog
        response = self.client.get(
            reverse("user_public_catalog", kwargs={"username": "seller"}),
            {"category": category.pk},
        )
        self.assertContains(response, "Public Gadget")


class CategoryWorkflowTest(BaseTestCase):
    """Test complete user workflows for category management"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create_admin()
        self.client.force_login(self.user)

    def test_complete_category_lifecycle(self):
        """Test complete category lifecycle from creation to deletion"""
        # 1. Create category
        create_data = {
            "name": "New Category",
            "slug": "new-category",
            "description": "Category description",
            "color": "#ff5733",
        }

        response = self.client.post(reverse("category_create"), data=create_data)
        self.assertEqual(response.status_code, 302)

        category = Category.objects.get(name="New Category")
        self.assertEqual(category.slug, "new-category")
        self.assertEqual(category.description, "Category description")
        self.assertEqual(category.color, "#ff5733")

        # 2. View category list
        response = self.client.get(reverse("category_list"))
        self.assertContains(response, "New Category")

        # 3. Update category
        update_data = {
            "name": "Updated Category",
            "slug": "updated-category",
            "description": "Updated description",
            "color": "#33ff57",
        }

        response = self.client.post(
            reverse("category_update", kwargs={"pk": category.pk}), data=update_data
        )
        self.assertEqual(response.status_code, 302)

        category.refresh_from_db()
        self.assertEqual(category.name, "Updated Category")
        self.assertEqual(category.description, "Updated description")
        self.assertEqual(category.color, "#33ff57")

        # 4. Duplicate category
        response = self.client.get(
            reverse("category_duplicate", kwargs={"pk": category.pk})
        )
        self.assertContains(response, "Updated Category (Cópia)")
        self.assertContains(response, "updated-category-copia")

        # Complete the duplication
        response = self.client.post(
            reverse("category_duplicate", kwargs={"pk": category.pk}),
            {
                "name": "Updated Category (Cópia)",
                "slug": "updated-category-copy",
                "description": "Updated description",
                "color": "#33ff57",
            },
        )
        self.assertEqual(response.status_code, 302)

        duplicated_category = Category.objects.get(name="Updated Category (Cópia)")
        self.assertEqual(duplicated_category.slug, "updated-category-copy")

        # 5. Delete original category
        response = self.client.post(
            reverse("category_delete", kwargs={"pk": category.pk})
        )
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Category.objects.filter(pk=category.pk).exists())
        self.assertTrue(Category.objects.filter(pk=duplicated_category.pk).exists())


class UserAccountWorkflowTest(BaseTestCase):
    """Test user account management workflows"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create_admin()
        self.client.force_login(self.user)

    def test_complete_user_registration_and_profile_workflow(self):
        """Test user registration and profile management"""
        # User is already created via factory
        self.client.login(username=self.user.username, password="testpass123")

        # 1. View profile
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

        # 2. Update profile
        profile_data = {"username": "newusername", "email": "newemail@example.com"}

        response = self.client.post(reverse("profile"), data=profile_data)
        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newusername")
        self.assertEqual(self.user.email, "newemail@example.com")

        # 3. Test theme functionality
        response = self.client.get(reverse("toggle_theme"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("theme"), "dark")

        # 4. Test view mode functionality
        response = self.client.get(reverse("set_view_mode", kwargs={"mode": "grid"}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("view_mode"), "grid")


class PriceHistoryWorkflowTest(BaseTestCase):
    """Test price history tracking workflows"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create_admin()
        self.client.force_login(self.user)

    def test_price_history_tracking_workflow(self):
        """Test automatic price history tracking"""
        # Create product
        product = ProductFactory.create(user=self.user, price=Decimal("100.00"))

        # Verify initial price history
        self.assertEqual(product.price_history.count(), 1)
        initial_history = product.price_history.first()

        # Asserção de que initial_history não é None.
        assert initial_history is not None
        self.assertEqual(initial_history.price, Decimal("100.00"))

        # Update price multiple times
        prices = [
            Decimal("120.00"),
            Decimal("95.00"),
            Decimal("110.00"),
            Decimal("110.00"),
            Decimal("135.00"),
        ]

        for price in prices:
            product.price = price
            product.save()

        # Verifica o histórico de preços, deve haver 5 entradas, sem duplicadas para 110 2x seguidas.
        self.assertEqual(product.price_history.count(), 5)

        # Verifica a view de histórico de preços.
        response = self.client.get(reverse("price_history", kwargs={"pk": product.pk}))
        self.assertEqual(response.status_code, 200)

        # Verifica a página de histórico de preço (com todos os produtos)
        response = self.client.get(reverse("price_history_overview"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "135,00"
        )  # Ultimo valor atualizado do produto em questão.

        # Testa o filtro de data no histórico de preço
        from datetime import datetime, timedelta

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        response = self.client.get(
            reverse("price_history", kwargs={"pk": product.pk}),
            {
                "data_inicio": yesterday.strftime("%Y-%m-%d"),
                "data_fim": today.strftime("%Y-%m-%d"),
            },
        )

        self.assertEqual(response.status_code, 200)


class ErrorHandlingWorkflowTest(BaseTestCase):
    """Test error handling in various workflows"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create_admin()
        self.other_user = UserFactory.create(username="otheruser")
        self.client.force_login(self.user)

    def test_permission_denied_workflow(self):
        """Testa cenários onde o acesso deve ser negado ou protegido"""
        # Cria um produto que NÃO pertence ao usuário logado
        private_product = ProductFactory.create(
            user=self.other_user, name="Private Item", is_public=False
        )

        # 2. Tentar acessar detalhes de um produto privado de outro usuário
        response = self.client.get(
            reverse("product_detail", kwargs={"pk": private_product.pk})
        )

        self.assertEqual(response.status_code, 302)

        # 3. Tentar editar produto de outro usuário
        # Na view product_detail usa get_object_or_404(Product, pk=pk, user=request.user)
        # Como o usuário logado não é o dono, DEVE retornar 404
        response = self.client.get(
            reverse("product_update", kwargs={"pk": private_product.pk})
        )
        self.assertEqual(response.status_code, 404)

        # 4. Tentar deletar produto de outro usuário
        # Mesmo comportamento: 404 por causa do filtro de usuário na QuerySet
        response = self.client.post(
            reverse("product_delete", kwargs={"pk": private_product.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_form_validation_workflow(self):
        """Test form validation errors for products and categories"""

        # 1. Teste de criação de produto inválido
        # Dados que violam as regras do Model/Form
        response = self.client.post(
            reverse("product_create"),
            {
                "name": "",  # Erro: Campo obrigatório
                "price": "not_a_num",  # Erro: Formato inválido
                "stock": -5,  # Erro: Valor negativo (se houver validação)
            },
        )

        # A página recarrega mostrando os erros
        self.assertEqual(response.status_code, 200)

        # Verifica se o formulário no contexto realmente contém erros
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("price", form.errors)
        self.assertIn("stock", form.errors)

        # 2. Teste de criação de categoria inválida (Slug duplicado)
        category = CategoryFactory.create(slug="test-slug")

        response = self.client.post(
            reverse("category_create"),
            {
                "name": "Another Category",
                "slug": "test-slug",  # Erro: Já existe no banco
            },
        )

        # Aqui o status 200 já estava correto no seu código original
        self.assertEqual(response.status_code, 200)

        form_cat = response.context["form"]
        self.assertFalse(form_cat.is_valid())
        self.assertIn("slug", form_cat.errors)

    def test_not_found_workflow(self):
        """Test 404 scenarios"""
        # Non-existent product
        response = self.client.get(reverse("product_detail", kwargs={"pk": 99999}))
        self.assertEqual(response.status_code, 404)

        # Non-existent category
        response = self.client.get(reverse("category_update", kwargs={"pk": 99999}))
        self.assertEqual(response.status_code, 404)

        # Non-existent user catalog
        response = self.client.get(
            reverse("user_public_catalog", kwargs={"username": "nonexistentuser"})
        )
        self.assertEqual(response.status_code, 404)
