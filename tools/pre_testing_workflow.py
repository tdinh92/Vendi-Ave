#!/usr/bin/env python3
"""
Pre-Testing Workflow - Integrated Architecture + Testing Pipeline
Runs architecture analysis first, then generates appropriate tests based on findings
"""

import sys
import os
from pathlib import Path
import json
from architecture_agent import ArchitectureAnalyzer, generate_architecture_report
from testing_agent import ProjectAnalyzer as TestAnalyzer, TestGenerator, InteractiveQuestionnaire

def run_pre_testing_workflow(project_path: str, output_dir: str = "./analysis_and_tests", interactive: bool = False):
    """Run complete pre-testing workflow: architecture analysis + test generation"""
    
    print("🚀 STARTING PRE-TESTING WORKFLOW")
    print("=" * 50)
    print(f"📁 Project: {project_path}")
    print(f"📝 Output: {output_dir}")
    print()
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # PHASE 1: Architecture Analysis
    print("🔍 PHASE 1: ARCHITECTURE ANALYSIS")
    print("-" * 35)
    
    arch_analyzer = ArchitectureAnalyzer(project_path)
    arch_analysis = arch_analyzer.analyze()
    
    # Generate architecture report
    arch_report_file = output_path / "architecture_report.txt"
    generate_architecture_report(arch_analysis, str(arch_report_file))
    
    # Save raw architecture data
    arch_json_file = output_path / "architecture_analysis.json"
    with open(arch_json_file, 'w') as f:
        json.dump(arch_analysis, f, indent=2)
    
    print(f"✅ Architecture analysis complete!")
    print(f"   Score: {arch_analysis['architecture_score']['score']}/100")
    print(f"   Grade: {arch_analysis['architecture_score']['grade']}")
    print(f"   Testability: {arch_analysis['architecture_score']['testability']}")
    print()
    
    # PHASE 2: Test Strategy Planning
    print("🧪 PHASE 2: TEST STRATEGY PLANNING")
    print("-" * 35)
    
    test_analyzer = TestAnalyzer(project_path)
    test_analysis = test_analyzer.analyze()
    
    # Create intelligent test requirements based on architecture findings
    test_requirements = create_intelligent_test_requirements(arch_analysis, test_analysis)
    
    print("📋 Test Strategy Based on Architecture:")
    print(f"   Test Framework: {test_requirements['test_framework']}")
    print(f"   Coverage Target: {test_requirements['coverage_target']}%")
    print(f"   Integration Tests: {'Yes' if test_requirements['include_integration'] else 'No'}")
    print(f"   Performance Tests: {'Yes' if test_requirements['include_performance'] else 'No'}")
    print(f"   Security Tests: {'Yes' if test_requirements.get('include_security') else 'No'}")
    print()
    
    # Interactive questionnaire if requested
    if interactive:
        print("🤔 INTERACTIVE QUESTIONNAIRE")
        print("-" * 28)
        questionnaire = InteractiveQuestionnaire(test_analysis)
        interactive_requirements = questionnaire.ask_questions()
        
        # Merge with intelligent requirements (interactive takes precedence)
        test_requirements.update(interactive_requirements)
    
    # PHASE 3: Test Generation
    print("🔨 PHASE 3: TEST GENERATION")
    print("-" * 26)
    
    test_generator = TestGenerator(test_analysis, test_requirements)
    test_output_dir = output_path / "generated_tests"
    generated_files = test_generator.generate_tests(str(test_output_dir))
    
    print(f"✅ Generated {len(generated_files)} test files:")
    for file_path in generated_files:
        print(f"   📄 {Path(file_path).name}")
    print()
    
    # PHASE 4: Integration Report
    print("📊 PHASE 4: INTEGRATION REPORT")
    print("-" * 30)
    
    integration_report = generate_integration_report(arch_analysis, test_analysis, test_requirements)
    
    integration_report_file = output_path / "integration_report.md"
    with open(integration_report_file, 'w') as f:
        f.write(integration_report)
    
    print("✅ WORKFLOW COMPLETE!")
    print("=" * 20)
    print("📁 Generated Files:")
    print(f"   🏗️ {arch_report_file}")
    print(f"   📊 {arch_json_file}")
    print(f"   🧪 {test_output_dir}/ (test files)")
    print(f"   📋 {integration_report_file}")
    print()
    print("🎯 NEXT STEPS:")
    print("1. Review architecture recommendations")
    print("2. Address high-priority code smells")
    print("3. Review and customize generated tests")
    print("4. Run tests and improve coverage")
    print("5. Set up CI/CD with testing pipeline")
    
    return {
        'architecture_analysis': arch_analysis,
        'test_analysis': test_analysis,
        'test_requirements': test_requirements,
        'generated_files': generated_files,
        'output_directory': str(output_path)
    }


