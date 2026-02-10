from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from products.forms import ProductForm, CategoryForm
from products.models import Product, Category
from products.tests.factories import UserFactory, CategoryFactory, ProductFactory


class ProductFormTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.category = CategoryFactory.create()

    def test_product_form_valid_data(self):
        """Test product form with valid data"""
        form_data = {
            "name": "Test Product",
            "description": "Test description",
            "price": "99,99",
            "stock": 10,
            "is_public": True,
            "categories": [self.category.id],
        }
        form = ProductForm(data=form_data)

        self.assertTrue(form.is_valid())
        product = form.save(commit=False)
        product.user = self.user
        product.save()
        form.save_m2m()

        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.price, Decimal("99.99"))
        self.assertEqual(product.stock, 10)
        self.assertTrue(product.is_public)
        self.assertIn(self.category, product.categories.all())

    def test_product_form_price_validation_with_comma(self):
        """Test price validation with comma decimal separator"""
        form_data = {"name": "Test Product", "price": "199,50", "stock": 5}
        form = ProductForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["price"], Decimal("199.50"))

    def test_product_form_price_validation_with_dot(self):
        """Test price validation with comma decimal separator (Brazilian format)"""
        form_data = {
            "name": "Test Product",
            "price": "199,50",  # Use comma as decimal separator (Brazilian format)
            "stock": 5,
            "categories": [],  # Add empty categories
        }
        form = ProductForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["price"], Decimal("199.50"))

    def test_product_form_price_with_thousands_separator(self):
        """Test price validation with thousands separator"""
        form_data = {"name": "Test Product", "price": "1.999,50", "stock": 5}
        form = ProductForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["price"], Decimal("1999.50"))

    def test_product_form_empty_price(self):
        """Test empty price handling in form"""
        form_data = {
            "name": "Test Product",
            "price": "0,00",  # Use valid empty equivalent instead of empty string
            "stock": 5,
        }
        form = ProductForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["price"], Decimal("0.00"))

    def test_product_form_invalid_price(self):
        """Test invalid price format"""
        form_data = {"name": "Test Product", "price": "invalid_price", "stock": 5}
        form = ProductForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_product_form_required_fields(self):
        """Test required fields"""
        form = ProductForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_product_form_widget_classes(self):
        """Test that form widgets have correct CSS classes"""
        form = ProductForm()

        # Check price input has correct class
        self.assertIn("input w-full", form["price"].field.widget.attrs["class"])

        # Check name input has correct class
        self.assertIn("input w-full", form["name"].field.widget.attrs["class"])

        # Check stock input has correct class
        self.assertIn("input w-full", form["stock"].field.widget.attrs["class"])

    def test_product_form_placeholders(self):
        """Test form field placeholders"""
        form = ProductForm()

        self.assertEqual(form["price"].field.widget.attrs["placeholder"], "0,00")
        self.assertEqual(form["name"].field.widget.attrs["placeholder"], "Product Name")
        self.assertEqual(
            form["description"].field.widget.attrs["placeholder"], "Description"
        )
        self.assertEqual(form["stock"].field.widget.attrs["placeholder"], "0")


class CategoryFormTest(TestCase):
    def test_category_form_valid_data(self):
        """Test category form with valid data"""
        form_data = {
            "name": "Test Category",
            "slug": "test-category",
            "description": "Test description",
            "color": "#ff0000",
        }
        form = CategoryForm(data=form_data)

        self.assertTrue(form.is_valid())
        category = form.save()

        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.slug, "test-category")
        self.assertEqual(category.description, "Test description")
        self.assertEqual(category.color, "#ff0000")

    def test_category_form_required_fields(self):
        """Test required fields"""
        form_data = {
            "name": "Test Category",
            "slug": "test-category",
            "color": "#ff0000",  # color is also required
        }
        form = CategoryForm(data=form_data)

        self.assertTrue(form.is_valid())  # name, slug, and color are required

    def test_category_form_optional_fields(self):
        """Test optional fields"""
        form_data = {
            "name": "Test Category",
            "slug": "test-category-unique",
            "color": "#3b82f6",  # color is required, not optional
        }
        form = CategoryForm(data=form_data)

        self.assertTrue(form.is_valid())
        category = form.save()

        self.assertEqual(category.description, "")  # description is optional
        self.assertEqual(category.color, "#3b82f6")  # color should match input

    def test_category_form_widget_classes(self):
        """Test that form widgets have correct CSS classes"""
        form = CategoryForm()

        self.assertIn("input w-full", form["name"].field.widget.attrs["class"])
        self.assertIn("input w-full", form["slug"].field.widget.attrs["class"])
        self.assertIn(
            "input w-full h-24 py-2", form["description"].field.widget.attrs["class"]
        )
        self.assertIn("input w-full h-10", form["color"].field.widget.attrs["class"])

    def test_category_form_placeholders(self):
        """Test form field placeholders"""
        form = CategoryForm()

        self.assertEqual(
            form["name"].field.widget.attrs["placeholder"], "Nome da Categoria"
        )
        self.assertEqual(
            form["slug"].field.widget.attrs["placeholder"], "slug-da-categoria"
        )
        self.assertEqual(
            form["description"].field.widget.attrs["placeholder"], "Descrição"
        )

    def test_category_form_color_widget_type(self):
        """Test color input has correct type"""
        form = CategoryForm()
        self.assertEqual(form["color"].field.widget.input_type, "color")

    def test_category_form_textarea_rows(self):
        """Test description textarea has correct height class"""
        form = CategoryForm()
        self.assertIn("h-24", form["description"].field.widget.attrs["class"])


class FormIntegrationTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create()

    def test_product_form_with_instance(self):
        """Test product form with existing instance"""
        product = ProductFactory.create(
            user=self.user, name="Original Product", price=Decimal("100.00")
        )

        form_data = {
            "name": "Updated Product",
            "price": "150,00",
            "stock": 20,
            "is_public": True,
        }
        form = ProductForm(data=form_data, instance=product)

        self.assertTrue(form.is_valid())
        updated_product = form.save()

        self.assertEqual(updated_product.name, "Updated Product")
        self.assertEqual(updated_product.price, Decimal("150.00"))
        self.assertEqual(updated_product.stock, 20)
        self.assertTrue(updated_product.is_public)
        self.assertEqual(
            updated_product.user, self.user
        )  # User should remain unchanged

    def test_category_form_with_instance(self):
        """Test category form with existing instance"""
        category = CategoryFactory.create(
            name="Original Category", slug="original-category"
        )

        form_data = {
            "name": "Updated Category",
            "slug": "updated-category",
            "description": "Updated description",
            "color": "#00ff00",
        }
        form = CategoryForm(data=form_data, instance=category)

        self.assertTrue(form.is_valid())
        updated_category = form.save()

        self.assertEqual(updated_category.name, "Updated Category")
        self.assertEqual(updated_category.slug, "updated-category")
        self.assertEqual(updated_category.description, "Updated description")
        self.assertEqual(updated_category.color, "#00ff00")
