#!/usr/bin/env python3
"""
Deployment & DevOps Agent
Specialized agent for managing deployments, environment setup, and DevOps workflows
Designed for Python Flask APIs, containerization, and cloud deployment
"""

import os
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil
import tempfile


class DeploymentAgent:
    """Agent for comprehensive deployment and DevOps automation"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.deployment_config = {}
        self.supported_platforms = ['docker', 'heroku', 'aws', 'gcp', 'azure']
        
    def analyze_project_for_deployment(self) -> Dict[str, Any]:
        """Analyze project structure and recommend deployment strategy"""
        print(f"🔍 Analyzing project for deployment readiness...")
        print(f"📁 Project path: {self.project_path}")
        
        analysis = {
            'project_info': self._analyze_project_structure(),
            'dependency_analysis': self._analyze_dependencies(),
            'configuration_analysis': self._analyze_configuration(),
            'deployment_readiness': {},
            'recommendations': []
        }
        
        # Check deployment readiness for different platforms
        analysis['deployment_readiness'] = {
            'docker': self._check_docker_readiness(analysis),
            'heroku': self._check_heroku_readiness(analysis),
            'cloud': self._check_cloud_readiness(analysis)
        }
        
        # Generate deployment recommendations
        analysis['recommendations'] = self._generate_deployment_recommendations(analysis)
        
        return analysis
    
    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project file structure"""
        structure = {
            'main_files': [],
            'config_files': [],
            'static_assets': [],
            'templates': [],
            'tests': [],
            'documentation': []
        }
        
        # Check for main application files
        for pattern in ['*.py', 'app.py', 'main.py', 'server.py', 'wsgi.py']:
            matches = list(self.project_path.glob(pattern))
            structure['main_files'].extend([str(f.relative_to(self.project_path)) for f in matches])
        
        # Check for configuration files
        config_patterns = ['requirements.txt', 'Pipfile', 'pyproject.toml', '*.env', '.env*', 'config.py']
        for pattern in config_patterns:
            matches = list(self.project_path.glob(pattern))
            structure['config_files'].extend([str(f.relative_to(self.project_path)) for f in matches])
        
        # Check for static assets and templates
        if (self.project_path / 'static').exists():
            structure['static_assets'] = [str(f.relative_to(self.project_path)) 
                                        for f in (self.project_path / 'static').rglob('*') if f.is_file()]
        
        if (self.project_path / 'templates').exists():
            structure['templates'] = [str(f.relative_to(self.project_path)) 
                                    for f in (self.project_path / 'templates').rglob('*') if f.is_file()]
        
        # Check for tests
        test_dirs = ['tests', 'test']
        for test_dir in test_dirs:
            if (self.project_path / test_dir).exists():
                structure['tests'] = [str(f.relative_to(self.project_path)) 
                                    for f in (self.project_path / test_dir).rglob('*.py')]
        
        # Check for documentation
        doc_patterns = ['README*', '*.md', 'docs/', 'CHANGELOG*', 'LICENSE*']
        for pattern in doc_patterns:
            matches = list(self.project_path.glob(pattern))
            structure['documentation'].extend([str(f.relative_to(self.project_path)) for f in matches])
        
        return structure
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies"""
        deps = {
            'requirements_files': [],
            'python_dependencies': [],
            'system_dependencies': [],
            'dependency_issues': []
        }
        
        # Check requirements.txt
        req_file = self.project_path / 'requirements.txt'
        if req_file.exists():
            deps['requirements_files'].append('requirements.txt')
            try:
                with open(req_file, 'r') as f:
                    deps['python_dependencies'] = [line.strip() for line in f 
                                                 if line.strip() and not line.startswith('#')]
            except Exception as e:
                deps['dependency_issues'].append(f"Error reading requirements.txt: {e}")
        
        # Check for test requirements
        test_req_file = self.project_path / 'tests' / 'requirements-test.txt'
        if test_req_file.exists():
            deps['requirements_files'].append('tests/requirements-test.txt')
        
        # Analyze dependency types
        web_frameworks = ['flask', 'django', 'fastapi', 'tornado']
        database_deps = ['sqlite', 'mysql', 'postgresql', 'mongodb']
        cloud_deps = ['boto3', 'google-cloud', 'azure']
        
        deps['framework_type'] = 'unknown'
        for framework in web_frameworks:
            if any(framework in dep.lower() for dep in deps['python_dependencies']):
                deps['framework_type'] = framework
                break
        
        deps['has_database'] = any(db in dep.lower() 
                                 for dep in deps['python_dependencies'] 
                                 for db in database_deps)
        
        deps['has_cloud_deps'] = any(cloud in dep.lower() 
                                   for dep in deps['python_dependencies'] 
                                   for cloud in cloud_deps)
        
        return deps
    
    def _analyze_configuration(self) -> Dict[str, Any]:
        """Analyze project configuration"""
        config = {
            'environment_variables': [],
            'configuration_files': [],
            'secrets_detected': False,
            'port_configuration': None,
            'configuration_issues': []
        }
        
        # Check .env files
        env_files = list(self.project_path.glob('.env*'))
        for env_file in env_files:
            config['configuration_files'].append(str(env_file.relative_to(self.project_path)))
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            var_name = line.split('=')[0].strip()
                            config['environment_variables'].append(var_name)
                            
                            # Check for secrets
                            if any(secret_word in var_name.lower() 
                                 for secret_word in ['key', 'secret', 'password', 'token']):
                                config['secrets_detected'] = True
            except Exception as e:
                config['configuration_issues'].append(f"Error reading {env_file}: {e}")
        
        # Check for port configuration in main Python files
        for py_file in self.project_path.glob('*.py'):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if 'app.run(' in content or 'run(port=' in content:
                        # Try to extract port number
                        import re
                        port_match = re.search(r'port=(\d+)', content)
                        if port_match:
                            config['port_configuration'] = int(port_match.group(1))
                        else:
                            config['port_configuration'] = 5000  # Flask default
            except Exception as e:
                config['configuration_issues'].append(f"Error analyzing {py_file}: {e}")
        
        return config
    
    def _check_docker_readiness(self, analysis: Dict) -> Dict[str, Any]:
        """Check if project is ready for Docker deployment"""
        readiness = {
            'ready': False,
            'missing_components': [],
            'existing_components': [],
            'recommendations': []
        }
        
        # Check for existing Docker files
        docker_files = ['Dockerfile', 'docker-compose.yml', '.dockerignore']
        for docker_file in docker_files:
            if (self.project_path / docker_file).exists():
                readiness['existing_components'].append(docker_file)
            else:
                readiness['missing_components'].append(docker_file)
        
        # Check requirements
        if 'requirements.txt' not in analysis['project_info']['config_files']:
            readiness['missing_components'].append('requirements.txt')
            readiness['recommendations'].append('Create requirements.txt with all Python dependencies')
        
        # Check for main application file
        main_files = analysis['project_info']['main_files']
        if not main_files:
            readiness['missing_components'].append('main application file (app.py/main.py)')
            readiness['recommendations'].append('Ensure you have a main Python file to run the application')
        
        # Determine readiness
        critical_missing = ['requirements.txt'] if 'requirements.txt' not in analysis['project_info']['config_files'] else []
        critical_missing.extend(['main application file'] if not main_files else [])
        
        readiness['ready'] = len(critical_missing) == 0
        
        if readiness['ready']:
            readiness['recommendations'].append('Project is Docker-ready. Consider creating Dockerfile and docker-compose.yml')
        
        return readiness
    
    def _check_heroku_readiness(self, analysis: Dict) -> Dict[str, Any]:
        """Check if project is ready for Heroku deployment"""
        readiness = {
            'ready': False,
            'missing_components': [],
            'existing_components': [],
            'recommendations': []
        }
        
        # Check for Heroku-specific files
        heroku_files = ['Procfile', 'runtime.txt', 'app.json']
        for heroku_file in heroku_files:
            if (self.project_path / heroku_file).exists():
                readiness['existing_components'].append(heroku_file)
            else:
                readiness['missing_components'].append(heroku_file)
        
        # Check requirements
        if 'requirements.txt' not in analysis['project_info']['config_files']:
            readiness['missing_components'].append('requirements.txt')
        else:
            readiness['existing_components'].append('requirements.txt')
        
        # Check for WSGI server
        deps = analysis['dependency_analysis']['python_dependencies']
        has_wsgi_server = any(server in dep.lower() for dep in deps 
                            for server in ['gunicorn', 'waitress', 'uwsgi'])
        
        if not has_wsgi_server:
            readiness['missing_components'].append('WSGI server (gunicorn recommended)')
            readiness['recommendations'].append('Add gunicorn to requirements.txt for production deployment')
        
        # Check for environment variable handling
        env_vars = analysis['configuration_analysis']['environment_variables']
        if not env_vars:
            readiness['recommendations'].append('Consider using environment variables for configuration')
        
        # Determine readiness
        critical_missing = []
        if 'requirements.txt' not in analysis['project_info']['config_files']:
            critical_missing.append('requirements.txt')
        if 'Procfile' not in readiness['existing_components']:
            critical_missing.append('Procfile')
        if not has_wsgi_server:
            critical_missing.append('WSGI server')
        
        readiness['ready'] = len(critical_missing) == 0
        
        return readiness
    
    def _check_cloud_readiness(self, analysis: Dict) -> Dict[str, Any]:
        """Check if project is ready for cloud deployment (AWS/GCP/Azure)"""
        readiness = {
            'ready': False,
            'platforms': {
                'aws': {'ready': False, 'recommendations': []},
                'gcp': {'ready': False, 'recommendations': []},
                'azure': {'ready': False, 'recommendations': []}
            },
            'general_recommendations': []
        }
        
        # General cloud readiness checks
        has_requirements = 'requirements.txt' in analysis['project_info']['config_files']
        has_main_file = len(analysis['project_info']['main_files']) > 0
        has_env_config = len(analysis['configuration_analysis']['environment_variables']) > 0
        
        base_ready = has_requirements and has_main_file
        
        # AWS-specific checks
        aws_files = ['serverless.yml', 'template.yaml', 'sam-template.yaml']
        aws_deps = ['boto3', 'aws', 'lambda']
        has_aws_files = any((self.project_path / f).exists() for f in aws_files)
        has_aws_deps = any(dep in ' '.join(analysis['dependency_analysis']['python_dependencies']).lower() 
                          for dep in aws_deps)
        
        readiness['platforms']['aws']['ready'] = base_ready
        if not has_aws_files and not has_aws_deps:
            readiness['platforms']['aws']['recommendations'].extend([
                'Consider AWS Lambda for serverless deployment',
                'Add boto3 for AWS services integration',
                'Create serverless.yml for Serverless Framework deployment'
            ])
        
        # GCP-specific checks
        gcp_files = ['app.yaml', 'cloudbuild.yaml', 'kubernetes.yaml']
        gcp_deps = ['google-cloud', 'gcp']
        has_gcp_files = any((self.project_path / f).exists() for f in gcp_files)
        has_gcp_deps = any(dep in ' '.join(analysis['dependency_analysis']['python_dependencies']).lower() 
                          for dep in gcp_deps)
        
        readiness['platforms']['gcp']['ready'] = base_ready
        if not has_gcp_files:
            readiness['platforms']['gcp']['recommendations'].extend([
                'Consider Google App Engine with app.yaml',
                'Use Cloud Run for containerized deployment',
                'Add google-cloud SDK for GCP services'
            ])
        
        # Azure-specific checks
        azure_files = ['azure-pipelines.yml', 'azuredeploy.json']
        azure_deps = ['azure', 'msal']
        has_azure_files = any((self.project_path / f).exists() for f in azure_files)
        
        readiness['platforms']['azure']['ready'] = base_ready
        if not has_azure_files:
            readiness['platforms']['azure']['recommendations'].extend([
                'Consider Azure App Service for web app hosting',
                'Use Azure Functions for serverless deployment',
                'Add Azure SDK for Azure services integration'
            ])
        
        # General recommendations
        if not has_env_config:
            readiness['general_recommendations'].append('Use environment variables for cloud configuration')
        
        if analysis['dependency_analysis']['framework_type'] == 'flask':
            readiness['general_recommendations'].append('Consider using gunicorn as WSGI server for production')
        
        readiness['ready'] = any(platform['ready'] for platform in readiness['platforms'].values())
        
        return readiness
    
    def _generate_deployment_recommendations(self, analysis: Dict) -> List[str]:
        """Generate overall deployment recommendations"""
        recommendations = []
        
        # Framework-specific recommendations
        framework = analysis['dependency_analysis']['framework_type']
        if framework == 'flask':
            recommendations.append('Flask detected - consider using gunicorn for production WSGI server')
        elif framework == 'django':
            recommendations.append('Django detected - ensure static files are configured for production')
        elif framework == 'fastapi':
            recommendations.append('FastAPI detected - consider using uvicorn for ASGI server')
        
        # Database recommendations
        if analysis['dependency_analysis']['has_database']:
            recommendations.append('Database dependencies detected - ensure environment-based configuration')
        
        # Security recommendations
        if analysis['configuration_analysis']['secrets_detected']:
            recommendations.append('Secrets detected in configuration - use secure environment variable management')
        
        # Deployment platform recommendations
        docker_ready = analysis['deployment_readiness']['docker']['ready']
        heroku_ready = analysis['deployment_readiness']['heroku']['ready']
        cloud_ready = analysis['deployment_readiness']['cloud']['ready']
        
        if docker_ready:
            recommendations.append('Docker deployment recommended - containerization provides consistency across environments')
        
        if heroku_ready:
            recommendations.append('Heroku deployment ready - good for rapid prototyping and small applications')
        
        if cloud_ready:
            recommendations.append('Cloud deployment ready - consider AWS/GCP/Azure for scalable production deployment')
        
        # Testing recommendations
        if analysis['project_info']['tests']:
            recommendations.append('Tests detected - integrate with CI/CD pipeline for automated deployment')
        else:
            recommendations.append('Consider adding tests before production deployment')
        
        return recommendations
    
    def generate_dockerfile(self, python_version: str = "3.9", port: int = 5000) -> str:
        """Generate Dockerfile for the project"""
        dockerfile_content = f"""# Use official Python runtime as base image