def create_intelligent_test_requirements(arch_analysis: dict, test_analysis: dict) -> dict:
    """Create intelligent test requirements based on architecture analysis"""
    
    requirements = {
        'test_framework': 'pytest',  # Default
        'coverage_target': 80,       # Default
        'include_integration': False,
        'include_performance': False,
        'include_security': False,
        'null_handling': 'raise_exception',
        'error_logging': True,
        'graceful_degradation': True
    }
    
    # Adjust coverage target based on architecture score
    arch_score = arch_analysis['architecture_score']['score']
    if arch_score >= 85:
        requirements['coverage_target'] = 90  # High-quality code deserves high coverage
    elif arch_score >= 70:
        requirements['coverage_target'] = 80  # Good code gets standard coverage
    else:
        requirements['coverage_target'] = 70  # Poor architecture needs gradual improvement
    
    # Include integration tests if APIs are detected
    if test_analysis.get('apis', []):
        requirements['include_integration'] = True
    
    # Include performance tests if performance concerns detected
    if arch_analysis.get('performance_concerns', []):
        requirements['include_performance'] = True
    
    # Include security tests if security issues detected
    if arch_analysis.get('security_issues', []):
        requirements['include_security'] = True
    
    # Adjust null handling based on detected patterns
    code_smells = arch_analysis.get('code_smells', [])
    if any('High Complexity' in smell.get('type', '') for smell in code_smells):
        requirements['null_handling'] = 'ask_per_function'  # Need more detailed handling
    
    # Adjust error handling based on architecture quality
    if arch_score < 60:
        requirements['graceful_degradation'] = False  # Focus on basic functionality first
    
    # Set critical functions based on complexity and security
    critical_functions = []
    
    # Add functions with high complexity
    for func in test_analysis.get('functions', []):
        if func.get('complexity', 0) > 10:  # High complexity threshold
            critical_functions.append(func['name'])
    
    # Add functions in files with security issues
    security_files = [issue['file'] for issue in arch_analysis.get('security_issues', [])]
    for func in test_analysis.get('functions', []):
        if func.get('file') in security_files:
            critical_functions.append(func['name'])
    
    requirements['critical_functions'] = list(set(critical_functions))  # Remove duplicates
    
    return requirements


