#!/usr/bin/env python3
"""
Example usage of the Universal Testing Agent
Shows different ways to use the testing framework
"""

import os
import json
from pathlib import Path
from testing_agent import ProjectAnalyzer, InteractiveQuestionnaire, TestGenerator


def example_basic_usage():
    """Example 1: Basic programmatic usage without interaction"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Programmatic Usage")
    print("=" * 60)
    
    # Analyze a project
    project_path = "../AVM_Api"  # Adjust path as needed
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.analyze()
    
    print(f"📊 Analysis Results:")
    print(f"  Functions: {len(analysis['functions'])}")
    print(f"  Classes: {len(analysis['classes'])}")
    print(f"  APIs: {len(analysis['apis'])}")
    print(f"  Framework: {analysis['framework']}")
    
    # Use default testing requirements
    requirements = {
        'test_framework': 'pytest',
        'coverage_target': 90,
        'include_integration': True,
        'critical_functions': ['get_avm_history', 'get_basic_profile'],
        'null_handling': 'raise_exception',
        'error_logging': True,
        'graceful_degradation': True
    }
    
    # Generate tests
    generator = TestGenerator(analysis, requirements)
    output_dir = "./example_tests"
    generated_files = generator.generate_tests(output_dir)
    
    print(f"\n✅ Generated {len(generated_files)} test files:")
    for file_path in generated_files:
        print(f"  📄 {file_path}")


def example_custom_requirements():
    """Example 2: Using custom testing requirements"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Custom Requirements")
    print("=" * 60)
    
    project_path = "../AVM_Api"
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.analyze()
    
    # Define custom requirements for API testing
    custom_requirements = {
        'test_framework': 'pytest',
        'coverage_target': 95,
        'include_integration': True,
        'include_performance': True,
        
        # Function-specific requirements
        'critical_functions': ['get_complete_report', 'get_combined_report'],
        'null_handling': 'return_none',
        
        # API-specific requirements  
        'api_property_complete': {
            'error_code': '400',
            'timeout': 3.0,
            'methods': ['POST']
        },
        'api_property_combined': {
            'error_code': '422', 
            'timeout': 5.0,
            'methods': ['POST']
        },
        'auth_required': False,
        
        # Error handling
        'error_logging': True,
        'graceful_degradation': True,
        'retry_logic': True,
        'user_facing_errors': 'generic_message'
    }
    
    generator = TestGenerator(analysis, custom_requirements)
    output_dir = "./custom_tests"
    generated_files = generator.generate_tests(output_dir)
    
    print(f"✅ Generated custom test suite with {len(generated_files)} files")


def example_analysis_only():
    """Example 3: Analysis-only mode for project exploration"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Analysis-Only Mode")
    print("=" * 60)
    
    project_path = "../AVM_Api"
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.analyze()
    
    # Pretty print detailed analysis
    print("📋 Detailed Analysis:")
    print(f"\n🔧 Functions ({len(analysis['functions'])}):")
    for func in analysis['functions'][:5]:  # Show first 5
        args_str = ", ".join(func['args'])
        decorators = " ".join([f"@{d}" for d in func['decorators']])
        print(f"  • {func['name']}({args_str}) - {func['file']}:{func['line']}")
        if decorators:
            print(f"    Decorators: {decorators}")
        if func['docstring']:
            print(f"    Doc: {func['docstring'][:50]}...")
    
    print(f"\n🌐 API Endpoints ({len(analysis['apis'])}):")
    for api in analysis['apis']:
        methods_str = ", ".join(api['methods'])
        print(f"  • {methods_str} {api['route']} - {api['file']}")
    
    print(f"\n🏗️ Classes ({len(analysis['classes'])}):")
    for cls in analysis['classes'][:3]:  # Show first 3
        methods_str = ", ".join(cls['methods'][:3])
        print(f"  • {cls['name']} - {cls['file']}:{cls['line']}")
        print(f"    Methods: {methods_str}...")
    
    # Save detailed analysis
    analysis_file = "./project_analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"\n💾 Full analysis saved to: {analysis_file}")


def example_framework_specific():
    """Example 4: Framework-specific test generation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Framework-Specific Testing")
    print("=" * 60)
    
    project_path = "../AVM_Api"
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.analyze()
    
    framework = analysis['framework']
    print(f"🔧 Detected Framework: {framework}")
    
    # Adjust requirements based on detected framework
    if framework == 'flask':
        requirements = {
            'test_framework': 'pytest',
            'coverage_target': 85,
            'include_integration': True,
            
            # Flask-specific testing
            'test_client_needed': True,
            'test_json_responses': True,
            'test_status_codes': True,
            'test_cors_headers': True,
            
            # API requirements
            'auth_required': False,
            'validate_request_format': True,
            'test_error_responses': True
        }
    elif framework == 'fastapi':
        requirements = {
            'test_framework': 'pytest',
            'coverage_target': 90,
            
            # FastAPI-specific testing
            'test_async_endpoints': True,
            'test_pydantic_validation': True,
            'test_openapi_schema': True
        }
    else:
        requirements = {
            'test_framework': 'pytest',
            'coverage_target': 80
        }
    
    generator = TestGenerator(analysis, requirements)
    output_dir = f"./{framework}_tests"
    generated_files = generator.generate_tests(output_dir)
    
    print(f"✅ Generated {framework}-specific tests in {len(generated_files)} files")


