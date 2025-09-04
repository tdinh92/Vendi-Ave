#!/usr/bin/env python3
"""
Architecture Analysis Agent - Pre-Testing Code Architecture Assessment
Analyzes code architecture, design patterns, dependencies, and potential issues
Provides recommendations before unit testing begins
"""

import os
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import argparse
from collections import defaultdict, Counter
import subprocess

class ArchitectureAnalyzer:
    """Analyzes project architecture and design patterns"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.files_analyzed = []
        self.dependencies = defaultdict(set)
        self.classes = []
        self.functions = []
        self.imports = defaultdict(list)
        self.design_patterns = []
        self.code_smells = []
        self.complexity_metrics = {}
        self.security_issues = []
        self.performance_concerns = []
    
    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive architecture analysis"""
        print(f"🏗️ Analyzing architecture: {self.project_path}")
        
        # Analyze all source files
        self._scan_source_files()
        
        # Analyze dependencies and imports
        self._analyze_dependencies()
        
        # Detect design patterns
        self._detect_design_patterns()
        
        # Identify code smells
        self._detect_code_smells()
        
        # Calculate complexity metrics
        self._calculate_complexity()
        
        # Security analysis
        self._security_analysis()
        
        # Performance analysis
        self._performance_analysis()
        
        # Generate architecture recommendations
        recommendations = self._generate_recommendations()
        
        return {
            'files_analyzed': len(self.files_analyzed),
            'total_classes': len(self.classes),
            'total_functions': len(self.functions),
            'dependencies': dict(self.dependencies),
            'design_patterns': self.design_patterns,
            'code_smells': self.code_smells,
            'complexity_metrics': self.complexity_metrics,
            'security_issues': self.security_issues,
            'performance_concerns': self.performance_concerns,
            'recommendations': recommendations,
            'architecture_score': self._calculate_architecture_score()
        }
    
    def _scan_source_files(self):
        """Scan and analyze all source files"""
        patterns = ['**/*.py', '**/*.js', '**/*.ts', '**/*.jsx', '**/*.tsx']
        
        for pattern in patterns:
            for file_path in self.project_path.rglob(pattern):
                if self._should_analyze_file(file_path):
                    self.files_analyzed.append(str(file_path.relative_to(self.project_path)))
                    
                    if file_path.suffix == '.py':
                        self._analyze_python_file(file_path)
                    elif file_path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                        self._analyze_javascript_file(file_path)
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Check if file should be analyzed"""
        skip_dirs = {'__pycache__', '.git', 'node_modules', 'venv', 'env', 'build', 'dist', '.pytest_cache'}
        skip_files = {'__init__.py'}
        
        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            return False
        if file_path.name in skip_files or file_path.name.startswith('.'):
            return False
        return True
    
    def _analyze_python_file(self, file_path: Path):
        """Analyze Python file for architecture patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Analyze classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._analyze_class(node, file_path, content)
                elif isinstance(node, ast.FunctionDef):
                    self._analyze_function(node, file_path, content)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    self._analyze_import(node, file_path)
                    
        except Exception as e:
            print(f"⚠️ Could not analyze {file_path}: {e}")
    
    def _analyze_class(self, node: ast.ClassDef, file_path: Path, content: str):
        """Analyze class for architecture patterns"""
        class_info = {
            'name': node.name,
            'file': str(file_path.relative_to(self.project_path)),
            'line': node.lineno,
            'methods': [],
            'properties': [],
            'base_classes': [self._get_name(base) for base in node.bases],
            'decorators': [self._get_name(dec) for dec in node.decorator_list],
            'complexity': self._calculate_class_complexity(node),
            'responsibilities': self._analyze_class_responsibilities(node, content)
        }
        
        # Analyze methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    'name': item.name,
                    'line': item.lineno,
                    'is_private': item.name.startswith('_'),
                    'is_property': any(self._get_name(d) == 'property' for d in item.decorator_list),
                    'complexity': self._calculate_function_complexity(item),
                    'parameters': len(item.args.args)
                }
                class_info['methods'].append(method_info)
        
        self.classes.append(class_info)
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path, content: str):
        """Analyze function for architecture patterns"""
        function_info = {
            'name': node.name,
            'file': str(file_path.relative_to(self.project_path)),
            'line': node.lineno,
            'parameters': len(node.args.args),
            'complexity': self._calculate_function_complexity(node),
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'decorators': [self._get_name(dec) for dec in node.decorator_list],
            'returns_value': self._has_return_value(node)
        }
        
        self.functions.append(function_info)
    
    def _analyze_import(self, node: ast.AST, file_path: Path):
        """Analyze imports for dependency analysis"""
        file_key = str(file_path.relative_to(self.project_path))
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.imports[file_key].append(alias.name)
                self.dependencies[file_key].add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                full_import = f"{module}.{alias.name}" if module else alias.name
                self.imports[file_key].append(full_import)
                self.dependencies[file_key].add(module if module else alias.name)
    
    def _analyze_javascript_file(self, file_path: Path):
        """Analyze JavaScript/TypeScript files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Analyze imports/requires
            import_patterns = [
                r'import\s+.*?\s+from\s+["\']([^"\']+)["\']',
                r'require\(["\']([^"\']+)["\']\)',
                r'import\s*\(\s*["\']([^"\']+)["\']\s*\)'
            ]
            
            file_key = str(file_path.relative_to(self.project_path))
            for pattern in import_patterns:
                for match in re.finditer(pattern, content):
                    dependency = match.group(1)
                    self.imports[file_key].append(dependency)
                    self.dependencies[file_key].add(dependency)
            
            # Analyze classes and functions (basic regex analysis)
            self._analyze_js_patterns(content, file_path)
                    
        except Exception as e:
            print(f"⚠️ Could not analyze {file_path}: {e}")
    
    def _analyze_js_patterns(self, content: str, file_path: Path):
        """Analyze JavaScript patterns using regex"""
        # Class pattern
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            extends = match.group(2)
            
            self.classes.append({
                'name': class_name,
                'file': str(file_path.relative_to(self.project_path)),
                'base_classes': [extends] if extends else [],
                'language': 'javascript'
            })
        
        # Function patterns
        function_patterns = [
            r'function\s+(\w+)',
            r'const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',
            r'(\w+)\s*:\s*(?:async\s+)?function'
        ]
        
        for pattern in function_patterns:
            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                self.functions.append({
                    'name': func_name,
                    'file': str(file_path.relative_to(self.project_path)),
                    'language': 'javascript',
                    'is_async': 'async' in match.group(0)
                })
    
    def _detect_design_patterns(self):
        """Detect common design patterns"""
        # Singleton pattern
        self._detect_singleton_pattern()
        
        # Factory pattern
        self._detect_factory_pattern()
        
        # Observer pattern
        self._detect_observer_pattern()
        
        # Repository pattern
        self._detect_repository_pattern()
        
        # MVC pattern
        self._detect_mvc_pattern()
        
        # Decorator pattern
        self._detect_decorator_pattern()
    
    def _detect_singleton_pattern(self):
        """Detect Singleton pattern implementations"""
        for cls in self.classes:
            # Look for __new__ method or instance variable patterns
            method_names = [m['name'] for m in cls.get('methods', [])]
            if '__new__' in method_names or any('instance' in m['name'].lower() for m in cls.get('methods', [])):
                self.design_patterns.append({
                    'pattern': 'Singleton',
                    'location': f"{cls['file']}:{cls['line']}",
                    'class': cls['name'],
                    'confidence': 'medium'
                })
    
    def _detect_factory_pattern(self):
        """Detect Factory pattern implementations"""
        for cls in self.classes:
            class_name = cls['name'].lower()
            if 'factory' in class_name or 'builder' in class_name:
                self.design_patterns.append({
                    'pattern': 'Factory',
                    'location': f"{cls['file']}:{cls['line']}",
                    'class': cls['name'],
                    'confidence': 'high'
                })
    
    def _detect_observer_pattern(self):
        """Detect Observer pattern implementations"""
        observer_indicators = ['notify', 'subscribe', 'unsubscribe', 'observer', 'listener']
        
        for cls in self.classes:
            method_names = [m['name'].lower() for m in cls.get('methods', [])]
            if any(indicator in ' '.join(method_names) for indicator in observer_indicators):
                self.design_patterns.append({
                    'pattern': 'Observer',
                    'location': f"{cls['file']}:{cls['line']}",
                    'class': cls['name'],
                    'confidence': 'medium'
                })
    
    def _detect_repository_pattern(self):
        """Detect Repository pattern implementations"""
        for cls in self.classes:
            class_name = cls['name'].lower()
            if 'repository' in class_name or 'repo' in class_name:
                self.design_patterns.append({
                    'pattern': 'Repository',
                    'location': f"{cls['file']}:{cls['line']}",
                    'class': cls['name'],
                    'confidence': 'high'
                })
    
    def _detect_mvc_pattern(self):
        """Detect MVC pattern implementation"""
        controllers = [cls for cls in self.classes if 'controller' in cls['name'].lower()]
        models = [cls for cls in self.classes if 'model' in cls['name'].lower()]
        views = [cls for cls in self.classes if 'view' in cls['name'].lower()]
        
        if controllers and models:
            self.design_patterns.append({
                'pattern': 'MVC',
                'location': 'Multiple files',
                'components': {
                    'controllers': len(controllers),
                    'models': len(models),
                    'views': len(views)
                },
                'confidence': 'high' if views else 'medium'
            })
    
    def _detect_decorator_pattern(self):
        """Detect Decorator pattern usage"""
        decorated_functions = [f for f in self.functions if f.get('decorators')]
        decorated_classes = [c for c in self.classes if c.get('decorators')]
        
        if decorated_functions or decorated_classes:
            self.design_patterns.append({
                'pattern': 'Decorator',
                'location': 'Multiple locations',
                'usage': {
                    'decorated_functions': len(decorated_functions),
                    'decorated_classes': len(decorated_classes)
                },
                'confidence': 'high'
            })
    
    def _detect_code_smells(self):
        """Detect various code smells"""
        # Long methods
        self._detect_long_methods()
        
        # Large classes
        self._detect_large_classes()
        
        # High complexity
        self._detect_high_complexity()
        
        # Duplicate code (basic detection)
        self._detect_potential_duplicates()
        
        # Circular dependencies
        self._detect_circular_dependencies()
    
    def _detect_long_methods(self):
        """Detect methods that are too long"""
        for func in self.functions:
            complexity = func.get('complexity', 0)
            if complexity > 15:  # Arbitrary threshold
                self.code_smells.append({
                    'type': 'Long Method',
                    'location': f"{func['file']}:{func['line']}",
                    'function': func['name'],
                    'complexity': complexity,
                    'severity': 'high' if complexity > 25 else 'medium'
                })
    
    def _detect_large_classes(self):
        """Detect classes that are too large"""
        for cls in self.classes:
            method_count = len(cls.get('methods', []))
            if method_count > 20:  # Arbitrary threshold
                self.code_smells.append({
                    'type': 'Large Class',
                    'location': f"{cls['file']}:{cls['line']}",
                    'class': cls['name'],
                    'method_count': method_count,
                    'severity': 'high' if method_count > 30 else 'medium'
                })
    
    def _detect_high_complexity(self):
        """Detect high complexity functions"""
        for cls in self.classes:
            complexity = cls.get('complexity', 0)
            if complexity > 20:
                self.code_smells.append({
                    'type': 'High Complexity Class',
                    'location': f"{cls['file']}:{cls['line']}",
                    'class': cls['name'],
                    'complexity': complexity,
                    'severity': 'high'
                })
    
    def _detect_potential_duplicates(self):
        """Detect potential code duplication"""
        function_names = [f['name'] for f in self.functions]
        name_counts = Counter(function_names)
        
        for name, count in name_counts.items():
            if count > 1:
                self.code_smells.append({
                    'type': 'Potential Duplicate',
                    'function_name': name,
                    'occurrences': count,
                    'severity': 'medium'
                })
    
    def _detect_circular_dependencies(self):
        """Detect circular dependencies between files"""
        # Simple circular dependency detection
        for file_a, deps_a in self.dependencies.items():
            for dep in deps_a:
                if dep in self.dependencies and file_a in self.dependencies[dep]:
                    self.code_smells.append({
                        'type': 'Circular Dependency',
                        'files': [file_a, dep],
                        'severity': 'high'
                    })
    
    def _security_analysis(self):
        """Perform basic security analysis"""
        security_patterns = {
            'SQL Injection': [r'SELECT.*\+.*', r'INSERT.*\+.*', r'UPDATE.*\+.*'],
            'Hard-coded Secrets': [r'password\s*=\s*["\'][^"\']+["\']', r'api_key\s*=\s*["\'][^"\']+["\']'],
            'Dangerous Functions': [r'eval\(', r'exec\(', r'subprocess\.call\(.*shell=True'],
            'Weak Crypto': [r'md5\(', r'sha1\(']
        }
        
        for file_path in self.files_analyzed:
            full_path = self.project_path / file_path
            if full_path.suffix == '.py':
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for issue_type, patterns in security_patterns.items():
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                self.security_issues.append({
                                    'type': issue_type,
                                    'file': file_path,
                                    'pattern': pattern,
                                    'severity': 'high' if issue_type in ['SQL Injection', 'Hard-coded Secrets'] else 'medium'
                                })
                except Exception:
                    continue
    
    def _performance_analysis(self):
        """Analyze for potential performance issues"""
        performance_patterns = {
            'N+1 Queries': [r'for.*in.*:\s*.*query', r'for.*in.*:\s*.*find'],
            'Inefficient Loops': [r'for.*in.*:\s*.*append'],
            'Large Data Loading': [r'\.read\(\)', r'load.*all']
        }
        
        for file_path in self.files_analyzed:
            full_path = self.project_path / file_path
            if full_path.suffix == '.py':
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for issue_type, patterns in performance_patterns.items():
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                self.performance_concerns.append({
                                    'type': issue_type,
                                    'file': file_path,
                                    'pattern': pattern,
                                    'severity': 'medium'
                                })
                except Exception:
                    continue
    
    def _calculate_complexity(self):
        """Calculate various complexity metrics"""
        if self.classes:
            avg_methods_per_class = sum(len(cls.get('methods', [])) for cls in self.classes) / len(self.classes)
            max_methods_per_class = max(len(cls.get('methods', [])) for cls in self.classes)
        else:
            avg_methods_per_class = 0
            max_methods_per_class = 0
        
        if self.functions:
            avg_params_per_function = sum(f.get('parameters', 0) for f in self.functions) / len(self.functions)
            max_params_per_function = max(f.get('parameters', 0) for f in self.functions)
        else:
            avg_params_per_function = 0
            max_params_per_function = 0
        
        self.complexity_metrics = {
            'total_files': len(self.files_analyzed),
            'total_classes': len(self.classes),
            'total_functions': len(self.functions),
            'avg_methods_per_class': round(avg_methods_per_class, 2),
            'max_methods_per_class': max_methods_per_class,
            'avg_params_per_function': round(avg_params_per_function, 2),
            'max_params_per_function': max_params_per_function,
            'dependency_count': sum(len(deps) for deps in self.dependencies.values()),
            'avg_dependencies_per_file': round(sum(len(deps) for deps in self.dependencies.values()) / max(len(self.dependencies), 1), 2)
        }
    
    def _generate_recommendations(self):
        """Generate architecture improvement recommendations"""
        recommendations = []
        
        # Based on code smells
        if any(smell['type'] == 'Long Method' for smell in self.code_smells):
            recommendations.append({
                'category': 'Code Structure',
                'issue': 'Long Methods Detected',
                'recommendation': 'Consider breaking long methods into smaller, more focused functions',
                'priority': 'high',
                'testing_impact': 'Makes unit testing more difficult - smaller functions are easier to test'
            })
        
        if any(smell['type'] == 'Large Class' for smell in self.code_smells):
            recommendations.append({
                'category': 'Class Design',
                'issue': 'Large Classes Detected',
                'recommendation': 'Consider applying Single Responsibility Principle - break large classes into smaller ones',
                'priority': 'high',
                'testing_impact': 'Large classes require more complex test setups and are harder to mock'
            })
        
        if any(smell['type'] == 'Circular Dependency' for smell in self.code_smells):
            recommendations.append({
                'category': 'Dependencies',
                'issue': 'Circular Dependencies Found',
                'recommendation': 'Refactor to eliminate circular dependencies using dependency injection or interfaces',
                'priority': 'critical',
                'testing_impact': 'Circular dependencies make it very difficult to test components in isolation'
            })
        
        # Based on design patterns
        if not any(pattern['pattern'] == 'Repository' for pattern in self.design_patterns):
            if any('database' in str(deps).lower() or 'db' in str(deps).lower() for deps in self.dependencies.values()):
                recommendations.append({
                    'category': 'Data Access',
                    'issue': 'Direct Database Access',
                    'recommendation': 'Consider implementing Repository pattern for better testability',
                    'priority': 'medium',
                    'testing_impact': 'Repository pattern makes database code much easier to mock and test'
                })
        
        # Based on security issues
        if self.security_issues:
            recommendations.append({
                'category': 'Security',
                'issue': f'{len(self.security_issues)} Security Issues Found',
                'recommendation': 'Address security vulnerabilities before deploying to production',
                'priority': 'critical',
                'testing_impact': 'Security tests should be added to prevent regressions'
            })
        
        # Based on complexity
        if self.complexity_metrics.get('avg_methods_per_class', 0) > 15:
            recommendations.append({
                'category': 'Complexity',
                'issue': 'High Average Class Complexity',
                'recommendation': 'Consider refactoring complex classes to improve maintainability',
                'priority': 'medium',
                'testing_impact': 'Complex classes require more comprehensive test coverage'
            })
        
        return recommendations
    
    def _calculate_architecture_score(self) -> Dict[str, Any]:
        """Calculate an overall architecture quality score"""
        score = 100
        
        # Deduct points for code smells
        high_severity_smells = [s for s in self.code_smells if s.get('severity') == 'high']
        medium_severity_smells = [s for s in self.code_smells if s.get('severity') == 'medium']
        
        score -= len(high_severity_smells) * 10
        score -= len(medium_severity_smells) * 5
        
        # Deduct points for security issues
        score -= len(self.security_issues) * 15
        
        # Deduct points for high complexity
        if self.complexity_metrics.get('max_methods_per_class', 0) > 30:
            score -= 20
        if self.complexity_metrics.get('max_params_per_function', 0) > 8:
            score -= 10
        
        # Add points for good patterns
        score += len(self.design_patterns) * 5
        
        # Ensure score stays within bounds
        score = max(0, min(100, score))
        
        # Determine grade
        if score >= 90:
            grade = 'A'
        elif score >= 80:
            grade = 'B'
        elif score >= 70:
            grade = 'C'
        elif score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'score': score,
            'grade': grade,
            'testability': 'Excellent' if score >= 85 else 'Good' if score >= 70 else 'Fair' if score >= 55 else 'Poor'
        }
    
    # Helper methods
    def _get_name(self, node) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, str):
            return node
        return str(node)
    
    def _calculate_class_complexity(self, node: ast.ClassDef) -> int:
        """Calculate complexity of a class"""
        complexity = len(node.body)
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                complexity += self._calculate_function_complexity(item)
        return complexity
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _analyze_class_responsibilities(self, node: ast.ClassDef, content: str) -> List[str]:
        """Analyze what responsibilities a class has"""
        responsibilities = []
        method_names = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
        
        # Data access responsibility
        if any(name in ['save', 'load', 'find', 'query', 'insert', 'update', 'delete'] for name in method_names):
            responsibilities.append('Data Access')
        
        # Business logic responsibility
        if any(name in ['calculate', 'process', 'validate', 'transform'] for name in method_names):
            responsibilities.append('Business Logic')
        
        # Presentation responsibility
        if any(name in ['render', 'display', 'format', 'serialize'] for name in method_names):
            responsibilities.append('Presentation')
        
        # Communication responsibility
        if any(name in ['send', 'receive', 'notify', 'publish'] for name in method_names):
            responsibilities.append('Communication')
        
        return responsibilities
    
    def _has_return_value(self, node: ast.FunctionDef) -> bool:
        """Check if function has explicit return values"""
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value is not None:
                return True
        return False


def generate_architecture_report(analysis: Dict[str, Any], output_file: str = None):
    """Generate a comprehensive architecture report"""
    
    report = []
    report.append("🏗️ ARCHITECTURE ANALYSIS REPORT")
    report.append("=" * 50)
    report.append("")
    
    # Summary
    report.append("📊 SUMMARY")
    report.append("-" * 20)
    report.append(f"Files Analyzed: {analysis['files_analyzed']}")
    report.append(f"Classes: {analysis['total_classes']}")
    report.append(f"Functions: {analysis['total_functions']}")
    report.append(f"Architecture Score: {analysis['architecture_score']['score']}/100 (Grade: {analysis['architecture_score']['grade']})")
    report.append(f"Testability: {analysis['architecture_score']['testability']}")
    report.append("")
    
    # Design patterns
    if analysis['design_patterns']:
        report.append("🎨 DESIGN PATTERNS DETECTED")
        report.append("-" * 30)
        for pattern in analysis['design_patterns']:
            report.append(f"✓ {pattern['pattern']} - {pattern.get('location', 'N/A')} (Confidence: {pattern.get('confidence', 'unknown')})")
        report.append("")
    
    # Code smells
    if analysis['code_smells']:
        report.append("⚠️ CODE SMELLS DETECTED")
        report.append("-" * 25)
        for smell in analysis['code_smells']:
            severity_emoji = "🔴" if smell.get('severity') == 'high' else "🟡" if smell.get('severity') == 'medium' else "🟢"
            report.append(f"{severity_emoji} {smell['type']} - {smell.get('location', 'N/A')}")
        report.append("")
    
    # Security issues
    if analysis['security_issues']:
        report.append("🔒 SECURITY CONCERNS")
        report.append("-" * 20)
        for issue in analysis['security_issues']:
            report.append(f"🚨 {issue['type']} in {issue['file']}")
        report.append("")
    
    # Performance concerns
    if analysis['performance_concerns']:
        report.append("⚡ PERFORMANCE CONCERNS")
        report.append("-" * 25)
        for concern in analysis['performance_concerns']:
            report.append(f"⚠️ {concern['type']} in {concern['file']}")
        report.append("")
    
    # Complexity metrics
    report.append("📈 COMPLEXITY METRICS")
    report.append("-" * 22)
    metrics = analysis['complexity_metrics']
    report.append(f"Average Methods per Class: {metrics.get('avg_methods_per_class', 0)}")
    report.append(f"Max Methods per Class: {metrics.get('max_methods_per_class', 0)}")
    report.append(f"Average Parameters per Function: {metrics.get('avg_params_per_function', 0)}")
    report.append(f"Max Parameters per Function: {metrics.get('max_params_per_function', 0)}")
    report.append(f"Average Dependencies per File: {metrics.get('avg_dependencies_per_file', 0)}")
    report.append("")
    
    # Recommendations
    if analysis['recommendations']:
        report.append("🎯 RECOMMENDATIONS")
        report.append("-" * 18)
        for rec in analysis['recommendations']:
            priority_emoji = "🔴" if rec['priority'] == 'critical' else "🟡" if rec['priority'] == 'high' else "🟢"
            report.append(f"{priority_emoji} {rec['category']}: {rec['issue']}")
            report.append(f"   💡 {rec['recommendation']}")
            if 'testing_impact' in rec:
                report.append(f"   🧪 Testing Impact: {rec['testing_impact']}")
            report.append("")
    
    report_text = "\n".join(report)
    
    # Print to console
    print(report_text)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_text)
        print(f"📄 Report saved to: {output_file}")
    
    return report_text


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Architecture Analysis Agent')
    parser.add_argument('project_path', help='Path to project to analyze')
    parser.add_argument('--output', '-o', help='Output file for report')
    parser.add_argument('--json', action='store_true', help='Output raw JSON analysis')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.project_path):
        print(f"❌ Project path does not exist: {args.project_path}")
        sys.exit(1)
    
    # Run analysis
    analyzer = ArchitectureAnalyzer(args.project_path)
    analysis = analyzer.analyze()
    
    if args.json:
        # Output raw JSON
        output_file = args.output or 'architecture_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"📄 JSON analysis saved to: {output_file}")
    else:
        # Generate formatted report
        generate_architecture_report(analysis, args.output)


if __name__ == '__main__':
    main()