FROM python:{python_version}-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    software-properties-common \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Run the application
CMD ["python", "property_rest_api.py"]
"""
        return dockerfile_content
    
    def generate_docker_compose(self, app_name: str = "avm-api", port: int = 5000) -> str:
        """Generate docker-compose.yml for the project"""
        compose_content = f"""version: '3.8'

services:
  {app_name}:
    build: .
    ports:
      - "{port}:{port}"
    environment:
      - FLASK_ENV=production
      - PYTHONPATH=/app
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{port}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - {app_name}-network

networks:
  {app_name}-network:
    driver: bridge

volumes:
  {app_name}-logs:
"""
        return compose_content
    
    def generate_procfile(self, main_file: str = "property_rest_api.py") -> str:
        """Generate Procfile for Heroku deployment"""
        return f"web: gunicorn {main_file.replace('.py', '')}:app --bind 0.0.0.0:$PORT\n"
    
    def generate_heroku_runtime(self, python_version: str = "3.9.18") -> str:
        """Generate runtime.txt for Heroku"""
        return f"python-{python_version}\n"
    
    def generate_dockerignore(self) -> str:
        """Generate .dockerignore file"""
        dockerignore_content = """# Git
.git
.gitignore
README.md

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.venv
venv/

# Testing
.pytest_cache
.coverage
htmlcov/
.tox/
.cache

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs
*.log
npm-debug.log*

