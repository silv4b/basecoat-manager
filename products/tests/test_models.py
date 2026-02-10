from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from products.models import Category, Product, PriceHistory, Profile
from products.tests.factories import (
    UserFactory,
    CategoryFactory,
    ProductFactory,
    PriceHistoryFactory,
)


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        """Test creating a category with all fields"""
        category = CategoryFactory.create(
            name="My Electronics",
            slug="my-electronics",
            description="Electronic products",
            color="#ff0000",
        )

        self.assertEqual(category.name, "My Electronics")
        self.assertEqual(category.slug, "my-electronics")
        self.assertEqual(category.description, "Electronic products")
        self.assertEqual(category.color, "#ff0000")
        self.assertEqual(str(category), "My Electronics")

    def test_category_verbose_name_plural(self):
        """Test verbose name plural is correctly set"""
        self.assertEqual(Category._meta.verbose_name_plural, "Categories")

    def test_category_unique_slug_per_user(self):
        """Test that slug must be unique per user"""
        user = UserFactory.create()
        CategoryFactory.create(user=user, slug="test-slug")
        with self.assertRaises(Exception):  # IntegrityError for unique constraint
            CategoryFactory.create(user=user, slug="test-slug")

    def test_category_duplicate_slug_different_users(self):
        """Test that different users can have same slug"""
        user1 = UserFactory.create()
        user2 = UserFactory.create()

        c1 = CategoryFactory.create(user=user1, slug="t-slug")
        c2 = CategoryFactory.create(user=user2, slug="t-slug")

        self.assertEqual(c1.slug, c2.slug)
        self.assertNotEqual(c1.pk, c2.pk)

    def test_default_categories_creation(self):
        """Test that default categories are created for new user"""
        user = UserFactory.create()
        # Default categories: "Eletrônicos", "Importados", "Nacionais", "Utensilios"
        self.assertEqual(Category.objects.filter(user=user).count(), 4)
        slugs = list(Category.objects.filter(user=user).values_list("slug", flat=True))
        self.assertIn("eletronicos", slugs)
        self.assertIn("importados", slugs)


class ProductModelTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.category = CategoryFactory.create(user=self.user)

    def test_product_creation(self):
        """Test creating a product with all fields"""
        product = ProductFactory.create(
            user=self.user,
            name="Laptop",
            description="High performance laptop",
            price=Decimal("999.99"),
            stock=5,
            is_public=True,
        )
        product.categories.add(self.category)

        self.assertEqual(product.user, self.user)
        self.assertEqual(product.name, "Laptop")
        self.assertEqual(product.description, "High performance laptop")
        self.assertEqual(product.price, Decimal("999.99"))
        self.assertEqual(product.stock, 5)
        self.assertTrue(product.is_public)
        self.assertIn(self.category, product.categories.all())
        self.assertEqual(str(product), "Laptop")

    def test_product_default_values(self):
        """Test product default values"""
        product = ProductFactory.create()

        self.assertEqual(product.stock, 0)
        self.assertFalse(product.is_public)

    def test_product_user_relationship(self):
        """Test product-user relationship"""
        product = ProductFactory.create(user=self.user)

        self.assertEqual(product.user, self.user)
        self.assertIn(product, self.user.products.all())# type: ignore

    def test_product_category_relationship(self):
        """Test many-to-many relationship with categories"""
        category1 = CategoryFactory.create(name="Category 1")
        category2 = CategoryFactory.create(name="Category 2")

        product = ProductFactory.create()
        product.categories.add(category1, category2)

        self.assertIn(product, category1.products.all())# type: ignore
        self.assertIn(product, category2.products.all())# type: ignore
        self.assertEqual(product.categories.count(), 2)

    def test_product_public_filtering(self):
        """Test filtering products by public status"""
        public_product = ProductFactory.create(is_public=True)
        private_product = ProductFactory.create(is_public=False)

        public_products = Product.objects.filter(is_public=True)
        private_products = Product.objects.filter(is_public=False)

        self.assertIn(public_product, public_products)
        self.assertNotIn(private_product, public_products)
        self.assertIn(private_product, private_products)
        self.assertNotIn(public_product, private_products)


