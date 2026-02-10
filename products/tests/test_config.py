"""
Test Configuration for Kore Product Manager

This module provides configuration for running tests efficiently.
"""

# Quick test suite for development
QUICK_TESTS = [
    "products.tests.test_models",
    "products.tests.test_forms",
]

# Full test suite including integration tests
FULL_TESTS = [
    "products.tests.test_models",
    "products.tests.test_forms",
    "products.tests.test_views",
    "products.tests.test_integration",
]

# Model tests only (fastest)
MODEL_TESTS = [
    "products.tests.test_models",
]

# View tests only
VIEW_TESTS = [
    "products.tests.test_views",
]

# Integration tests only (slowest)
INTEGRATION_TESTS = [
    "products.tests.test_integration",
]


def run_test_suite(suite_type="quick"):
    """
    Run test suite based on type

    Args:
        suite_type: 'quick', 'full', 'models', 'views', 'integration'
    """
    import django
    from django.conf import settings
    from django.test.utils import get_runner

    django.setup()

    TestRunner = get_runner(settings)

    if suite_type == "quick":
        test_labels = QUICK_TESTS
    elif suite_type == "full":
        test_labels = FULL_TESTS
    elif suite_type == "models":
        test_labels = MODEL_TESTS
    elif suite_type == "views":
        test_labels = VIEW_TESTS
    elif suite_type == "integration":
        test_labels = INTEGRATION_TESTS
    else:
        raise ValueError(f"Unknown suite type: {suite_type}")

    runner = TestRunner(verbosity=2, keepdb=False)
    failures = runner.run_tests(test_labels)

    return failures
