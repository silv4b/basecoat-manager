"""
Test package for products app.

This package contains all test modules for the products app.
Run tests with:
- All tests: python manage.py test products.tests
- Specific module: python manage.py test products.tests.test_models
- Quick test: python manage.py test products.tests.test_models products.tests.test_forms
"""

# Import all test modules for test discovery
from . import test_models
from . import test_forms
from . import test_views
from . import test_integration
from . import factories
from . import test_utils