# Deployment
.vercel
.serverless/
"""
        return dockerignore_content
    
    def create_deployment_files(self, platform: str, config: Dict[str, Any] = None) -> Dict[str, str]:
        """Create deployment files for specified platform"""
        if config is None:
            config = {}
        
        created_files = {}
        
        if platform == 'docker':
            # Create Dockerfile
            dockerfile_path = self.project_path / 'Dockerfile'
            if not dockerfile_path.exists():
                dockerfile_content = self.generate_dockerfile(
                    python_version=config.get('python_version', '3.9'),
                    port=config.get('port', 5000)
                )
                with open(dockerfile_path, 'w') as f:
                    f.write(dockerfile_content)
                created_files['Dockerfile'] = str(dockerfile_path)
            
            # Create docker-compose.yml
            compose_path = self.project_path / 'docker-compose.yml'
            if not compose_path.exists():
                compose_content = self.generate_docker_compose(
                    app_name=config.get('app_name', 'avm-api'),
                    port=config.get('port', 5000)
                )
                with open(compose_path, 'w') as f:
                    f.write(compose_content)
                created_files['docker-compose.yml'] = str(compose_path)
            
            # Create .dockerignore
            dockerignore_path = self.project_path / '.dockerignore'
            if not dockerignore_path.exists():
                dockerignore_content = self.generate_dockerignore()
                with open(dockerignore_path, 'w') as f:
                    f.write(dockerignore_content)
                created_files['.dockerignore'] = str(dockerignore_path)
        
        elif platform == 'heroku':
            # Create Procfile
            procfile_path = self.project_path / 'Procfile'
            if not procfile_path.exists():
                procfile_content = self.generate_procfile(config.get('main_file', 'property_rest_api.py'))
                with open(procfile_path, 'w') as f:
                    f.write(procfile_content)
                created_files['Procfile'] = str(procfile_path)
            
            # Create runtime.txt
            runtime_path = self.project_path / 'runtime.txt'
            if not runtime_path.exists():
                runtime_content = self.generate_heroku_runtime(config.get('python_version', '3.9.18'))
                with open(runtime_path, 'w') as f:
                    f.write(runtime_content)
                created_files['runtime.txt'] = str(runtime_path)
            
            # Update requirements.txt to include gunicorn if not present
            req_path = self.project_path / 'requirements.txt'
            if req_path.exists():
                with open(req_path, 'r') as f:
                    requirements = f.read()
                
                if 'gunicorn' not in requirements.lower():
                    with open(req_path, 'a') as f:
                        f.write('\ngunicorn>=20.0.0\n')
                    created_files['requirements.txt'] = 'Updated with gunicorn'
        
        return created_files
    
    def run_deployment_checks(self) -> Dict[str, Any]:
        """Run pre-deployment checks"""
        print("🔍 Running pre-deployment checks...")
        
        checks = {
            'security_checks': self._run_security_checks(),
            'dependency_checks': self._run_dependency_checks(),
            'configuration_checks': self._run_configuration_checks(),
            'test_checks': self._run_test_checks(),
            'overall_status': 'unknown'
        }
        
        # Determine overall status
        failed_checks = []
        for check_type, results in checks.items():
            if check_type != 'overall_status' and isinstance(results, dict):
                if results.get('status') == 'failed':
                    failed_checks.append(check_type)
        
        if not failed_checks:
            checks['overall_status'] = 'passed'
        elif len(failed_checks) <= 1:
            checks['overall_status'] = 'warning'
        else:
            checks['overall_status'] = 'failed'
        
        return checks
    
    def _run_security_checks(self) -> Dict[str, Any]:
        """Run security checks"""
        issues = []
        
        # Check for exposed secrets
        env_files = list(self.project_path.glob('.env*'))
        for env_file in env_files:
            if env_file.name == '.env':
                # Check if .env is in .gitignore
                gitignore_path = self.project_path / '.gitignore'
                if gitignore_path.exists():
                    with open(gitignore_path, 'r') as f:
                        gitignore_content = f.read()
                    if '.env' not in gitignore_content:
                        issues.append('.env file should be added to .gitignore')
                else:
                    issues.append('Create .gitignore file to exclude sensitive files')
        
        # Check for hardcoded secrets in code
        for py_file in self.project_path.glob('*.py'):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if any(pattern in content.lower() 
                          for pattern in ['api_key =', 'password =', 'secret =', 'token =']):
                        issues.append(f'Potential hardcoded secrets in {py_file.name}')
            except Exception:
                pass
        
        return {
            'status': 'failed' if issues else 'passed',
            'issues': issues,
            'recommendations': [
                'Use environment variables for all secrets',
                'Add sensitive files to .gitignore',
                'Consider using secret management services in production'
            ] if issues else []
        }
    
    def _run_dependency_checks(self) -> Dict[str, Any]:
        """Run dependency checks"""
        issues = []
        
        # Check if requirements.txt exists
        req_path = self.project_path / 'requirements.txt'
        if not req_path.exists():
            issues.append('requirements.txt file missing')
        else:
            # Check for potential security issues in dependencies
            try:
                with open(req_path, 'r') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                # Check for unpinned versions
                unpinned = [dep for dep in deps if '==' not in dep and '>=' not in dep and dep.strip()]
                if unpinned:
                    issues.append(f'Unpinned dependencies: {", ".join(unpinned)}')
                
            except Exception as e:
                issues.append(f'Error reading requirements.txt: {e}')
        
        return {
            'status': 'failed' if issues else 'passed',
            'issues': issues,
            'recommendations': [
                'Pin all dependency versions in requirements.txt',
                'Regularly update dependencies for security patches',
                'Consider using pip-audit for security scanning'
            ] if issues else []
        }
    
    def _run_configuration_checks(self) -> Dict[str, Any]:
        """Run configuration checks"""
        issues = []
        warnings = []
        
        # Check for environment-based configuration
        env_files = list(self.project_path.glob('.env*'))
        if not env_files:
            warnings.append('No environment configuration files found')
        
        # Check for production configuration
        config_files = ['config.py', 'settings.py']
        has_config = any((self.project_path / f).exists() for f in config_files)
        if not has_config:
            warnings.append('No dedicated configuration file found')
        
        # Check for debug mode in production
        for py_file in self.project_path.glob('*.py'):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if 'debug=True' in content or 'DEBUG = True' in content:
                        issues.append(f'Debug mode enabled in {py_file.name} - disable for production')
            except Exception:
                pass
        
        return {
            'status': 'failed' if issues else 'warning' if warnings else 'passed',
            'issues': issues,
            'warnings': warnings,
            'recommendations': [
                'Use environment variables for configuration',
                'Disable debug mode in production',
                'Create separate config files for different environments'
            ] if issues or warnings else []
        }
    
    def _run_test_checks(self) -> Dict[str, Any]:
        """Run test-related checks"""
        warnings = []
        
        # Check for test files
        test_files = list(self.project_path.glob('test*.py')) + list((self.project_path / 'tests').glob('*.py') if (self.project_path / 'tests').exists() else [])
        
        if not test_files:
            warnings.append('No test files found - consider adding tests before deployment')
        
        return {
            'status': 'warning' if warnings else 'passed',
            'warnings': warnings,
            'recommendations': [
                'Add comprehensive test suite',
                'Integrate tests with CI/CD pipeline',
                'Aim for at least 70% code coverage'
            ] if warnings else []
        }
    
    def export_deployment_plan(self, analysis_data: Dict, output_path: str = "deployment_plan.json"):
        """Export deployment analysis and plan to JSON"""
        analysis_data['export_timestamp'] = datetime.now().isoformat()
        analysis_data['agent_version'] = "1.0.0"
        
        with open(output_path, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        print(f"📄 Deployment plan exported to: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="Deployment & DevOps Agent")
    parser.add_argument('--project-path', default='.', help='Path to project directory')
    parser.add_argument('--action', choices=['analyze', 'create-files', 'check', 'all'], 
                       default='analyze', help='Action to perform')
    parser.add_argument('--platform', choices=['docker', 'heroku', 'aws', 'gcp', 'azure'], 
                       help='Target deployment platform')
    parser.add_argument('--output', default='deployment_plan.json', help='Output file path')
    
    args = parser.parse_args()
    
    agent = DeploymentAgent(args.project_path)
    
    print("🚀 Deployment & DevOps Agent Starting...")
    print(f"📁 Project Path: {agent.project_path}")
    print(f"🎯 Action: {args.action}")
    if args.platform:
        print(f"🌐 Platform: {args.platform}")
    print()
    
    results = {}
    
    if args.action in ['analyze', 'all']:
        print("🔍 Analyzing project for deployment...")
        analysis = agent.analyze_project_for_deployment()
        results['deployment_analysis'] = analysis
        
        print(f"✅ Analysis complete!")
        print(f"📊 Project Type: {analysis['dependency_analysis']['framework_type']}")
        print(f"🐳 Docker Ready: {analysis['deployment_readiness']['docker']['ready']}")
        print(f"🟣 Heroku Ready: {analysis['deployment_readiness']['heroku']['ready']}")
        print()
    
    if args.action in ['create-files', 'all'] and args.platform:
        print(f"📝 Creating deployment files for {args.platform}...")
        created_files = agent.create_deployment_files(args.platform)
        results['created_files'] = created_files
        
        for file_type, path in created_files.items():
            print(f"✅ Created: {file_type} -> {path}")
        print()
    
    if args.action in ['check', 'all']:
        print("🔍 Running deployment checks...")
        checks = agent.run_deployment_checks()
        results['deployment_checks'] = checks
        
        print(f"🎯 Overall Status: {checks['overall_status'].upper()}")
        for check_type, check_results in checks.items():
            if check_type != 'overall_status' and isinstance(check_results, dict):
                status = check_results.get('status', 'unknown')
                print(f"   {check_type}: {status.upper()}")
        print()
    
    # Export results
    agent.export_deployment_plan(results, args.output)
    
    print("✅ Deployment Agent Complete!")
    print(f"📄 Results saved to: {args.output}")


if __name__ == '__main__':
    main()