class PriceHistoryModelTest(TestCase):
    def setUp(self):
        self.product = ProductFactory.create(price=Decimal("100.00"))

    def test_price_history_creation(self):
        """Test creating price history entry"""
        history = PriceHistoryFactory.create(
            product=self.product, price=Decimal("150.00")
        )

        self.assertEqual(history.product, self.product)
        self.assertEqual(history.price, Decimal("150.00"))
        self.assertIsNotNone(history.changed_at)

    def test_price_history_string_representation(self):
        """Test string representation of price history"""
        history = PriceHistoryFactory.create(
            product=self.product, price=Decimal("99.99")
        )

        expected = f"{self.product.name} - R$ 99.99 em {history.changed_at.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(history), expected)

    def test_price_history_ordering(self):
        """Test that price history is ordered by changed_at descending"""
        import time

        # The product already has one price history entry from creation
        # Create additional history entries with slight delay
        time.sleep(0.01)
        middle_history = PriceHistoryFactory.create(
            product=self.product, price=Decimal("50.00")
        )
        time.sleep(0.01)
        new_history = PriceHistoryFactory.create(
            product=self.product, price=Decimal("75.00")
        )

        histories = PriceHistory.objects.all()
        # Should be ordered by changed_at descending (newest first)
        self.assertEqual(histories.first(), new_history)
        # The oldest (original from product creation) should be last
        original_history = histories.last()
        self.assertEqual(
            original_history.price, Decimal("100.00")# type: ignore
        )  # Original product price

    def test_price_history_verbose_name_plural(self):
        """Test verbose name plural"""
        self.assertEqual(PriceHistory._meta.verbose_name_plural, "Price Histories")

    def test_price_history_product_relationship(self):
        """Test price history-product relationship"""
        history = PriceHistoryFactory.create(product=self.product)

        self.assertEqual(history.product, self.product)
        self.assertIn(history, self.product.price_history.all())


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create()

    def test_profile_creation(self):
        """Test profile creation via signal"""
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertEqual(self.user.profile.user, self.user)# type: ignore
        self.assertEqual(self.user.profile.theme, "light")# type: ignore

    def test_profile_string_representation(self):
        """Test string representation"""
        self.user.username = "testuser"
        self.user.save()

        expected = f"{self.user.username}'s profile"
        self.assertEqual(str(self.user.profile), expected)  # type: ignore

    def test_profile_theme_choices(self):
        """Test theme choices"""
        self.assertEqual(
            Profile.THEME_CHOICES,
            [
                ("light", "Light"),
                ("dark", "Dark"),
            ],
        )

    def test_profile_default_theme(self):
        """Test default theme is light"""
        self.assertEqual(self.user.profile.theme, "light")  # type: ignore

    def test_profile_theme_update(self):
        """Test updating profile theme"""
        self.user.profile.theme = "dark"  # type: ignore
        self.user.profile.save()  # type: ignore

        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.theme, "dark")  # type: ignore


class SignalTests(TestCase):
    def test_profile_creation_signal(self):
        """Test that profile is created when user is created"""
        user = UserFactory.create()

        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, Profile)  # type: ignore

    def test_price_history_signal_on_product_creation(self):
        """Test that price history is created when product is created"""
        product = ProductFactory.create(price=Decimal("199.99"))

        self.assertEqual(product.price_history.count(), 1)
        history = product.price_history.first()
        self.assertEqual(history.price, Decimal("199.99"))  # type: ignore

    def test_price_history_signal_on_price_change(self):
        """Test that price history is created when price changes"""
        product = ProductFactory.create(price=Decimal("100.00"))

        # Change price
        product.price = Decimal("150.00")
        product.save()

        self.assertEqual(product.price_history.count(), 2)
        prices = [h.price for h in product.price_history.order_by("changed_at")]
        self.assertEqual(prices, [Decimal("100.00"), Decimal("150.00")])

    def test_price_history_signal_no_duplicate_on_same_price(self):
        """Test that no duplicate history is created for same price"""
        product = ProductFactory.create(price=Decimal("100.00"))

        # Save without changing price
        product.name = "Updated name"
        product.save()

        self.assertEqual(product.price_history.count(), 1)  # Only initial entry
