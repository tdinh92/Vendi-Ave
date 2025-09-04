#!/usr/bin/env python3
"""
Quick Test Generator - Simple wrapper for the Universal Testing Agent
Use this for quick test generation without interactive prompts
"""

import sys
import os
from pathlib import Path
from testing_agent import ProjectAnalyzer, TestGenerator

def quick_generate_tests(project_path: str, output_dir: str = "./tests"):
    """Generate tests quickly with sensible defaults"""
    
    print("🚀 Quick Test Generation Starting...")
    print(f"📁 Project: {project_path}")
    print(f"📝 Output: {output_dir}")
    print()
    
    # Analyze project
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.analyze()
    
    # Print analysis summary
    print("📊 PROJECT ANALYSIS:")
    print(f"  Functions: {len(analysis['functions'])}")
    print(f"  Classes: {len(analysis['classes'])}")
    print(f"  APIs: {len(analysis['apis'])}")
    print(f"  Framework: {analysis['framework']}")
    print(f"  Test Coverage: {analysis['test_coverage']['estimated_coverage_percent']:.1f}%")
    print()
    
    # Use intelligent defaults based on analysis
    requirements = {
        'test_framework': 'pytest',
        'coverage_target': 80,
        'include_integration': len(analysis['apis']) > 0,
        'include_performance': len(analysis['apis']) > 0,
        'null_handling': 'raise_exception',
        'error_logging': True,
        'graceful_degradation': True,
        'auth_required': any('auth' in str(api).lower() for api in analysis['apis']),
        'critical_functions': [f['name'] for f in analysis['functions'][:10]]  # First 10 functions
    }
    
    # Generate tests
    print("🔨 GENERATING TESTS...")
    generator = TestGenerator(analysis, requirements)
    generated_files = generator.generate_tests(output_dir)
    
    print("✅ TEST GENERATION COMPLETE!")
    print(f"Generated {len(generated_files)} files:")
    for file_path in generated_files:
        print(f"  📄 {file_path}")
    
    print()
    print("🎯 NEXT STEPS:")
    print("1. Review generated tests and fill in TODO sections")
    print("2. Install dependencies: pip install pytest pytest-cov")
    print(f"3. Run tests: python {output_dir}/run_tests.py")
    
    return generated_files

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_test.py <project_path> [output_dir]")
        print("Example: python quick_test.py /path/to/my/project ./my_tests")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./tests"
    
    if not os.path.exists(project_path):
        print(f"❌ Project path does not exist: {project_path}")
        sys.exit(1)
    
    try:
        quick_generate_tests(project_path, output_dir)
    except Exception as e:
        print(f"❌ Error generating tests: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()