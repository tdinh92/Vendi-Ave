# Universal Testing Agent

A comprehensive, reusable testing framework that analyzes your project, asks intelligent questions about error handling requirements, and generates tailored test suites.

## 🚀 Features

### 🔍 **Project Analysis**
- **Multi-language support**: Python, JavaScript
- **Framework detection**: Flask, FastAPI, Django, Express, React, Vue
- **Component identification**: Functions, classes, API endpoints
- **Dependency analysis**: Import mapping and framework detection

### 🤔 **Interactive Requirements Gathering**
- **Context-aware questions** about your specific project
- **Error handling scope validation**
- **Performance and reliability requirements**
- **Business logic criticality assessment**

### 🔨 **Test Generation**
- **Comprehensive test suites** with proper structure
- **Multiple testing frameworks**: pytest, unittest, Jest, Mocha
- **Error boundary validation** according to your specifications
- **Performance and integration tests**

## 📦 Installation

No installation required! Just Python 3.7+

```bash
# Make it executable
chmod +x testing_agent.py
```

## 🎯 Quick Start

### Basic Usage (Interactive)
```bash
python testing_agent.py /path/to/your/project --interactive
```

### Analysis Only
```bash
python testing_agent.py /path/to/your/project --analyze-only
```

### Automated with Default Settings
```bash
python testing_agent.py /path/to/your/project --output ./my_tests
```

## 📊 Example Usage

### For Your AVM API
```bash
cd /workspace/tools
python testing_agent.py ../AVM_Api --interactive --output ../AVM_Api/tests
```

This will:
1. Analyze all Python files in AVM_Api
2. Detect Flask framework and API endpoints
3. Ask you about error handling requirements
4. Generate comprehensive test suites

### For Any Python Project
```bash
python testing_agent.py /path/to/my/django/app --interactive
```

## 🤔 Questions It Will Ask You

### **General Testing**
- What testing framework do you prefer?
- Target test coverage percentage?
- Include integration tests?
- Include performance tests?

### **Function-Specific**
- Which functions are critical for business logic?
- How should functions handle null/None inputs?
- What's acceptable for edge cases?

### **API-Specific** 
- What error codes for invalid data? (400, 422, 500)
- Acceptable response times?
- Authentication requirements?

### **Error Handling Scope**
- Should errors be logged?
- Graceful degradation on failures?
- Retry logic for failed operations?
- User-facing error message strategy?

## 📁 Generated Test Structure

```
tests/
├── test_functions.py      # Unit tests for functions
├── test_apis.py          # API endpoint tests
├── test_classes.py       # Class/object tests  
├── test_error_handling.py # Error boundary tests
└── pytest.ini           # Test configuration
```

## 🔧 Customization

### Adding New Languages

```python
def _analyze_java_file(self, file_path: Path):
    """Add Java analysis"""
    # Your Java parsing logic
    pass
```

### Adding New Frameworks

```python
framework_indicators = {
    'your_framework': ['import pattern', 'usage pattern']
}
```

### Custom Question Types

```python
def _ask_custom_question(self):
    """Add your domain-specific questions"""
    pass
```

## 📋 Command Line Options

```bash
python testing_agent.py <project_path> [options]

Required:
  project_path              Path to project to analyze

Options:
  --output, -o DIR         Output directory for tests (default: ./tests)
  --interactive, -i        Run interactive questionnaire  
  --analyze-only          Only analyze project, don't generate tests
  --help, -h              Show help message
```

## 🎯 Real-World Examples

### Example 1: Flask API Testing
```bash
python testing_agent.py ../AVM_Api --interactive
```

**Analysis Results:**
- 6 functions found (get_avm_history, get_basic_profile, etc.)
- 8 API endpoints found (/property/complete, /property/combined, etc.)
- Flask framework detected
- API project type

**Questions Asked:**
- "Is 'get_avm_history()' critical for business logic?" → Yes
- "What error code for invalid data on /property/complete?" → 400
- "Acceptable response time for /property/complete?" → 5 seconds
- "Should errors be logged?" → Yes

**Generated Tests:**
- API endpoint tests with proper error codes
- Function tests with null handling
- Response time validation
- Error logging verification

### Example 2: Library/Package Testing
```bash
python testing_agent.py ../my_utils_library --interactive
```

**Analysis Results:**
- 15 utility functions found
- 3 classes found
- No APIs (library project type)

**Generated Tests:**
- Comprehensive function unit tests
- Class initialization and method tests
- Edge case handling
- Input validation tests

## 🔍 Analysis Output

The tool generates a detailed analysis of your project:

```json
{
  "functions": [
    {
      "name": "get_avm_history",
      "file": "property_api_service.py",
      "line": 118,
      "args": ["address"],
      "is_async": false,
      "decorators": [],
      "docstring": "Get AVM data from Attom API"
    }
  ],
  "apis": [
    {
      "route": "/property/complete",
      "methods": ["POST"],
      "file": "property_rest_api.py",
      "framework": "flask"
    }
  ],
  "framework": "flask",
  "project_type": "api"
}
```

## 🚀 Advanced Features

### **Smart Test Generation**
- Tests are tailored to your specific error handling requirements
- Framework-specific test patterns (pytest vs unittest)
- Performance tests based on your SLA requirements

### **Error Boundary Validation**
- Ensures errors are handled within your defined scope
- Validates retry logic implementation
- Tests graceful degradation scenarios

### **Reusable Templates**
- Save question responses for similar projects
- Customize test templates for your team's standards
- Export/import testing configurations

## 🤝 Integration with Development Workflow

### CI/CD Integration
```yaml
# .github/workflows/test.yml
- name: Generate Tests
  run: python tools/testing_agent.py . --output ./tests

- name: Run Generated Tests  
  run: pytest tests/ --cov
```

### Pre-commit Hook
```bash
#!/bin/sh
python tools/testing_agent.py . --analyze-only
# Check if new functions need tests
```

## 📈 Next Steps After Generation

1. **Review Generated Tests**: Fill in TODO sections with actual test data
2. **Install Dependencies**: `pip install pytest pytest-cov`
3. **Run Tests**: `pytest tests/ --cov`
4. **Customize**: Adapt tests to your specific business logic
5. **Integrate**: Add to CI/CD pipeline

## 🛠️ Extending the Agent

### Add New Question Types
```python
def _ask_business_specific_questions(self):
    """Add your domain questions"""
    self.requirements['data_retention'] = self._ask_numeric(
        "How long should test data be retained (days)?",
        default=30
    )
```

### Add New Test Generators
```python
def _generate_security_tests(self, output_path: Path):
    """Generate security-focused tests"""
    # Your security test templates
    pass
```

---

## 💡 Pro Tips

1. **Run interactively first** to understand what questions will be asked
2. **Save your requirements** - the tool outputs JSON you can reuse
3. **Start with critical functions** - focus testing efforts on business logic
4. **Use analyze-only** for large codebases to understand scope first
5. **Customize templates** - modify generated tests to match your team's style

**Built to be your universal testing companion for any project! 🧪**