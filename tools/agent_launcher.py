#!/usr/bin/env python3
"""
Agent Launcher - Unified Interface for All Specialized Agents
Provides a single entry point to run any agent with guided workflows
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any
import json


class AgentLauncher:
    """Unified launcher for all specialized agents"""
    
    def __init__(self):
        self.agents = {
            'testing': {
                'file': 'testing_agent.py',
                'description': 'Universal Testing Agent - Generate comprehensive test suites',
                'examples': [
                    'python3 testing_agent.py ../AVM_Api --interactive --output ../AVM_Api/tests'
                ]
            },
            'property': {
                'file': 'property_data_agent.py',
                'description': 'Property Data Analysis Agent - Portfolio analysis and market trends',
                'examples': [
                    'python3 property_data_agent.py --addresses "4 Fiorenza Dr, Wilmington, MA" --analysis-type portfolio',
                    'python3 property_data_agent.py --addresses "123 Main St, Boston, MA" --analysis-type trends'
                ]
            },
            'monitoring': {
                'file': 'api_monitoring_agent.py',
                'description': 'API Monitoring Agent - Performance testing and health monitoring',
                'examples': [
                    'python3 api_monitoring_agent.py --monitor-type health --duration 10',
                    'python3 api_monitoring_agent.py --monitor-type stress --concurrent-users 20'
                ]
            },
            'quality': {
                'file': 'data_quality_agent.py',
                'description': 'Data Quality Agent - Comprehensive data validation and analysis',
                'examples': [
                    'python3 data_quality_agent.py --addresses "123 Main St, Boston, MA" --endpoints "/property/combined"',
                    'python3 data_quality_agent.py --addresses "456 Oak Ave, Springfield, IL"'
                ]
            },
            'deployment': {
                'file': 'deployment_agent.py',
                'description': 'Deployment Agent - DevOps automation and deployment preparation',
                'examples': [
                    'python3 deployment_agent.py --action analyze',
                    'python3 deployment_agent.py --action create-files --platform docker'
                ]
            },
            'architecture': {
                'file': 'architecture_agent.py',
                'description': 'Architecture Analysis Agent - Analyze codebase architecture patterns',
                'examples': [
                    'python3 architecture_agent.py ../AVM_Api --output architecture_analysis.json'
                ]
            }
        }
        
        self.workflows = {
            'investment-analysis': {
                'description': 'Complete investment analysis workflow',
                'agents': ['property', 'quality', 'monitoring'],
                'steps': [
                    'Analyze property portfolio performance',
                    'Validate data quality for investment decisions', 
                    'Monitor API performance for real-time analysis'
                ]
            },
            'production-deployment': {
                'description': 'Production deployment readiness workflow',
                'agents': ['quality', 'deployment', 'testing', 'monitoring'],
                'steps': [
                    'Validate data quality',
                    'Check deployment readiness',
                    'Run comprehensive tests',
                    'Monitor production performance'
                ]
            },
            'market-analysis': {
                'description': 'Market trend analysis workflow',
                'agents': ['property', 'quality'],
                'steps': [
                    'Analyze market trends and valuation accuracy',
                    'Ensure data quality for analysis'
                ]
            },
            'api-health-check': {
                'description': 'Complete API health and performance check',
                'agents': ['monitoring', 'quality', 'testing'],
                'steps': [
                    'Monitor API performance and availability',
                    'Validate data quality across endpoints',
                    'Run automated tests'
                ]
            }
        }
    
    def list_agents(self):
        """Display all available agents"""
        print("🤖 Available Specialized Agents:\n")
        
        for agent_id, info in self.agents.items():
            print(f"🔹 {agent_id.upper()}")
            print(f"   File: {info['file']}")
            print(f"   Description: {info['description']}")
            print(f"   Examples:")
            for example in info['examples'][:2]:  # Show first 2 examples
                print(f"     {example}")
            print()
    
    def list_workflows(self):
        """Display all available workflows"""
        print("🔄 Available Workflows:\n")
        
        for workflow_id, info in self.workflows.items():
            print(f"🔹 {workflow_id.upper()}")
            print(f"   Description: {info['description']}")
            print(f"   Agents Used: {', '.join(info['agents'])}")
            print(f"   Steps:")
            for i, step in enumerate(info['steps'], 1):
                print(f"     {i}. {step}")
            print()
    
    def run_agent(self, agent_name: str, args: List[str] = None):
        """Run a specific agent with arguments"""
        if agent_name not in self.agents:
            print(f"❌ Agent '{agent_name}' not found.")
            print("Available agents:", ', '.join(self.agents.keys()))
            return False
        
        agent_file = self.agents[agent_name]['file']
        
        if not Path(agent_file).exists():
            print(f"❌ Agent file '{agent_file}' not found.")
            return False
        
        # Build command
        cmd = ['python3', agent_file]
        if args:
            cmd.extend(args)
        
        print(f"🚀 Running {agent_name} agent...")
        print(f"Command: {' '.join(cmd)}")
        print()
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=False)
            print(f"✅ {agent_name} agent completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {agent_name} agent failed with exit code {e.returncode}")
            return False
        except KeyboardInterrupt:
            print(f"🛑 {agent_name} agent interrupted by user")
            return False
    
    def run_workflow(self, workflow_name: str, config: Dict[str, Any] = None):
        """Run a complete workflow"""
        if workflow_name not in self.workflows:
            print(f"❌ Workflow '{workflow_name}' not found.")
            print("Available workflows:", ', '.join(self.workflows.keys()))
            return False
        
        workflow = self.workflows[workflow_name]
        
        print(f"🔄 Starting Workflow: {workflow_name.upper()}")
        print(f"Description: {workflow['description']}")
        print(f"Steps: {len(workflow['steps'])}")
        print()
        
        if config is None:
            config = self._get_workflow_config(workflow_name)
        
        # Execute workflow steps
        success_count = 0
        for i, (agent_name, step_desc) in enumerate(zip(workflow['agents'], workflow['steps']), 1):
            print(f"📋 Step {i}/{len(workflow['steps'])}: {step_desc}")
            print(f"🤖 Running {agent_name} agent...")
            
            # Get agent-specific configuration
            agent_args = self._build_agent_args(agent_name, config)
            
            success = self.run_agent(agent_name, agent_args)
            
            if success:
                success_count += 1
                print(f"✅ Step {i} completed successfully!\n")
            else:
                print(f"❌ Step {i} failed!\n")
                
                # Ask user if they want to continue
                response = input(f"Continue with remaining steps? (y/n): ").lower()
                if response != 'y':
                    break
        
        # Workflow summary
        print(f"🎯 Workflow Summary:")
        print(f"   Total Steps: {len(workflow['steps'])}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {len(workflow['steps']) - success_count}")
        
        if success_count == len(workflow['steps']):
            print(f"✅ Workflow '{workflow_name}' completed successfully!")
        else:
            print(f"⚠️  Workflow '{workflow_name}' completed with some failures.")
        
        return success_count == len(workflow['steps'])
    
    def _get_workflow_config(self, workflow_name: str) -> Dict[str, Any]:
        """Get configuration for a workflow from user input"""
        config = {}
        
        if workflow_name in ['investment-analysis', 'market-analysis']:
            # Get property addresses
            addresses_input = input("Enter property addresses (comma-separated): ")
            if addresses_input.strip():
                config['addresses'] = [addr.strip() for addr in addresses_input.split(',')]
            else:
                config['addresses'] = ["4 Fiorenza Drive, Wilmington, MA 01887"]
        
        if workflow_name in ['production-deployment']:
            # Get deployment platform
            platform = input("Enter deployment platform (docker/heroku/aws/gcp/azure): ")
            if platform.strip():
                config['platform'] = platform.strip()
            else:
                config['platform'] = 'docker'
        
        # Get API URL
        api_url = input("Enter API URL (default: http://localhost:5000): ")
        config['api_url'] = api_url.strip() if api_url.strip() else 'http://localhost:5000'
        
        return config
    
    def _build_agent_args(self, agent_name: str, config: Dict[str, Any]) -> List[str]:
        """Build command-line arguments for specific agent"""
        args = []
        
        # Common arguments
        if 'api_url' in config:
            args.extend(['--api-url', config['api_url']])
        
        # Agent-specific arguments
        if agent_name == 'property':
            if 'addresses' in config:
                args.extend(['--addresses'] + config['addresses'])
            args.extend(['--analysis-type', 'all'])
        
        elif agent_name == 'quality':
            if 'addresses' in config:
                args.extend(['--addresses'] + config['addresses'])
        
        elif agent_name == 'monitoring':
            args.extend(['--monitor-type', 'all', '--duration', '5'])
        
        elif agent_name == 'deployment':
            args.extend(['--action', 'analyze'])
            if 'platform' in config:
                args.extend(['--platform', config['platform']])
        
        elif agent_name == 'testing':
            args.extend(['../AVM_Api', '--output', '../AVM_Api/tests'])
        
        return args
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("🤖 Agent Launcher - Interactive Mode")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. List available agents")
            print("2. List available workflows")  
            print("3. Run specific agent")
            print("4. Run workflow")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                self.list_agents()
            
            elif choice == '2':
                self.list_workflows()
            
            elif choice == '3':
                print("\nAvailable agents:", ', '.join(self.agents.keys()))
                agent_name = input("Enter agent name: ").strip()
                
                if agent_name in self.agents:
                    print(f"\nExample usage for {agent_name}:")
                    for example in self.agents[agent_name]['examples']:
                        print(f"  {example}")
                    
                    custom_args = input("\nEnter custom arguments (or press Enter for guided setup): ").strip()
                    
                    if custom_args:
                        args = custom_args.split()
                    else:
                        # Guided setup for common arguments
                        args = self._guided_agent_setup(agent_name)
                    
                    self.run_agent(agent_name, args)
                else:
                    print(f"❌ Agent '{agent_name}' not found.")
            
            elif choice == '4':
                print("\nAvailable workflows:", ', '.join(self.workflows.keys()))
                workflow_name = input("Enter workflow name: ").strip()
                
                if workflow_name in self.workflows:
                    self.run_workflow(workflow_name)
                else:
                    print(f"❌ Workflow '{workflow_name}' not found.")
            
            elif choice == '5':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-5.")
    
    def _guided_agent_setup(self, agent_name: str) -> List[str]:
        """Guided setup for agent arguments"""
        args = []
        
        if agent_name in ['property', 'quality']:
            addresses_input = input("Enter property addresses (comma-separated): ")
            if addresses_input.strip():
                addresses = [addr.strip() for addr in addresses_input.split(',')]
                args.extend(['--addresses'] + addresses)
        
        if agent_name == 'property':
            analysis_type = input("Enter analysis type (portfolio/trends/accuracy/all) [default: all]: ")
            args.extend(['--analysis-type', analysis_type.strip() or 'all'])
        
        elif agent_name == 'monitoring':
            monitor_type = input("Enter monitor type (health/stress/usage/all) [default: health]: ")
            args.extend(['--monitor-type', monitor_type.strip() or 'health'])
            
            duration = input("Enter duration in minutes [default: 5]: ")
            args.extend(['--duration', duration.strip() or '5'])
        
        elif agent_name == 'deployment':
            action = input("Enter action (analyze/create-files/check/all) [default: analyze]: ")
            args.extend(['--action', action.strip() or 'analyze'])
            
            if action in ['create-files', 'all']:
                platform = input("Enter platform (docker/heroku/aws/gcp/azure): ")
                if platform.strip():
                    args.extend(['--platform', platform.strip()])
        
        # API URL
        api_url = input("Enter API URL [default: http://localhost:5000]: ")
        if api_url.strip() and agent_name not in ['testing', 'deployment']:
            args.extend(['--api-url', api_url.strip()])
        
        return args


def main():
    parser = argparse.ArgumentParser(description="Agent Launcher - Unified interface for all specialized agents")
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--list-agents', action='store_true', help='List all available agents')
    parser.add_argument('--list-workflows', action='store_true', help='List all available workflows')
    parser.add_argument('--agent', choices=['testing', 'property', 'monitoring', 'quality', 'deployment', 'architecture'], 
                       help='Run specific agent')
    parser.add_argument('--workflow', choices=['investment-analysis', 'production-deployment', 'market-analysis', 'api-health-check'],
                       help='Run specific workflow')
    parser.add_argument('--args', nargs='*', help='Arguments to pass to agent')
    
    args = parser.parse_args()
    
    launcher = AgentLauncher()
    
    print("🚀 Agent Launcher - Specialized Agents for Real Estate & API Development")
    print("=" * 70)
    
    if args.interactive:
        launcher.interactive_mode()
    
    elif args.list_agents:
        launcher.list_agents()
    
    elif args.list_workflows:
        launcher.list_workflows()
    
    elif args.agent:
        launcher.run_agent(args.agent, args.args)
    
    elif args.workflow:
        launcher.run_workflow(args.workflow)
    
    else:
        # Show help and available options
        launcher.list_agents()
        print("\n" + "=" * 50)
        launcher.list_workflows()
        print(f"\n💡 Use --interactive for guided mode")
        print(f"💡 Use --agent <name> --args <arguments> to run specific agent")
        print(f"💡 Use --workflow <name> to run complete workflow")


if __name__ == '__main__':
    main()