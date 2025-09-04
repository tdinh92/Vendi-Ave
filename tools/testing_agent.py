#!/usr/bin/env python3
"""
Universal Testing Agent - Enhanced Reusable Testing Framework
Analyzes any project, asks contextual questions, generates comprehensive tests
Supports Python, JavaScript, TypeScript, API testing, and more
"""

import os
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import argparse
import subprocess
import importlib.util


class ProjectAnalyzer:
    """Analyzes project structure and identifies testable components"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.functions = []
        self.classes = []
        self.apis = []
        self.imports = []
        self.config_files = []
        self.test_files = []
        self.project_metadata = {}
    
    def analyze(self) -> Dict[str, Any]:
        """Main analysis method"""
        print(f"🔍 Analyzing project: {self.project_path}")
        
        # Scan Python files
        for py_file in self.project_path.rglob("*.py"):
            if not self._should_skip_file(py_file):
                self._analyze_python_file(py_file)
        
        # Scan JavaScript/TypeScript files
        for js_file in self.project_path.rglob("*.js"):
            if not self._should_skip_file(js_file):
                self._analyze_javascript_file(js_file)
        
        for ts_file in self.project_path.rglob("*.ts"):
            if not self._should_skip_file(ts_file):
                self._analyze_typescript_file(ts_file)
                
        # Scan existing test files
        self._find_existing_tests()
        
        # Scan configuration files
        self._find_config_files()
        
        # Detect project metadata
        self._detect_project_metadata()
        
        # Detect framework patterns
        framework = self._detect_framework()
        
        return {
            'functions': self.functions,
            'classes': self.classes,
            'apis': self.apis,
            'imports': self.imports,
            'config_files': self.config_files,
            'test_files': self.test_files,
            'project_metadata': self.project_metadata,
            'framework': framework,
            'project_type': self._determine_project_type(),
            'test_coverage': self._estimate_test_coverage()
        }
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Skip files that shouldn't be analyzed"""
        skip_dirs = {'__pycache__', '.git', 'node_modules', 'venv', 'env', '.pytest_cache'}
        skip_files = {'__init__.py'}
        
        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            return True
        if file_path.name in skip_files:
            return True
        return False
    
    def _analyze_python_file(self, file_path: Path):
        """Analyze Python file for functions, classes, APIs"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.functions.append({
                        'name': node.name,
                        'file': str(file_path.relative_to(self.project_path)),
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                        'docstring': ast.get_docstring(node)
                    })
                
                elif isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    self.classes.append({
                        'name': node.name,
                        'file': str(file_path.relative_to(self.project_path)),
                        'line': node.lineno,
                        'methods': [m.name for m in methods],
                        'base_classes': [self._get_base_name(base) for base in node.bases],
                        'docstring': ast.get_docstring(node)
                    })
                
                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    self._extract_imports(node, file_path)
            
            # Check for Flask/FastAPI routes
            self._detect_api_routes(content, file_path)
            
        except Exception as e:
            print(f"⚠️ Could not analyze {file_path}: {e}")
    
    def _analyze_typescript_file(self, file_path: Path):
        """Analyze TypeScript files for functions and classes"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # TypeScript function patterns
            function_patterns = [
                r'(?:export\s+)?(?:async\s+)?function\s+(\w+)',
                r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>', 
                r'(\w+)\s*:\s*(?:async\s+)?\([^)]*\)\s*=>'
            ]
            
            for pattern in function_patterns:
                for match in re.finditer(pattern, content):
                    func_name = match.group(1)
                    if func_name:
                        line_num = content[:match.start()].count('\n') + 1
                        self.functions.append({
                            'name': func_name,
                            'file': str(file_path.relative_to(self.project_path)),
                            'line': line_num,
                            'language': 'typescript',
                            'is_async': 'async' in match.group(0),
                            'is_exported': 'export' in match.group(0)
                        })
            
            # TypeScript class patterns
            class_pattern = r'(?:export\s+)?class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                self.classes.append({
                    'name': class_name,
                    'file': str(file_path.relative_to(self.project_path)),
                    'line': line_num,
                    'language': 'typescript',
                    'is_exported': 'export' in match.group(0)
                })
                
        except Exception as e:
            print(f"⚠️ Could not analyze {file_path}: {e}")
    
    def _analyze_javascript_file(self, file_path: Path):
        """Basic JavaScript analysis for functions and exports"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex patterns for JavaScript functions
            function_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)\s*=>|\([^)]*\)\s*{)|(\w+)\s*:\s*(?:async\s+)?function)'
            
            for match in re.finditer(function_pattern, content):
                func_name = match.group(1) or match.group(2) or match.group(3)
                if func_name:
                    line_num = content[:match.start()].count('\n') + 1
                    self.functions.append({
                        'name': func_name,
                        'file': str(file_path.relative_to(self.project_path)),
                        'line': line_num,
                        'language': 'javascript',
                        'is_async': 'async' in match.group(0)
                    })
            
        except Exception as e:
            print(f"⚠️ Could not analyze {file_path}: {e}")
    
    def _detect_api_routes(self, content: str, file_path: Path):
        """Detect Flask/FastAPI/Express API routes"""
        # Flask routes
        flask_pattern = r'@app\.route\(["\']([^"\']+)["\'](?:,\s*methods\s*=\s*\[([^\]]+)\])?'
        for match in re.finditer(flask_pattern, content):
            route = match.group(1)
            methods = match.group(2) if match.group(2) else 'GET'
            methods = [m.strip().strip('"\'') for m in methods.split(',')]
            
            self.apis.append({
                'route': route,
                'methods': methods,
                'file': str(file_path.relative_to(self.project_path)),
                'framework': 'flask'
            })
        
        # FastAPI routes
        fastapi_pattern = r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        for match in re.finditer(fastapi_pattern, content):
            method = match.group(1).upper()
            route = match.group(2)
            
            self.apis.append({
                'route': route,
                'methods': [method],
                'file': str(file_path.relative_to(self.project_path)),
                'framework': 'fastapi'
            })
    
    def _extract_imports(self, node: ast.AST, file_path: Path):
        """Extract import information"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.imports.append({
                    'module': alias.name,
                    'alias': alias.asname,
                    'file': str(file_path.relative_to(self.project_path))
                })
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                self.imports.append({
                    'module': f"{module}.{alias.name}" if module else alias.name,
                    'from_module': module,
                    'alias': alias.asname,
                    'file': str(file_path.relative_to(self.project_path))
                })
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Extract decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        return str(decorator)
    
    def _get_base_name(self, base: ast.AST) -> str:
        """Extract base class name"""
        if isinstance(base, ast.Name):
            return base.id
        return str(base)
    
    def _find_config_files(self):
        """Find configuration files"""
        config_patterns = ['*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '*.env', 'requirements.txt', 'package.json']
        
        for pattern in config_patterns:
            for config_file in self.project_path.rglob(pattern):
                if not self._should_skip_file(config_file):
                    self.config_files.append(str(config_file.relative_to(self.project_path)))
    
    def _detect_framework(self) -> str:
        """Detect the main framework being used"""
        framework_indicators = {
            'flask': ['from flask import', 'import flask', '@app.route'],
            'fastapi': ['from fastapi import', 'import fastapi', '@app.get'],
            'django': ['from django import', 'import django'],
            'express': ['express()', 'app.get(', 'app.post('],
            'react': ['import React', 'from react'],
            'vue': ['import Vue', 'from vue']
        }
        
        all_content = ""
        for py_file in self.project_path.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    all_content += f.read().lower()
            except:
                continue
        
        for js_file in self.project_path.rglob("*.js"):
            try:
                with open(js_file, 'r') as f:
                    all_content += f.read().lower()
            except:
                continue
        
        detected_frameworks = []
        for framework, indicators in framework_indicators.items():
            if any(indicator.lower() in all_content for indicator in indicators):
                detected_frameworks.append(framework)
        
        return detected_frameworks[0] if detected_frameworks else 'unknown'
    
    def _find_existing_tests(self):
        """Find existing test files in the project"""
        test_patterns = ['test_*.py', '*_test.py', '*.test.js', '*.spec.js', '*.test.ts', '*.spec.ts']
        
        for pattern in test_patterns:
            for test_file in self.project_path.rglob(pattern):
                if not self._should_skip_file(test_file):
                    self.test_files.append({
                        'file': str(test_file.relative_to(self.project_path)),
                        'type': self._determine_test_type(test_file),
                        'framework': self._detect_test_framework(test_file)
                    })
    
    def _determine_test_type(self, test_file: Path) -> str:
        """Determine what type of test file this is"""
        name = test_file.name.lower()
        if 'integration' in name or 'e2e' in name:
            return 'integration'
        elif 'unit' in name:
            return 'unit'
        elif 'api' in name:
            return 'api'
        else:
            return 'unit'  # default
    
    def _detect_test_framework(self, test_file: Path) -> str:
        """Detect which testing framework is used in a test file"""
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            if 'import pytest' in content or 'from pytest' in content:
                return 'pytest'
            elif 'import unittest' in content or 'from unittest' in content:
                return 'unittest'
            elif 'describe(' in content and 'it(' in content:
                return 'jest' if test_file.suffix in ['.js', '.ts'] else 'mocha'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def _detect_project_metadata(self):
        """Detect project metadata from common files"""
        # Package.json for Node.js projects
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    self.project_metadata['package_json'] = {
                        'name': data.get('name'),
                        'version': data.get('version'),
                        'scripts': data.get('scripts', {}),
                        'dependencies': list(data.get('dependencies', {}).keys()),
                        'devDependencies': list(data.get('devDependencies', {}).keys())
                    }
            except:
                pass
        
        # Requirements.txt for Python projects
        requirements_txt = self.project_path / 'requirements.txt'
        if requirements_txt.exists():
            try:
                with open(requirements_txt) as f:
                    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    self.project_metadata['requirements'] = requirements
            except:
                pass
        
        # Setup.py for Python packages
        setup_py = self.project_path / 'setup.py'
        if setup_py.exists():
            self.project_metadata['has_setup_py'] = True
    
    def _estimate_test_coverage(self) -> Dict[str, Any]:
        """Estimate current test coverage based on existing tests"""
        total_functions = len(self.functions)
        total_classes = len(self.classes)
        total_apis = len(self.apis)
        total_testable = total_functions + total_classes + total_apis
        
        existing_tests = len(self.test_files)
        
        # Simple heuristic: assume each test file covers ~5 testable items
        estimated_covered = min(existing_tests * 5, total_testable)
        coverage_percent = (estimated_covered / total_testable * 100) if total_testable > 0 else 0
        
        return {
            'total_testable_items': total_testable,
            'existing_test_files': existing_tests,
            'estimated_coverage_percent': coverage_percent,
            'functions': total_functions,
            'classes': total_classes,
            'apis': total_apis
        }
    
    def _determine_project_type(self) -> str:
        """Determine the type of project"""
        if self.apis:
            return 'api'
        elif any('class' in str(cls) for cls in self.classes):
            return 'library'
        elif self.functions:
            return 'scripts'
        else:
            return 'unknown'


class InteractiveQuestionnaire:
    """Asks contextual questions about error handling and testing requirements"""
    
    def __init__(self, analysis: Dict[str, Any]):
        self.analysis = analysis
        self.requirements = {}
    
    def ask_questions(self) -> Dict[str, Any]:
        """Main questionnaire flow"""
        print("\n" + "="*60)
        print("🤔 TESTING REQUIREMENTS QUESTIONNAIRE")
        print("="*60)
        
        # General project questions
        self._ask_general_questions()
        
        # Function-specific questions
        if self.analysis['functions']:
            self._ask_function_questions()
        
        # API-specific questions
        if self.analysis['apis']:
            self._ask_api_questions()
        
        # Class-specific questions
        if self.analysis['classes']:
            self._ask_class_questions()
        
        # Error handling scope
        self._ask_error_handling_questions()
        
        return self.requirements
    
    def _ask_general_questions(self):
        """Ask general testing questions"""
        print("\n📋 GENERAL TESTING PREFERENCES")
        print("-" * 40)
        
        self.requirements['test_framework'] = self._ask_choice(
            "What testing framework do you prefer?",
            ['pytest', 'unittest', 'jest', 'mocha', 'other']
        )
        
        self.requirements['coverage_target'] = self._ask_numeric(
            "Target test coverage percentage (0-100):",
            default=80
        )
        
        self.requirements['include_integration'] = self._ask_yes_no(
            "Include integration tests?",
            default=True
        )
        
        self.requirements['include_performance'] = self._ask_yes_no(
            "Include performance/load tests?",
            default=False
        )
    
    def _ask_function_questions(self):
        """Ask questions about function testing"""
        print("\n🔧 FUNCTION TESTING")
        print("-" * 40)
        
        critical_functions = []
        for func in self.analysis['functions'][:5]:  # Show first 5 functions
            is_critical = self._ask_yes_no(
                f"Is '{func['name']}()' critical for business logic?",
                default=True
            )
            if is_critical:
                critical_functions.append(func['name'])
        
        self.requirements['critical_functions'] = critical_functions
        
        self.requirements['null_handling'] = self._ask_choice(
            "How should functions handle null/None inputs?",
            ['raise_exception', 'return_none', 'return_default', 'ask_per_function']
        )
    
    def _ask_api_questions(self):
        """Ask questions about API testing"""
        print("\n🌐 API TESTING")
        print("-" * 40)
        
        for api in self.analysis['apis'][:3]:  # Show first 3 APIs
            route = api['route']
            
            error_code = self._ask_choice(
                f"What error code for invalid data on {route}?",
                ['400', '422', '500', 'custom']
            )
            
            timeout = self._ask_numeric(
                f"Acceptable response time for {route} (seconds):",
                default=5.0
            )
            
            self.requirements[f'api_{route.replace("/", "_")}'] = {
                'error_code': error_code,
                'timeout': timeout,
                'methods': api['methods']
            }
        
        self.requirements['auth_required'] = self._ask_yes_no(
            "Do APIs require authentication?",
            default=True
        )
    
    def _ask_class_questions(self):
        """Ask questions about class testing"""
        print("\n🏗️ CLASS TESTING")
        print("-" * 40)
        
        for cls in self.analysis['classes'][:3]:  # Show first 3 classes
            class_name = cls['name']
            
            init_required = self._ask_yes_no(
                f"Does {class_name} require specific initialization parameters?",
                default=True
            )
            
            state_matters = self._ask_yes_no(
                f"Does {class_name} maintain important state between method calls?",
                default=True
            )
            
            self.requirements[f'class_{class_name}'] = {
                'init_required': init_required,
                'state_matters': state_matters,
                'methods': cls['methods']
            }
    
    def _ask_error_handling_questions(self):
        """Ask about error handling scope and expectations"""
        print("\n⚠️ ERROR HANDLING SCOPE")
        print("-" * 40)
        
        self.requirements['error_logging'] = self._ask_yes_no(
            "Should errors be logged?",
            default=True
        )
        
        self.requirements['graceful_degradation'] = self._ask_yes_no(
            "Should the system gracefully degrade on errors?",
            default=True
        )
        
        self.requirements['retry_logic'] = self._ask_yes_no(
            "Should failed operations be retried automatically?",
            default=False
        )
        
        self.requirements['user_facing_errors'] = self._ask_choice(
            "How should user-facing errors be handled?",
            ['generic_message', 'detailed_message', 'custom_per_error', 'silent_fail']
        )
    
    def _ask_choice(self, question: str, choices: List[str]) -> str:
        """Ask multiple choice question"""
        print(f"\n{question}")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        while True:
            try:
                answer = input(f"Choose (1-{len(choices)}): ").strip()
                index = int(answer) - 1
                if 0 <= index < len(choices):
                    return choices[index]
                print(f"Please choose a number between 1 and {len(choices)}")
            except (ValueError, KeyboardInterrupt):
                print("Please enter a valid number")
    
    def _ask_yes_no(self, question: str, default: bool = None) -> bool:
        """Ask yes/no question"""
        default_text = " [Y/n]" if default else " [y/N]" if default is False else " [y/n]"
        
        while True:
            answer = input(f"{question}{default_text}: ").strip().lower()
            if answer in ['y', 'yes']:
                return True
            elif answer in ['n', 'no']:
                return False
            elif answer == '' and default is not None:
                return default
            print("Please enter y/yes or n/no")
    
    def _ask_numeric(self, question: str, default: float = None) -> float:
        """Ask numeric question"""
        default_text = f" (default: {default})" if default is not None else ""
        
        while True:
            try:
                answer = input(f"{question}{default_text}: ").strip()
                if answer == '' and default is not None:
                    return default
                return float(answer)
            except (ValueError, KeyboardInterrupt):
                print("Please enter a valid number")


class TestGenerator:
    """Generates comprehensive test suites based on analysis and requirements"""
    
    def __init__(self, analysis: Dict[str, Any], requirements: Dict[str, Any]):
        self.analysis = analysis
        self.requirements = requirements
        self.test_framework = requirements.get('test_framework', 'pytest')
    
    def generate_tests(self, output_dir: str) -> List[str]:
        """Generate all test files with intelligent organization"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        generated_files = []
        
        # Organize by language/framework
        python_functions = [f for f in self.analysis['functions'] if f.get('language') != 'javascript' and f.get('language') != 'typescript']
        js_functions = [f for f in self.analysis['functions'] if f.get('language') in ['javascript', 'typescript']]
        
        # Generate Python tests
        if python_functions:
            test_file = self._generate_function_tests(output_path, python_functions, 'python')
            generated_files.append(test_file)
        
        # Generate JavaScript/TypeScript tests  
        if js_functions:
            test_file = self._generate_function_tests(output_path, js_functions, 'javascript')
            generated_files.append(test_file)
        
        # Generate API tests
        if self.analysis['apis']:
            test_file = self._generate_api_tests(output_path)
            generated_files.append(test_file)
        
        # Generate class tests
        if self.analysis['classes']:
            test_file = self._generate_class_tests(output_path)
            generated_files.append(test_file)
        
        # Generate error handling tests
        test_file = self._generate_error_tests(output_path)
        generated_files.append(test_file)
        
        # Generate integration tests if APIs exist
        if self.analysis['apis'] and self.requirements.get('include_integration'):
            test_file = self._generate_integration_tests(output_path)
            generated_files.append(test_file)
        
        # Generate test configuration
        config_file = self._generate_test_config(output_path)
        generated_files.append(config_file)
        
        # Generate test runner script
        runner_file = self._generate_test_runner(output_path)
        generated_files.append(runner_file)
        
        return generated_files
    
    def _generate_function_tests(self, output_path: Path, functions_list: List = None, language: str = 'python') -> str:
        """Generate function unit tests"""
        if functions_list is None:
            functions_list = self.analysis['functions']
            
        if language == 'python':
            test_file = output_path / "test_functions.py"
            content = self._get_test_file_header('python')
            content += "\n\n# Function Tests\n"
            
            for func in functions_list:
                if func['name'] in self.requirements.get('critical_functions', [func['name']]):
                    content += self._generate_single_function_test(func, 'python')
        else:
            test_file = output_path / "test_functions.test.js"
            content = self._get_test_file_header('javascript')
            content += "\n\n// Function Tests\n"
            
            for func in functions_list:
                if func['name'] in self.requirements.get('critical_functions', [func['name']]):
                    content += self._generate_single_function_test(func, 'javascript')
        
        with open(test_file, 'w') as f:
            f.write(content)
        
        return str(test_file)
    
    def _generate_api_tests(self, output_path: Path) -> str:
        """Generate API tests"""
        test_file = output_path / "test_apis.py"
        
        content = self._get_test_file_header()
        content += "\nimport requests\nimport pytest\nfrom unittest.mock import patch\n\n"
        content += "# API Tests\n"
        
        for api in self.analysis['apis']:
            content += self._generate_single_api_test(api)
        
        with open(test_file, 'w') as f:
            f.write(content)
        
        return str(test_file)
    
    def _generate_class_tests(self, output_path: Path) -> str:
        """Generate class tests"""
        test_file = output_path / "test_classes.py"
        
        content = self._get_test_file_header()
        content += "\n\n# Class Tests\n"
        
        for cls in self.analysis['classes']:
            content += self._generate_single_class_test(cls)
        
        with open(test_file, 'w') as f:
            f.write(content)
        
        return str(test_file)
    
    def _generate_error_tests(self, output_path: Path) -> str:
        """Generate error handling tests"""
        test_file = output_path / "test_error_handling.py"
        
        content = self._get_test_file_header()
        content += "\n\n# Error Handling Tests\n"
        
        # Generate tests based on error handling requirements
        if self.requirements.get('retry_logic'):
            content += self._generate_retry_tests()
        
        if self.requirements.get('graceful_degradation'):
            content += self._generate_degradation_tests()
        
        content += self._generate_input_validation_tests()
        
        with open(test_file, 'w') as f:
            f.write(content)
        
        return str(test_file)
    
    def _generate_test_config(self, output_path: Path) -> str:
        """Generate test configuration files"""
        if self.test_framework == 'pytest':
            config_file = output_path / "pytest.ini"
            content = f"""[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --tb=short --cov --cov-report=term-missing --cov-fail-under={self.requirements.get('coverage_target', 80)}
"""
        else:
            config_file = output_path / "test_config.json"
            content = json.dumps({
                'framework': self.test_framework,
                'coverage_target': self.requirements.get('coverage_target', 80),
                'requirements': self.requirements
            }, indent=2)
        
        with open(config_file, 'w') as f:
            f.write(content)
        
        return str(config_file)
    
    def _get_test_file_header(self, language: str = 'python') -> str:
        """Get standard test file header"""
        if language == 'python':
            if self.test_framework == 'pytest':
                return """\"\"\"
Auto-generated test suite
Generated by Universal Testing Agent
\"\"\"

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
            else:
                return """\"\"\"
Auto-generated test suite  
Generated by Universal Testing Agent
\"\"\"

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
        else:  # JavaScript/TypeScript
            framework = 'jest'  # Default for JS
            if framework == 'jest':
                return """/**
 * Auto-generated test suite
 * Generated by Universal Testing Agent
 */

const request = require('supertest');
const { expect } = require('@jest/globals');

"""
            else:  # Mocha
                return """/**
 * Auto-generated test suite
 * Generated by Universal Testing Agent
 */

const chai = require('chai');
const expect = chai.expect;
const request = require('supertest');

"""
    
    def _generate_single_function_test(self, func: Dict, language: str = 'python') -> str:
        """Generate test for a single function"""
        func_name = func['name']
        
        if language == 'python':
            test_content = f"""

class Test{func_name.title()}:
    \"\"\"Tests for {func_name}() function\"\"\"
    
    def test_{func_name}_valid_input(self):
        \"\"\"Test {func_name} with valid input\"\"\"
        # TODO: Import the function: from {func.get('file', 'module').replace('.py', '').replace('/', '.')} import {func_name}
        # TODO: Add valid input test
        pass
    
    def test_{func_name}_invalid_input(self):
        \"\"\"Test {func_name} with invalid input\"\"\"
        # TODO: Add invalid input handling test
        pass
"""
        else:  # JavaScript/TypeScript
            # Convert from snake_case to camelCase for JS conventions
            camel_name = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(func_name.split('_')))
            
            test_content = f"""

describe('{func_name}', () => {{
    // TODO: Import the function: const {{ {func_name} }} = require('../{func.get('file', 'module').replace('.js', '').replace('.ts', '')}');
    
    test('should handle valid input', () => {{
        // TODO: Add valid input test
        expect(true).toBe(true); // Placeholder
    }});
    
    test('should handle invalid input', () => {{
        // TODO: Add invalid input handling test
        expect(true).toBe(true); // Placeholder
    }});
"""
            
            # Add async test if function is async
            if func.get('is_async'):
                test_content += f"""
    test('should handle async operations', async () => {{
        // TODO: Add async test
        expect(true).toBe(true); // Placeholder
    }});
"""
            
            test_content += "});\n"
            
        # Add null handling test for Python only
        if language == 'python':
            null_handling = self.requirements.get('null_handling', 'raise_exception')
            if null_handling == 'raise_exception':
                test_content += f"""
    def test_{func_name}_null_input_raises_exception(self):
        \"\"\"Test {func_name} raises exception with null input\"\"\"
        with pytest.raises(Exception):
            {func_name}(None)
"""
            elif null_handling == 'return_none':
                test_content += f"""
    def test_{func_name}_null_input_returns_none(self):
        \"\"\"Test {func_name} returns None with null input\"\"\"
        result = {func_name}(None)
        assert result is None
"""
        
        return test_content
    
    def _generate_single_api_test(self, api: Dict) -> str:
        """Generate test for a single API endpoint"""
        route = api['route']
        safe_name = route.replace('/', '_').replace('<', '').replace('>', '').strip('_')
        
        test_content = f"""

class TestApi{safe_name.title()}:
    \"\"\"Tests for {route} endpoint\"\"\"
    
    BASE_URL = "http://localhost:5000"  # TODO: Configure base URL
    
    def test_{safe_name}_valid_request(self):
        \"\"\"Test {route} with valid request\"\"\"
        # TODO: Add valid request test
        pass
    
    def test_{safe_name}_invalid_data(self):
        \"\"\"Test {route} with invalid data\"\"\"
        # TODO: Add invalid data test
        # Expected response code: {self.requirements.get(f'api_{safe_name}', {}).get('error_code', '400')}
        pass
    
    def test_{safe_name}_response_time(self):
        \"\"\"Test {route} response time\"\"\"
        import time
        start_time = time.time()
        # TODO: Make actual request
        end_time = time.time()
        response_time = end_time - start_time
        max_time = {self.requirements.get(f'api_{safe_name}', {}).get('timeout', 5.0)}
        assert response_time < max_time, f"Response time {{response_time}} exceeds limit {{max_time}}"
"""
        
        if self.requirements.get('auth_required'):
            test_content += f"""
    def test_{safe_name}_requires_auth(self):
        \"\"\"Test {route} requires authentication\"\"\"
        # TODO: Test unauthorized access returns 401
        pass
"""
        
        return test_content
    
    def _generate_single_class_test(self, cls: Dict) -> str:
        """Generate test for a single class"""
        class_name = cls['name']
        
        test_content = f"""

class Test{class_name}:
    \"\"\"Tests for {class_name} class\"\"\"
    
    def setup_method(self):
        \"\"\"Setup for each test method\"\"\"
        # TODO: Initialize {class_name} instance
        pass
    
    def test_{class_name.lower()}_initialization(self):
        \"\"\"Test {class_name} can be initialized\"\"\"
        # TODO: Test class initialization
        pass
"""
        
        # Add method tests
        for method in cls['methods']:
            if not method.startswith('_'):  # Skip private methods
                test_content += f"""
    def test_{method}(self):
        \"\"\"Test {class_name}.{method}() method\"\"\"
        # TODO: Add {method} test
        pass
"""
        
        return test_content
    
    def _generate_retry_tests(self) -> str:
        """Generate retry logic tests"""
        return """

class TestRetryLogic:
    \"\"\"Tests for retry logic\"\"\"
    
    def test_retry_on_failure(self):
        \"\"\"Test operations are retried on failure\"\"\"
        # TODO: Test retry mechanism
        pass
    
    def test_max_retries_respected(self):
        \"\"\"Test maximum retry limit is respected\"\"\"
        # TODO: Test max retries
        pass
"""
    
    def _generate_degradation_tests(self) -> str:
        """Generate graceful degradation tests"""
        return """

class TestGracefulDegradation:
    \"\"\"Tests for graceful degradation\"\"\"
    
    def test_graceful_degradation_on_error(self):
        \"\"\"Test system degrades gracefully on errors\"\"\"
        # TODO: Test graceful degradation
        pass
    
    def test_partial_functionality_maintained(self):
        \"\"\"Test partial functionality is maintained during failures\"\"\"
        # TODO: Test partial functionality
        pass
"""
    
    def _generate_input_validation_tests(self) -> str:
        """Generate input validation tests"""
        return """

class TestInputValidation:
    \"\"\"Tests for input validation\"\"\"
    
    def test_empty_input_handling(self):
        \"\"\"Test handling of empty inputs\"\"\"
        # TODO: Test empty input handling
        pass
    
    def test_malformed_input_handling(self):
        \"\"\"Test handling of malformed inputs\"\"\"
        # TODO: Test malformed input handling
        pass
    
    def test_boundary_values(self):
        \"\"\"Test boundary value handling\"\"\"
        # TODO: Test boundary values
        pass
"""
    
    def _generate_integration_tests(self, output_path: Path) -> str:
        """Generate integration tests for APIs"""
        test_file = output_path / "test_integration.py"
        
        content = self._get_test_file_header('python')
        content += "\n\n# Integration Tests\n"
        content += """
class TestIntegration:
    \"\"\"End-to-end integration tests\"\"\"
    
    @pytest.fixture(scope="session")
    def app_client(self):
        \"\"\"Create test client for the application\"\"\"
        # TODO: Set up test client (Flask: app.test_client(), FastAPI: TestClient(app))
        pass
    
    def test_api_workflow(self, app_client):
        \"\"\"Test complete API workflow\"\"\"
        # TODO: Test a complete user workflow across multiple endpoints
        pass
    
    def test_database_integration(self):
        \"\"\"Test database operations\"\"\"
        # TODO: Test database connections and operations
        pass
    
    def test_external_services(self):
        \"\"\"Test external service integrations\"\"\"
        # TODO: Test third-party API integrations
        pass
"""
        
        with open(test_file, 'w') as f:
            f.write(content)
        
        return str(test_file)
    
    def _generate_test_runner(self, output_path: Path) -> str:
        """Generate a test runner script"""
        if self.test_framework == 'pytest':
            runner_file = output_path / "run_tests.py"
            content = f"""#!/usr/bin/env python3
\"\"\"
Test Runner Script
Generated by Universal Testing Agent
\"\"\"

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    \"\"\"Run all tests with appropriate configurations\"\"\"
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(project_root)
    
    # Basic pytest command
    cmd = [
        'python', '-m', 'pytest',
        str(test_dir),
        '-v',
        '--tb=short'
    ]
    
    # Add coverage if requested
    coverage_target = {self.requirements.get('coverage_target', 80)}
    if coverage_target > 0:
        cmd.extend([
            '--cov=' + str(project_root),
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            f'--cov-fail-under={coverage_target}'
        ])
    
    print("🧪 Running tests with command:")
    print(" ".join(cmd))
    print()
    
    # Run tests
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print("\\n✅ All tests passed!")
        if coverage_target > 0:
            print(f"📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\\n❌ Some tests failed!")
        sys.exit(result.returncode)

if __name__ == '__main__':
    run_tests()
"""
        else:
            runner_file = output_path / "run_tests.js"
            content = """#!/usr/bin/env node
/**
 * Test Runner Script
 * Generated by Universal Testing Agent
 */

const { spawn } = require('child_process');
const path = require('path');

function runTests() {
    const testDir = __dirname;
    const projectRoot = path.dirname(testDir);
    
    // Jest command
    const cmd = 'npx';
    const args = ['jest', '--verbose', '--coverage'];
    
    console.log('🧪 Running tests with command:');
    console.log(`${cmd} ${args.join(' ')}`);
    console.log();
    
    const test = spawn(cmd, args, {
        cwd: projectRoot,
        stdio: 'inherit'
    });
    
    test.on('close', (code) => {
        if (code === 0) {
            console.log('\\n✅ All tests passed!');
            console.log('📊 Coverage report generated in coverage/');
        } else {
            console.log('\\n❌ Some tests failed!');
            process.exit(code);
        }
    });
}

runTests();
"""
        
        with open(runner_file, 'w') as f:
            f.write(content)
        
        # Make executable
        try:
            os.chmod(runner_file, 0o755)
        except:
            pass  # Windows doesn't need this
        
        return str(runner_file)


def main():
    """Main entry point for the testing agent"""
    parser = argparse.ArgumentParser(description='Universal Testing Agent')
    parser.add_argument('project_path', help='Path to project to analyze')
    parser.add_argument('--output', '-o', default='./tests', help='Output directory for tests')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run interactive questionnaire')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze project, don\'t generate tests')
    
    args = parser.parse_args()
    
    # Analyze project
    print("🚀 Starting Universal Testing Agent")
    analyzer = ProjectAnalyzer(args.project_path)
    analysis = analyzer.analyze()
    
    print(f"\n📊 ANALYSIS RESULTS")
    print(f"Functions found: {len(analysis['functions'])}")
    print(f"Classes found: {len(analysis['classes'])}")
    print(f"APIs found: {len(analysis['apis'])}")
    print(f"Framework detected: {analysis['framework']}")
    print(f"Project type: {analysis['project_type']}")
    
    if args.analyze_only:
        # Save analysis to file
        analysis_file = Path(args.output) / 'project_analysis.json'
        analysis_file.parent.mkdir(exist_ok=True)
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\n📄 Analysis saved to: {analysis_file}")
        return
    
    # Interactive questionnaire
    requirements = {}
    if args.interactive:
        questionnaire = InteractiveQuestionnaire(analysis)
        requirements = questionnaire.ask_questions()
    else:
        # Use default requirements
        requirements = {
            'test_framework': 'pytest',
            'coverage_target': 80,
            'include_integration': True,
            'null_handling': 'raise_exception',
            'error_logging': True,
            'graceful_degradation': True
        }
    
    # Generate tests
    print(f"\n🔨 GENERATING TESTS")
    generator = TestGenerator(analysis, requirements)
    generated_files = generator.generate_tests(args.output)
    
    print(f"\n✅ TEST GENERATION COMPLETE")
    print(f"Generated {len(generated_files)} test files:")
    for file_path in generated_files:
        print(f"  📄 {file_path}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Review generated tests and fill in TODO sections")
    print(f"2. Install test framework: pip install {requirements['test_framework']}")
    print(f"3. Run tests: {requirements['test_framework']} {args.output}")
    print(f"4. Customize tests based on your specific requirements")


if __name__ == '__main__':
    main()