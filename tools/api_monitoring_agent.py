#!/usr/bin/env python3
"""
API Monitoring & Performance Agent
Specialized agent for monitoring API health, performance, and usage patterns
Designed for REST APIs, microservices, and production monitoring
"""

import time
import json
import requests
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


class APIMonitoringAgent:
    """Agent for comprehensive API monitoring and performance analysis"""
    
    def __init__(self, api_base_url: str = "http://localhost:5000"):
        self.api_base_url = api_base_url.rstrip('/')
        self.monitoring_data = []
        self.health_checks = []
        self.performance_metrics = {}
        
    def run_health_check_monitoring(self, duration_minutes: int = 5, interval_seconds: int = 30) -> Dict[str, Any]:
        """Run continuous health check monitoring"""
        print(f"🔍 Starting health check monitoring for {duration_minutes} minutes...")
        print(f"⏱️  Check interval: {interval_seconds} seconds")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        health_results = []
        
        while datetime.now() < end_time:
            check_result = self._perform_health_check()
            health_results.append(check_result)
            
            # Print status
            status_icon = "✅" if check_result['healthy'] else "❌"
            print(f"{status_icon} {check_result['timestamp'][:19]} - "
                  f"Response: {check_result['response_time']:.3f}s - "
                  f"Status: {check_result['status_code']}")
            
            time.sleep(interval_seconds)
        
        # Analyze health check results
        analysis = self._analyze_health_checks(health_results)
        analysis['monitoring_duration_minutes'] = duration_minutes
        analysis['check_interval_seconds'] = interval_seconds
        
        return analysis
    
    def _perform_health_check(self) -> Dict[str, Any]:
        """Perform a single health check"""
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            return {
                'timestamp': timestamp,
                'healthy': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response_time,
                'response_data': response.json() if response.status_code == 200 else None,
                'error': None
            }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                'timestamp': timestamp,
                'healthy': False,
                'status_code': None,
                'response_time': response_time,
                'response_data': None,
                'error': str(e)
            }
    
    def _analyze_health_checks(self, health_results: List[Dict]) -> Dict[str, Any]:
        """Analyze health check monitoring results"""
        if not health_results:
            return {'error': 'No health check data to analyze'}
        
        total_checks = len(health_results)
        successful_checks = len([r for r in health_results if r['healthy']])
        failed_checks = total_checks - successful_checks
        
        response_times = [r['response_time'] for r in health_results if r['response_time']]
        
        analysis = {
            'uptime_statistics': {
                'total_checks': total_checks,
                'successful_checks': successful_checks,
                'failed_checks': failed_checks,
                'uptime_percentage': (successful_checks / total_checks) * 100,
                'availability_sla': 'Excellent (99.9%+)' if successful_checks / total_checks > 0.999 else
                                  'Good (99%+)' if successful_checks / total_checks > 0.99 else
                                  'Acceptable (95%+)' if successful_checks / total_checks > 0.95 else
                                  'Poor (<95%)'
            },
            'performance_statistics': {
                'average_response_time': statistics.mean(response_times) if response_times else 0,
                'median_response_time': statistics.median(response_times) if response_times else 0,
                'min_response_time': min(response_times) if response_times else 0,
                'max_response_time': max(response_times) if response_times else 0,
                'response_time_std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0
            },
            'incidents': [r for r in health_results if not r['healthy']],
            'monitoring_period': {
                'start_time': health_results[0]['timestamp'],
                'end_time': health_results[-1]['timestamp']
            }
        }
        
        # Add performance insights
        if response_times:
            avg_response = statistics.mean(response_times)
            analysis['performance_insights'] = []
            
            if avg_response < 0.1:
                analysis['performance_insights'].append("Excellent response times - under 100ms average")
            elif avg_response < 0.5:
                analysis['performance_insights'].append("Good response times - under 500ms average")
            elif avg_response < 2.0:
                analysis['performance_insights'].append("Acceptable response times - under 2s average")
            else:
                analysis['performance_insights'].append("Slow response times - over 2s average")
            
            if len(response_times) > 1:
                std_dev = statistics.stdev(response_times)
                if std_dev < 0.1:
                    analysis['performance_insights'].append("Consistent performance - low response time variation")
                elif std_dev > 1.0:
                    analysis['performance_insights'].append("Variable performance - high response time variation")
        
        return analysis
    
    def run_endpoint_stress_test(self, endpoint_configs: List[Dict], 
                                concurrent_users: int = 10, 
                                duration_minutes: int = 2) -> Dict[str, Any]:
        """Run stress test on multiple endpoints"""
        print(f"🚀 Starting endpoint stress test...")
        print(f"👥 Concurrent users: {concurrent_users}")
        print(f"⏱️  Duration: {duration_minutes} minutes")
        print(f"🎯 Endpoints: {len(endpoint_configs)}")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        all_results = []
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # Submit stress test tasks for each endpoint
            futures = []
            
            for config in endpoint_configs:
                for _ in range(concurrent_users):
                    future = executor.submit(
                        self._run_single_endpoint_stress_test, 
                        config, 
                        end_time
                    )
                    futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result()
                    all_results.extend(result)
                except Exception as e:
                    print(f"❌ Stress test thread failed: {e}")
        
        # Analyze stress test results
        analysis = self._analyze_stress_test_results(all_results, endpoint_configs)
        analysis['test_configuration'] = {
            'concurrent_users': concurrent_users,
            'duration_minutes': duration_minutes,
            'endpoints_tested': len(endpoint_configs)
        }
        
        return analysis
    
    def _run_single_endpoint_stress_test(self, config: Dict, end_time: datetime) -> List[Dict]:
        """Run stress test for a single endpoint configuration"""
        results = []
        request_count = 0
        
        while datetime.now() < end_time:
            start_time = time.time()
            
            try:
                if config['method'].upper() == 'GET':
                    response = requests.get(
                        f"{self.api_base_url}{config['endpoint']}", 
                        timeout=30
                    )
                elif config['method'].upper() == 'POST':
                    response = requests.post(
                        f"{self.api_base_url}{config['endpoint']}",
                        json=config.get('payload', {}),
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )
                
                response_time = time.time() - start_time
                
                results.append({
                    'endpoint': config['endpoint'],
                    'method': config['method'],
                    'timestamp': datetime.now().isoformat(),
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'success': 200 <= response.status_code < 300,
                    'request_size': len(json.dumps(config.get('payload', {})).encode()),
                    'response_size': len(response.content) if response.content else 0,
                    'error': None
                })
                
            except Exception as e:
                response_time = time.time() - start_time
                results.append({
                    'endpoint': config['endpoint'],
                    'method': config['method'],
                    'timestamp': datetime.now().isoformat(),
                    'status_code': None,
                    'response_time': response_time,
                    'success': False,
                    'request_size': len(json.dumps(config.get('payload', {})).encode()),
                    'response_size': 0,
                    'error': str(e)
                })
            
            request_count += 1
            
            # Small delay to prevent overwhelming the server
            time.sleep(0.1)
        
        return results
    
    def _analyze_stress_test_results(self, results: List[Dict], configs: List[Dict]) -> Dict[str, Any]:
        """Analyze stress test results"""
        if not results:
            return {'error': 'No stress test data to analyze'}
        
        # Group results by endpoint
        by_endpoint = {}
        for result in results:
            endpoint = result['endpoint']
            if endpoint not in by_endpoint:
                by_endpoint[endpoint] = []
            by_endpoint[endpoint].append(result)
        
        endpoint_analysis = {}
        overall_stats = {
            'total_requests': len(results),
            'successful_requests': len([r for r in results if r['success']]),
            'failed_requests': len([r for r in results if not r['success']]),
            'average_response_time': 0,
            'requests_per_second': 0
        }
        
        # Calculate overall success rate
        overall_stats['success_rate'] = (overall_stats['successful_requests'] / overall_stats['total_requests']) * 100
        
        # Analyze each endpoint
        for endpoint, endpoint_results in by_endpoint.items():
            response_times = [r['response_time'] for r in endpoint_results if r['response_time']]
            successful = [r for r in endpoint_results if r['success']]
            
            # Calculate requests per second
            if endpoint_results:
                time_span = (datetime.fromisoformat(endpoint_results[-1]['timestamp']) - 
                           datetime.fromisoformat(endpoint_results[0]['timestamp'])).total_seconds()
                rps = len(endpoint_results) / max(time_span, 1)
            else:
                rps = 0
            
            endpoint_analysis[endpoint] = {
                'total_requests': len(endpoint_results),
                'successful_requests': len(successful),
                'success_rate': (len(successful) / len(endpoint_results)) * 100 if endpoint_results else 0,
                'requests_per_second': rps,
                'performance_metrics': {
                    'average_response_time': statistics.mean(response_times) if response_times else 0,
                    'median_response_time': statistics.median(response_times) if response_times else 0,
                    'min_response_time': min(response_times) if response_times else 0,
                    'max_response_time': max(response_times) if response_times else 0,
                    'p95_response_time': self._percentile(response_times, 95) if response_times else 0,
                    'p99_response_time': self._percentile(response_times, 99) if response_times else 0
                },
                'error_analysis': self._analyze_errors([r for r in endpoint_results if not r['success']])
            }
        
        # Calculate overall metrics
        all_response_times = [r['response_time'] for r in results if r['response_time']]
        if all_response_times:
            overall_stats['average_response_time'] = statistics.mean(all_response_times)
        
        if results:
            time_span = (datetime.fromisoformat(results[-1]['timestamp']) - 
                        datetime.fromisoformat(results[0]['timestamp'])).total_seconds()
            overall_stats['requests_per_second'] = len(results) / max(time_span, 1)
        
        return {
            'overall_statistics': overall_stats,
            'endpoint_analysis': endpoint_analysis,
            'performance_insights': self._generate_performance_insights(endpoint_analysis),
            'load_test_summary': self._generate_load_test_summary(overall_stats, endpoint_analysis)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _analyze_errors(self, failed_requests: List[Dict]) -> Dict[str, Any]:
        """Analyze error patterns in failed requests"""
        if not failed_requests:
            return {'no_errors': True}
        
        error_types = {}
        status_codes = {}
        
        for request in failed_requests:
            # Group by error type
            error = request.get('error', 'Unknown')
            if error not in error_types:
                error_types[error] = 0
            error_types[error] += 1
            
            # Group by status code
            status = request.get('status_code', 'None')
            if status not in status_codes:
                status_codes[status] = 0
            status_codes[status] += 1
        
        return {
            'total_errors': len(failed_requests),
            'error_types': error_types,
            'status_code_distribution': status_codes,
            'error_rate': len(failed_requests) / len(failed_requests) * 100  # This will be 100% for failed requests only
        }
    
    def _generate_performance_insights(self, endpoint_analysis: Dict) -> List[str]:
        """Generate insights about API performance"""
        insights = []
        
        for endpoint, metrics in endpoint_analysis.items():
            success_rate = metrics['success_rate']
            avg_response = metrics['performance_metrics']['average_response_time']
            rps = metrics['requests_per_second']
            
            # Success rate insights
            if success_rate >= 99.9:
                insights.append(f"{endpoint}: Excellent reliability (99.9%+ success rate)")
            elif success_rate >= 95:
                insights.append(f"{endpoint}: Good reliability ({success_rate:.1f}% success rate)")
            else:
                insights.append(f"{endpoint}: Poor reliability ({success_rate:.1f}% success rate) - needs investigation")
            
            # Performance insights
            if avg_response < 0.1:
                insights.append(f"{endpoint}: Excellent performance (<100ms average)")
            elif avg_response < 0.5:
                insights.append(f"{endpoint}: Good performance (<500ms average)")
            elif avg_response > 2.0:
                insights.append(f"{endpoint}: Slow performance (>{avg_response:.1f}s average) - optimization needed")
            
            # Throughput insights
            if rps > 100:
                insights.append(f"{endpoint}: High throughput capability ({rps:.1f} req/s)")
            elif rps < 10:
                insights.append(f"{endpoint}: Low throughput ({rps:.1f} req/s) - may need scaling")
        
        return insights
    
    def _generate_load_test_summary(self, overall_stats: Dict, endpoint_analysis: Dict) -> List[str]:
        """Generate load test summary insights"""
        summary = []
        
        # Overall system health
        overall_success = overall_stats['success_rate']
        if overall_success >= 99:
            summary.append("System handles load excellently - minimal failures under stress")
        elif overall_success >= 95:
            summary.append("System handles load well - some failures under stress")
        else:
            summary.append("System struggles under load - significant failures detected")
        
        # Performance summary
        avg_response = overall_stats['average_response_time']
        if avg_response < 0.5:
            summary.append("Response times remain fast under load")
        elif avg_response < 2.0:
            summary.append("Response times acceptable under load")
        else:
            summary.append("Response times degraded under load - performance bottlenecks detected")
        
        # Throughput summary
        total_rps = overall_stats['requests_per_second']
        summary.append(f"System throughput: {total_rps:.1f} requests per second")
        
        return summary
    
    def monitor_endpoint_usage_patterns(self, duration_minutes: int = 10) -> Dict[str, Any]:
        """Monitor real-time usage patterns by analyzing server logs or making test requests"""
        print(f"📊 Monitoring endpoint usage patterns for {duration_minutes} minutes...")
        
        # Define test endpoints to monitor
        test_endpoints = [
            {'endpoint': '/health', 'method': 'GET'},
            {'endpoint': '/', 'method': 'GET'},
            {'endpoint': '/charts', 'method': 'GET'},
            {'endpoint': '/property/combined', 'method': 'POST', 'payload': {'address': 'test address'}},
        ]
        
        usage_data = []
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            for endpoint_config in test_endpoints:
                usage_result = self._test_endpoint_usage(endpoint_config)
                usage_data.append(usage_result)
            
            time.sleep(30)  # Check every 30 seconds
        
        # Analyze usage patterns
        analysis = self._analyze_usage_patterns(usage_data)
        return analysis
    
    def _test_endpoint_usage(self, config: Dict) -> Dict[str, Any]:
        """Test endpoint and record usage metrics"""
        start_time = time.time()
        
        try:
            if config['method'].upper() == 'GET':
                response = requests.get(f"{self.api_base_url}{config['endpoint']}", timeout=10)
            else:
                response = requests.post(
                    f"{self.api_base_url}{config['endpoint']}",
                    json=config.get('payload', {}),
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            
            response_time = time.time() - start_time
            
            return {
                'endpoint': config['endpoint'],
                'method': config['method'],
                'timestamp': datetime.now().isoformat(),
                'response_time': response_time,
                'status_code': response.status_code,
                'available': 200 <= response.status_code < 300,
                'response_size': len(response.content) if response.content else 0
            }
        
        except Exception as e:
            return {
                'endpoint': config['endpoint'],
                'method': config['method'],
                'timestamp': datetime.now().isoformat(),
                'response_time': time.time() - start_time,
                'status_code': None,
                'available': False,
                'response_size': 0,
                'error': str(e)
            }
    
    def _analyze_usage_patterns(self, usage_data: List[Dict]) -> Dict[str, Any]:
        """Analyze endpoint usage patterns"""
        if not usage_data:
            return {'error': 'No usage data collected'}
        
        # Group by endpoint
        by_endpoint = {}
        for record in usage_data:
            endpoint = record['endpoint']
            if endpoint not in by_endpoint:
                by_endpoint[endpoint] = []
            by_endpoint[endpoint].append(record)
        
        patterns = {}
        for endpoint, records in by_endpoint.items():
            available_checks = len([r for r in records if r['available']])
            total_checks = len(records)
            avg_response_time = statistics.mean([r['response_time'] for r in records if 'response_time' in r])
            
            patterns[endpoint] = {
                'availability_percentage': (available_checks / total_checks) * 100,
                'average_response_time': avg_response_time,
                'total_checks': total_checks,
                'status': 'Healthy' if available_checks / total_checks > 0.95 else 'Degraded'
            }
        
        return {
            'monitoring_summary': patterns,
            'overall_system_health': 'Healthy' if all(p['status'] == 'Healthy' for p in patterns.values()) else 'Degraded',
            'monitoring_period': {
                'start': usage_data[0]['timestamp'],
                'end': usage_data[-1]['timestamp'],
                'total_data_points': len(usage_data)
            }
        }
    
    def export_monitoring_report(self, monitoring_data: Dict, output_path: str = "api_monitoring_report.json"):
        """Export monitoring results to JSON report"""
        monitoring_data['export_timestamp'] = datetime.now().isoformat()
        monitoring_data['agent_version'] = "1.0.0"
        
        with open(output_path, 'w') as f:
            json.dump(monitoring_data, f, indent=2, default=str)
        
        print(f"📄 Monitoring report exported to: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="API Monitoring & Performance Agent")
    parser.add_argument('--api-url', default='http://localhost:5000', help='API base URL to monitor')
    parser.add_argument('--monitor-type', choices=['health', 'stress', 'usage', 'all'], 
                       default='all', help='Type of monitoring to perform')
    parser.add_argument('--duration', type=int, default=5, help='Monitoring duration in minutes')
    parser.add_argument('--concurrent-users', type=int, default=10, help='Concurrent users for stress testing')
    parser.add_argument('--output', default='api_monitoring_report.json', help='Output file path')
    
    args = parser.parse_args()
    
    agent = APIMonitoringAgent(args.api_url)
    
    print("🔍 API Monitoring & Performance Agent Starting...")
    print(f"🌐 API URL: {args.api_url}")
    print(f"📊 Monitor Type: {args.monitor_type}")
    print(f"⏱️  Duration: {args.duration} minutes")
    print()
    
    results = {
        'monitoring_configuration': {
            'api_url': args.api_url,
            'monitor_type': args.monitor_type,
            'duration_minutes': args.duration
        }
    }
    
    if args.monitor_type in ['health', 'all']:
        print("Running health check monitoring...")
        results['health_monitoring'] = agent.run_health_check_monitoring(duration_minutes=args.duration)
        print()
    
    if args.monitor_type in ['stress', 'all']:
        print("Running stress test...")
        # Define test endpoints for stress testing
        test_endpoints = [
            {'endpoint': '/health', 'method': 'GET'},
            {'endpoint': '/property/combined', 'method': 'POST', 'payload': {'address': '123 Main St, Boston, MA'}},
            {'endpoint': '/', 'method': 'GET'}
        ]
        results['stress_testing'] = agent.run_endpoint_stress_test(
            test_endpoints, 
            concurrent_users=args.concurrent_users, 
            duration_minutes=min(args.duration, 2)  # Limit stress test duration
        )
        print()
    
    if args.monitor_type in ['usage', 'all']:
        print("Running usage pattern monitoring...")
        results['usage_patterns'] = agent.monitor_endpoint_usage_patterns(duration_minutes=args.duration)
        print()
    
    # Export results
    agent.export_monitoring_report(results, args.output)
    
    print("✅ API Monitoring Complete!")
    print(f"📄 Report saved to: {args.output}")


if __name__ == '__main__':
    main()