# Test Suite Documentation

## Overview

This is a comprehensive test suite for the Kore Product Manager Django application. The test suite covers all aspects of the application including models, views, forms, and integration workflows.

## Test Structure

### Directory Organization

```text
products/tests/
├── __init__.py                 # Test package initialization
├── factories.py               # Test factories for creating test data
├── test_models.py             # Model tests for all app models
├── test_forms.py              # Form tests for ProductForm and CategoryForm
├── test_views.py              # View tests for all app views
├── test_integration.py        # Integration tests for complete user workflows
├── test_utils.py              # Test utilities and mixins
└── ../tests.py                # Main test module that imports all tests
```

### Test Coverage Areas

#### 1. Model Tests (`test_models.py`)

- **Category Model**: Creation, validation, relationships, verbose names
- **Product Model**: Creation, user relationships, category relationships, public/private filtering
- **PriceHistory Model**: Creation, ordering, product relationships, string representation
- **Profile Model**: Creation via signals, theme management, user relationships
- **Signal Tests**: Profile creation signal, price history tracking signal

#### 2. Form Tests (`test_forms.py`)

- **ProductForm**:
  - Valid data submission with various price formats
  - Price validation (comma/dot separators, thousands separators)
  - Widget configuration and attributes
  - Form validation with instances
- **CategoryForm**:
  - Valid data submission
  - Required and optional fields
  - Widget configuration
  - Form validation with instances

#### 3. View Tests (`test_views.py`)

- **Product Views**:
  - Product list with filtering and sorting
  - Product creation, update, deletion
  - Product detail view with permission checks
  - Price history views
- **Category Views**:
  - Category CRUD operations
  - Category duplication
  - Sorting functionality
- **Public Catalog Views**:
  - Public product listing
  - User-specific catalogs
- **Account Views**:
  - Profile management
  - Account deletion
- **Utility Views**:
  - Theme toggle
  - View mode setting
  - Custom logout

#### 4. Integration Tests (`test_integration.py`)

- **Complete Product Lifecycle**: Create → View → Update → Delete workflow
- **Product Filtering Workflow**: Complex filtering and sorting scenarios
- **Category Management Workflow**: Complete CRUD operations with duplication
- **User Account Workflow**: Registration, profile management, preferences
- **Price History Tracking**: Automatic price change tracking
- **Error Handling**: Permission denied, form validation, 404 scenarios

#### 5. Test Utilities (`test_utils.py`)

- **BaseTestCase**: Common setup and assertion utilities
- **Mixins**: Specialized testing utilities for:
  - Authentication testing
  - Model testing
  - Price history testing
  - Permission testing
  - Form testing
  - Response testing
  - Filter testing

### Test Factories (`factories.py`)

- **UserFactory**: Creates test users with profiles
- **CategoryFactory**: Creates test categories
- **ProductFactory**: Creates test products with optional relationships
- **PriceHistoryFactory**: Creates price history entries

## Running Tests

### Run All Tests

```bash
python manage.py test
```

### Run Specific Test Classes

```bash
# Model tests
python manage.py test products.tests.test_models

# View tests
python manage.py test products.tests.test_views

# Form tests
python manage.py test products.tests.test_forms

# Integration tests
python manage.py test products.tests.test_integration
```

### Run Specific Test Methods

```bash
# Single test method
python manage.py test products.tests.test_models.ProductModelTest.test_product_creation

# Tests with specific pattern
python manage.py test products.tests -k test_product_creation
```

### Generate Coverage Report

```bash
# Install coverage if not already installed
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

## Test Data Management

### Database Setup

Tests use Django's test database that's created and destroyed automatically.
All test data is isolated between test methods.

### Factories Usage

```python
# Create a user with profile
user = UserFactory.create(username='testuser')

# Create a category
category = CategoryFactory.create(name='Electronics')

# Create a product with relationships
product = ProductFactory.create(
    user=user,
    name='Laptop',
    price=Decimal('999.99'),
    categories=[category]
)
```

## Best Practices Used

1. **Test Isolation**: Each test method runs in isolation with clean data
2. **Descriptive Test Names**: Test methods clearly describe what they test
3. **Assertion Messages**: Clear assertion messages for debugging
4. **Test Factories**: Reusable factories for test data creation
5. **Test Utilities**: Shared utilities for common test patterns
6. **Permission Testing**: Comprehensive permission and access control testing
7. **Error Scenarios**: Testing of error conditions and edge cases
8. **Integration Testing**: End-to-end workflow testing

## Future Enhancements

1. **Performance Testing**: Load testing for high-traffic views
2. **API Testing**: If API endpoints are added
3. **JavaScript Testing**: Frontend functionality testing
4. **Security Testing**: CSRF, XSS, and security vulnerability testing
5. **Browser Testing**: Selenium tests for complex user interactions

## Continuous Integration

These tests are designed to run in CI/CD environments:

- No external dependencies required
- Fast execution time
- Clear pass/fail results
- Proper isolation between tests

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all test modules are properly imported in `tests.py`
2. **Database Errors**: Test database should be created automatically
3. **Permission Errors**: Ensure test users are properly created and logged in
4. **Factory Errors**: Check factory default values and required fields

### Debugging Tips

1. Use `print()` statements in tests to see intermediate values
2. Use Django's `pdb` for interactive debugging
3. Check test database contents in shell: `python manage.py shell --settings=your_project.settings_test`
4. Use `--verbosity=2` flag for detailed test output

## Performance Considerations

- Tests are optimized for speed with minimal database queries
- Factories use `create()` instead of `build()` when relationships are needed
- Test methods are kept small and focused
- Setup is done in `setUp()` to reduce code duplication