def generate_integration_report(arch_analysis: dict, test_analysis: dict, test_requirements: dict) -> str:
    """Generate an integrated report combining architecture and testing insights"""
    
    report = []
    report.append("# Pre-Testing Analysis & Strategy Report")
    report.append()
    report.append("## Executive Summary")
    report.append()
    
    arch_score = arch_analysis['architecture_score']
    report.append(f"**Architecture Quality:** {arch_score['score']}/100 (Grade {arch_score['grade']})")
    report.append(f"**Testability Rating:** {arch_score['testability']}")
    report.append(f"**Recommended Coverage Target:** {test_requirements['coverage_target']}%")
    report.append()
    
    # Architecture highlights
    report.append("## Architecture Analysis Highlights")
    report.append()
    
    if arch_analysis['design_patterns']:
        report.append("### ✅ Design Patterns Found")
        for pattern in arch_analysis['design_patterns']:
            report.append(f"- **{pattern['pattern']}** at {pattern.get('location', 'N/A')}")
        report.append()
    
    if arch_analysis['code_smells']:
        report.append("### ⚠️ Issues to Address Before Testing")
        high_priority = [s for s in arch_analysis['code_smells'] if s.get('severity') == 'high']
        medium_priority = [s for s in arch_analysis['code_smells'] if s.get('severity') == 'medium']
        
        if high_priority:
            report.append("**High Priority:**")
            for smell in high_priority:
                report.append(f"- {smell['type']} at {smell.get('location', 'N/A')}")
            report.append()
        
        if medium_priority:
            report.append("**Medium Priority:**")
            for smell in medium_priority[:5]:  # Limit to 5 to avoid overwhelming
                report.append(f"- {smell['type']} at {smell.get('location', 'N/A')}")
            report.append()
    
    # Security and performance
    if arch_analysis['security_issues']:
        report.append("### 🔒 Security Concerns")
        report.append("**Critical:** Address these before production deployment:")
        for issue in arch_analysis['security_issues']:
            report.append(f"- {issue['type']} in {issue['file']}")
        report.append()
    
    if arch_analysis['performance_concerns']:
        report.append("### ⚡ Performance Concerns")
        for concern in arch_analysis['performance_concerns']:
            report.append(f"- {concern['type']} in {concern['file']}")
        report.append()
    
    # Testing strategy
    report.append("## Testing Strategy")
    report.append()
    report.append("### Test Types Recommended")
    test_types = []
    test_types.append("✅ Unit Tests (Core functionality)")
    
    if test_requirements['include_integration']:
        test_types.append("✅ Integration Tests (API endpoints detected)")
    
    if test_requirements['include_performance']:
        test_types.append("✅ Performance Tests (Performance issues detected)")
    
    if test_requirements.get('include_security'):
        test_types.append("✅ Security Tests (Security vulnerabilities found)")
    
    for test_type in test_types:
        report.append(f"- {test_type}")
    report.append()
    
    # Critical functions to test
    if test_requirements.get('critical_functions'):
        report.append("### 🎯 Critical Functions Requiring Thorough Testing")
        for func in test_requirements['critical_functions'][:10]:  # Limit to 10
            report.append(f"- `{func}()`")
        report.append()
    
    # Recommendations
    report.append("## Recommendations")
    report.append()
    
    # Architecture-based recommendations
    if arch_analysis['recommendations']:
        report.append("### Architecture Improvements")
        for rec in arch_analysis['recommendations']:
            priority_emoji = "🔴" if rec['priority'] == 'critical' else "🟡" if rec['priority'] == 'high' else "🟢"
            report.append(f"{priority_emoji} **{rec['category']}:** {rec['recommendation']}")
            if 'testing_impact' in rec:
                report.append(f"   *Testing Impact:* {rec['testing_impact']}")
            report.append()
    
    # Testing workflow recommendations
    report.append("### Testing Workflow")
    workflow_steps = [
        "1. **Address Critical Architecture Issues** - Fix circular dependencies and high-priority code smells",
        "2. **Implement Unit Tests** - Start with critical functions identified above",
        "3. **Add Integration Tests** - Test API endpoints and component interactions" if test_requirements['include_integration'] else None,
        "4. **Security Testing** - Address security vulnerabilities with appropriate tests" if test_requirements.get('include_security') else None,
        "5. **Performance Testing** - Add performance benchmarks for identified bottlenecks" if test_requirements['include_performance'] else None,
        f"6. **Coverage Monitoring** - Aim for {test_requirements['coverage_target']}% code coverage",
        "7. **CI/CD Integration** - Set up automated testing pipeline"
    ]
    
    for step in workflow_steps:
        if step:  # Skip None values
            report.append(step)
    report.append()
    
    # Complexity metrics
    report.append("## Complexity Metrics")
    report.append()
    metrics = arch_analysis['complexity_metrics']
    report.append(f"- **Files Analyzed:** {metrics.get('total_files', 0)}")
    report.append(f"- **Classes:** {metrics.get('total_classes', 0)}")
    report.append(f"- **Functions:** {metrics.get('total_functions', 0)}")
    report.append(f"- **Average Methods per Class:** {metrics.get('avg_methods_per_class', 0)}")
    report.append(f"- **Average Dependencies per File:** {metrics.get('avg_dependencies_per_file', 0)}")
    report.append()
    
    # Tools and commands
    report.append("## Useful Commands")
    report.append()
    report.append("```bash")
    report.append("# Run architecture analysis")
    report.append(f"python tools/architecture_agent.py {test_analysis.get('project_path', '.')}")
    report.append()
    report.append("# Generate tests")
    report.append(f"python tools/testing_agent.py {test_analysis.get('project_path', '.')} --interactive")
    report.append()
    report.append("# Run tests with coverage")
    report.append("python generated_tests/run_tests.py")
    report.append("```")
    report.append()
    
    return "\n".join(report)


def main():
    """Main entry point for pre-testing workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pre-Testing Workflow: Architecture + Testing')
    parser.add_argument('project_path', help='Path to project to analyze')
    parser.add_argument('--output', '-o', default='./analysis_and_tests', help='Output directory')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run interactive questionnaire')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.project_path):
        print(f"❌ Project path does not exist: {args.project_path}")
        sys.exit(1)
    
    try:
        result = run_pre_testing_workflow(args.project_path, args.output, args.interactive)
        print(f"\n🎉 Workflow completed successfully!")
        print(f"📁 All outputs saved to: {result['output_directory']}")
    except Exception as e:
        print(f"❌ Error running workflow: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()