# AVM API Test Suite

Comprehensive test suite for the AVM (Automated Valuation Model) API with 95+ test cases covering all components.

## 📊 Test Coverage

- **35 Functions** tested across core service layer
- **16 API Endpoints** tested with various scenarios  
- **Error Handling** comprehensive edge case coverage
- **Integration Tests** end-to-end workflow validation
- **Performance Tests** response time and load testing

## 🚀 Quick Start

### Install Test Dependencies

```bash
cd AVM_Api
pip install -r tests/requirements-test.txt
```

### Run All Tests

```bash
# Run complete test suite
pytest

# Run with coverage report
pytest --cov=property_api_service --cov=property_rest_api --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only  
pytest -m api           # API endpoint tests only
```

## 📁 Test Structure

```
tests/
├── test_property_api_service.py    # Unit tests for service layer (35+ tests)
├── test_rest_api.py               # API endpoint tests (45+ tests)
├── test_integration.py            # End-to-end integration tests (15+ tests)
├── pytest.ini                    # Test configuration
├── requirements-test.txt          # Test dependencies
└── README.md                     # This documentation
```

## 🧪 Test Categories

### Unit Tests (`test_property_api_service.py`)
- Service initialization and configuration
- Address parsing with edge cases
- Data cleaning and formatting
- API response processing
- Error handling scenarios
- Currency and date formatting
- Data validation

### API Tests (`test_rest_api.py`)
- All 16 REST endpoints
- Request/response validation
- Error code verification (400, 404, 500)
- JSON payload validation
- Batch processing scenarios
- CORS and content-type handling
- Performance characteristics

### Integration Tests (`test_integration.py`)
- End-to-end API workflows
- Real component interactions
- Data consistency across endpoints
- Browser integration testing
- Comprehensive analysis flow

## 🏃‍♂️ Running Specific Tests

### By Test File
```bash
pytest tests/test_property_api_service.py      # Service tests only
pytest tests/test_rest_api.py                  # API tests only
pytest tests/test_integration.py               # Integration tests only
```

### By Test Function
```bash
pytest tests/test_property_api_service.py::TestPropertyAPIService::test_parse_address_valid
pytest tests/test_rest_api.py::TestRestAPI::test_health_check
```

### By Markers
```bash
pytest -m "unit and not slow"           # Fast unit tests
pytest -m "api or integration"          # All API-related tests  
pytest -m "error"                       # Error handling tests
pytest -m "performance"                 # Performance tests
```

## 📈 Coverage Reports

### Generate HTML Coverage Report
```bash
pytest --cov=property_api_service --cov=property_rest_api --cov-report=html
open htmlcov/index.html  # View detailed coverage
```

### Coverage Targets
- **Overall Coverage**: 70%+ (enforced by pytest.ini)
- **Service Layer**: 85%+ target
- **API Layer**: 80%+ target
- **Critical Functions**: 95%+ target

## 🔧 Test Configuration

### Pytest Settings (pytest.ini)
- Minimum coverage: 70%
- Test timeout: 5 minutes
- HTML and terminal coverage reports
- Custom test markers for organization
- Warning filters for clean output

### Environment Variables
Tests use the same `.env` file as the main application:
```bash
ATTOM_API_KEY=your_api_key_here
```

## 🚨 Running Tests in CI/CD

### GitHub Actions Example
```yaml
- name: Install test dependencies
  run: pip install -r tests/requirements-test.txt

- name: Run tests with coverage
  run: pytest --cov --cov-report=xml

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
```

### Local Pre-commit Testing
```bash
# Quick test run before committing
pytest tests/test_rest_api.py::TestRestAPI::test_health_check
pytest -m "unit and not slow"
```

## 🎯 Test Scenarios Covered

### Address Handling
- ✅ Valid address formats
- ✅ Empty/null addresses
- ✅ Special characters and Unicode
- ✅ Very long addresses
- ✅ Address parsing edge cases

### API Response Processing
- ✅ Successful responses
- ✅ API errors (404, 500, rate limits)
- ✅ Network timeouts
- ✅ Malformed JSON responses
- ✅ Missing data fields

### Data Cleaning & Formatting
- ✅ Currency formatting ($1,234,567)
- ✅ Date standardization
- ✅ Property size calculations
- ✅ Owner name concatenation
- ✅ Missing data handling (N/A values)

### API Endpoints
- ✅ All 16 endpoints tested
- ✅ Request validation
- ✅ Response structure verification
- ✅ Error handling
- ✅ Batch processing limits

### Integration Scenarios
- ✅ Health check availability
- ✅ Chart interface accessibility
- ✅ End-to-end property workflows
- ✅ Data consistency across endpoints
- ✅ Browser automation

## 🐛 Debugging Failed Tests

### Verbose Output
```bash
pytest -v -s  # Verbose with print statements
```

### Debug Specific Test
```bash
pytest tests/test_property_api_service.py::test_parse_address_valid -v -s --tb=long
```

### Coverage Analysis
```bash
pytest --cov --cov-report=term-missing  # See uncovered lines
```

## 📝 Adding New Tests

### Test Structure Template
```python
def test_new_functionality(self, service):
    \"\"\"Test description explaining what is being tested\"\"\"
    # Arrange
    input_data = {"test": "data"}
    
    # Act  
    result = service.method_under_test(input_data)
    
    # Assert
    assert result['expected_field'] == 'expected_value'
```

### Mocking External APIs
```python
@patch('requests.get')
def test_api_call(self, mock_get, service):
    mock_response = Mock()
    mock_response.json.return_value = {'test': 'data'}
    mock_get.return_value = mock_response
    
    result = service.get_external_data()
    
    assert result['test'] == 'data'
    mock_get.assert_called_once()
```

## ⚡ Performance Testing

### Response Time Validation
```bash
pytest -m performance  # Run performance tests
```

Performance targets:
- API endpoints: < 5 seconds
- Address parsing: < 1ms per address
- Data cleaning: < 100ms per property

## 🎉 Test Results Summary

When all tests pass, you should see:
- **95+ test cases** executed successfully
- **70%+ code coverage** achieved
- **All API endpoints** validated
- **Error scenarios** properly handled
- **Integration workflows** verified

The test suite provides confidence that the AVM API system works correctly across all scenarios and maintains reliability in production.