def example_batch_processing():
    """Example 5: Batch process multiple projects"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Batch Processing Multiple Projects")
    print("=" * 60)
    
    # List of projects to analyze
    projects = [
        "../AVM_Api",
        "../simple_api",
        # Add more project paths as needed
    ]
    
    batch_results = {}
    
    for project_path in projects:
        project_name = Path(project_path).name
        print(f"\n🔍 Processing: {project_name}")
        
        if not Path(project_path).exists():
            print(f"⚠️ Skipping {project_name} - path not found")
            continue
        
        try:
            analyzer = ProjectAnalyzer(project_path)
            analysis = analyzer.analyze()
            
            # Quick analysis
            batch_results[project_name] = {
                'function_count': len(analysis['functions']),
                'class_count': len(analysis['classes']),
                'api_count': len(analysis['apis']),
                'framework': analysis['framework'],
                'project_type': analysis['project_type']
            }
            
            print(f"  📊 Functions: {len(analysis['functions'])}")
            print(f"  📊 Classes: {len(analysis['classes'])}")  
            print(f"  📊 APIs: {len(analysis['apis'])}")
            print(f"  📊 Framework: {analysis['framework']}")
            
        except Exception as e:
            print(f"❌ Error analyzing {project_name}: {e}")
            batch_results[project_name] = {'error': str(e)}
    
    # Save batch results
    with open('./batch_analysis_results.json', 'w') as f:
        json.dump(batch_results, f, indent=2)
    
    print(f"\n📊 Batch Analysis Summary:")
    for project, results in batch_results.items():
        if 'error' not in results:
            print(f"  {project}: {results['function_count']} functions, {results['api_count']} APIs, {results['framework']} framework")


def example_save_and_reuse_config():
    """Example 6: Save and reuse testing configurations"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Save & Reuse Testing Configurations")
    print("=" * 60)
    
    # Define a reusable testing configuration
    api_testing_config = {
        'test_framework': 'pytest',
        'coverage_target': 90,
        'include_integration': True,
        'include_performance': True,
        
        # API-specific defaults
        'default_timeout': 5.0,
        'default_error_code': '400',
        'auth_required': True,
        
        # Error handling standards
        'error_logging': True,
        'graceful_degradation': True,
        'retry_logic': False,
        'user_facing_errors': 'generic_message',
        
        # Quality standards
        'null_handling': 'raise_exception',
        'validate_input': True,
        'test_edge_cases': True
    }
    
    # Save configuration for reuse
    config_file = './api_testing_config.json'
    with open(config_file, 'w') as f:
        json.dump(api_testing_config, f, indent=2)
    
    print(f"💾 Saved reusable config to: {config_file}")
    
    # Load and use saved configuration
    with open(config_file, 'r') as f:
        loaded_config = json.load(f)
    
    print("🔄 Using saved configuration:")
    for key, value in loaded_config.items():
        print(f"  {key}: {value}")
    
    # Apply to project
    project_path = "../AVM_Api"
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.analyze()
    
    generator = TestGenerator(analysis, loaded_config)
    output_dir = "./config_based_tests"
    generated_files = generator.generate_tests(output_dir)
    
    print(f"✅ Generated tests using saved config: {len(generated_files)} files")


if __name__ == '__main__':
    """Run all examples"""
    print("🧪 Universal Testing Agent - Usage Examples")
    print("=" * 60)
    
    # Create output directory
    Path("./examples_output").mkdir(exist_ok=True)
    os.chdir("./examples_output")
    
    try:
        # Run all examples
        example_basic_usage()
        example_custom_requirements()  
        example_analysis_only()
        example_framework_specific()
        example_batch_processing()
        example_save_and_reuse_config()
        
        print("\n" + "=" * 60)
        print("🎉 All examples completed successfully!")
        print("Check the generated files in ./examples_output/")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("Make sure the AVM_Api project exists at ../AVM_Api")
    finally:
        # Return to original directory
        os.chdir("..")