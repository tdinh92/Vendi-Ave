#!/usr/bin/env python3
"""
Data Quality & Validation Agent
Specialized agent for analyzing data quality, consistency, and validation issues
Designed for APIs returning property data, financial data, and structured datasets
"""

import json
import requests
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import re
import statistics
from collections import Counter


class DataQualityAgent:
    """Agent for comprehensive data quality analysis and validation"""
    
    def __init__(self, api_base_url: str = "http://localhost:5000"):
        self.api_base_url = api_base_url.rstrip('/')
        self.quality_issues = []
        self.validation_rules = self._load_validation_rules()
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load data validation rules for property data"""
        return {
            'address_validation': {
                'required_fields': ['address'],
                'format_patterns': {
                    'address': r'^.+,\s*.+,\s*[A-Z]{2}\s*\d{5}.*$'  # Basic US address pattern
                }
            },
            'financial_validation': {
                'currency_fields': ['current_estimated_value', 'value_range_low', 'value_range_high', 
                                  'last_sale_price', 'current_assessment'],
                'currency_pattern': r'^\$[\d,]+$',
                'reasonable_ranges': {
                    'property_value': {'min': 10000, 'max': 50000000},
                    'tax_amount': {'min': 100, 'max': 500000},
                    'confidence_score': {'min': 0, 'max': 100}
                }
            },
            'property_validation': {
                'numeric_fields': ['bedrooms', 'bathrooms', 'year_built'],
                'size_fields': ['property_size', 'lot_size'],
                'date_fields': ['estimate_date', 'last_sale_date', 'data_retrieved'],
                'reasonable_ranges': {
                    'bedrooms': {'min': 0, 'max': 20},
                    'bathrooms': {'min': 0, 'max': 20},
                    'year_built': {'min': 1700, 'max': datetime.now().year + 2}
                }
            }
        }
    
    def analyze_data_quality(self, addresses: List[str], endpoints: List[str] = None) -> Dict[str, Any]:
        """Comprehensive data quality analysis across multiple addresses and endpoints"""
        if endpoints is None:
            endpoints = ['/property/combined', '/property/avm', '/property/basic', '/property/comprehensive']
        
        print(f"🔍 Starting data quality analysis...")
        print(f"🏘️  Addresses: {len(addresses)}")
        print(f"🔗 Endpoints: {len(endpoints)}")
        
        analysis_results = {
            'analysis_config': {
                'addresses_analyzed': len(addresses),
                'endpoints_tested': endpoints,
                'analysis_timestamp': datetime.now().isoformat()
            },
            'endpoint_analysis': {},
            'cross_endpoint_consistency': {},
            'data_completeness': {},
            'quality_score': 0
        }
        
        # Analyze each endpoint
        for endpoint in endpoints:
            print(f"\n📊 Analyzing endpoint: {endpoint}")
            endpoint_results = self._analyze_endpoint_quality(addresses, endpoint)
            analysis_results['endpoint_analysis'][endpoint] = endpoint_results
        
        # Cross-endpoint consistency analysis
        if len(endpoints) > 1:
            print(f"\n🔗 Analyzing cross-endpoint consistency...")
            consistency_results = self._analyze_cross_endpoint_consistency(addresses, endpoints)
            analysis_results['cross_endpoint_consistency'] = consistency_results
        
        # Overall data completeness
        completeness_results = self._analyze_data_completeness(analysis_results['endpoint_analysis'])
        analysis_results['data_completeness'] = completeness_results
        
        # Calculate overall quality score
        quality_score = self._calculate_overall_quality_score(analysis_results)
        analysis_results['quality_score'] = quality_score
        
        return analysis_results
    
    def _analyze_endpoint_quality(self, addresses: List[str], endpoint: str) -> Dict[str, Any]:
        """Analyze data quality for a specific endpoint"""
        responses = []
        validation_issues = []
        
        for address in addresses:
            try:
                if endpoint in ['/property/combined', '/property/avm', '/property/basic', '/property/comprehensive']:
                    response = requests.post(
                        f"{self.api_base_url}{endpoint}",
                        json={'address': address},
                        timeout=15
                    )
                else:
                    response = requests.get(f"{self.api_base_url}{endpoint}", timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    responses.append({
                        'address': address,
                        'data': data,
                        'response_code': 200
                    })
                    
                    # Validate this response
                    issues = self._validate_response_data(data, address, endpoint)
                    validation_issues.extend(issues)
                    
                else:
                    responses.append({
                        'address': address,
                        'error': f"HTTP {response.status_code}",
                        'response_code': response.status_code
                    })
                    validation_issues.append({
                        'address': address,
                        'issue_type': 'API_ERROR',
                        'severity': 'HIGH',
                        'description': f"HTTP {response.status_code} error"
                    })
                    
            except Exception as e:
                responses.append({
                    'address': address,
                    'error': str(e),
                    'response_code': None
                })
                validation_issues.append({
                    'address': address,
                    'issue_type': 'CONNECTION_ERROR',
                    'severity': 'HIGH',
                    'description': str(e)
                })
        
        # Analyze response patterns
        successful_responses = [r for r in responses if r.get('response_code') == 200]
        
        endpoint_analysis = {
            'total_requests': len(addresses),
            'successful_responses': len(successful_responses),
            'success_rate': (len(successful_responses) / len(addresses)) * 100 if addresses else 0,
            'validation_issues': validation_issues,
            'data_patterns': self._analyze_data_patterns(successful_responses),
            'field_completeness': self._analyze_field_completeness(successful_responses),
            'quality_metrics': self._calculate_endpoint_quality_metrics(successful_responses, validation_issues)
        }
        
        return endpoint_analysis
    
    def _validate_response_data(self, data: Dict, address: str, endpoint: str) -> List[Dict]:
        """Validate individual response data against quality rules"""
        issues = []
        
        # Address validation
        if 'address' in data:
            address_issues = self._validate_address_field(data['address'], address)
            issues.extend(address_issues)
        
        # Financial data validation
        financial_issues = self._validate_financial_fields(data, address)
        issues.extend(financial_issues)
        
        # Property data validation
        property_issues = self._validate_property_fields(data, address)
        issues.extend(property_issues)
        
        # Date validation
        date_issues = self._validate_date_fields(data, address)
        issues.extend(date_issues)
        
        # Missing required fields
        missing_field_issues = self._validate_required_fields(data, address, endpoint)
        issues.extend(missing_field_issues)
        
        return issues
    
    def _validate_address_field(self, response_address: str, input_address: str) -> List[Dict]:
        """Validate address field quality"""
        issues = []
        
        if not response_address or response_address.strip() == '':
            issues.append({
                'address': input_address,
                'issue_type': 'MISSING_ADDRESS',
                'severity': 'HIGH',
                'field': 'address',
                'description': 'Address field is empty or missing'
            })
        elif response_address == 'N/A':
            issues.append({
                'address': input_address,
                'issue_type': 'INVALID_ADDRESS',
                'severity': 'MEDIUM',
                'field': 'address',
                'description': 'Address field contains N/A value'
            })
        else:
            # Check address format (basic US address pattern)
            pattern = self.validation_rules['address_validation']['format_patterns']['address']
            if not re.match(pattern, response_address):
                issues.append({
                    'address': input_address,
                    'issue_type': 'ADDRESS_FORMAT',
                    'severity': 'LOW',
                    'field': 'address',
                    'description': f'Address format may be non-standard: {response_address}'
                })
        
        return issues
    
    def _validate_financial_fields(self, data: Dict, address: str) -> List[Dict]:
        """Validate financial fields (currency values)"""
        issues = []
        currency_fields = self.validation_rules['financial_validation']['currency_fields']
        currency_pattern = self.validation_rules['financial_validation']['currency_pattern']
        
        for field in currency_fields:
            if field in data:
                value = data[field]
                if value and value != 'N/A':
                    # Check currency format
                    if not re.match(currency_pattern, str(value)):
                        issues.append({
                            'address': address,
                            'issue_type': 'CURRENCY_FORMAT',
                            'severity': 'MEDIUM',
                            'field': field,
                            'description': f'Invalid currency format: {value}'
                        })
                    else:
                        # Check reasonable value ranges
                        numeric_value = float(str(value).replace('$', '').replace(',', ''))
                        if field in ['current_estimated_value', 'last_sale_price', 'current_assessment']:
                            ranges = self.validation_rules['financial_validation']['reasonable_ranges']['property_value']
                            if numeric_value < ranges['min'] or numeric_value > ranges['max']:
                                issues.append({
                                    'address': address,
                                    'issue_type': 'VALUE_OUT_OF_RANGE',
                                    'severity': 'LOW',
                                    'field': field,
                                    'description': f'Value may be unrealistic: {value}'
                                })
        
        return issues
    
    def _validate_property_fields(self, data: Dict, address: str) -> List[Dict]:
        """Validate property-specific fields"""
        issues = []
        numeric_fields = self.validation_rules['property_validation']['numeric_fields']
        ranges = self.validation_rules['property_validation']['reasonable_ranges']
        
        for field in numeric_fields:
            if field in data:
                value = data[field]
                if value is not None and value != 'N/A':
                    try:
                        numeric_value = float(value)
                        if field in ranges:
                            field_range = ranges[field]
                            if numeric_value < field_range['min'] or numeric_value > field_range['max']:
                                issues.append({
                                    'address': address,
                                    'issue_type': 'VALUE_OUT_OF_RANGE',
                                    'severity': 'MEDIUM',
                                    'field': field,
                                    'description': f'{field} value seems unrealistic: {value}'
                                })
                    except (ValueError, TypeError):
                        issues.append({
                            'address': address,
                            'issue_type': 'INVALID_NUMERIC',
                            'severity': 'MEDIUM',
                            'field': field,
                            'description': f'{field} should be numeric: {value}'
                        })
        
        # Validate size fields
        size_fields = self.validation_rules['property_validation']['size_fields']
        for field in size_fields:
            if field in data and data[field] and data[field] != 'N/A':
                value = str(data[field])
                # Check for proper size format (e.g., "2,500 sqft", "0.25 acres")
                if field == 'property_size' and 'sqft' not in value.lower():
                    issues.append({
                        'address': address,
                        'issue_type': 'FORMAT_ISSUE',
                        'severity': 'LOW',
                        'field': field,
                        'description': f'Property size missing unit: {value}'
                    })
                elif field == 'lot_size' and 'acres' not in value.lower() and 'sqft' not in value.lower():
                    issues.append({
                        'address': address,
                        'issue_type': 'FORMAT_ISSUE',
                        'severity': 'LOW',
                        'field': field,
                        'description': f'Lot size missing unit: {value}'
                    })
        
        return issues
    
    def _validate_date_fields(self, data: Dict, address: str) -> List[Dict]:
        """Validate date fields"""
        issues = []
        date_fields = self.validation_rules['property_validation']['date_fields']
        
        for field in date_fields:
            if field in data and data[field] and data[field] != 'N/A':
                date_value = str(data[field])
                
                # Check basic date format patterns
                date_patterns = [
                    r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
                    r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',  # YYYY-MM-DD HH:MM:SS
                    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO format
                ]
                
                if not any(re.match(pattern, date_value) for pattern in date_patterns):
                    issues.append({
                        'address': address,
                        'issue_type': 'DATE_FORMAT',
                        'severity': 'LOW',
                        'field': field,
                        'description': f'Date format may be non-standard: {date_value}'
                    })
        
        return issues
    
    def _validate_required_fields(self, data: Dict, address: str, endpoint: str) -> List[Dict]:
        """Validate that required fields are present"""
        issues = []
        
        # Define required fields by endpoint type
        required_fields_by_endpoint = {
            '/property/combined': ['address', 'data_retrieved'],
            '/property/avm': ['address', 'data_retrieved'],
            '/property/basic': ['address', 'data_retrieved'],
            '/property/comprehensive': ['address', 'analysis_type', 'data_sources']
        }
        
        if endpoint in required_fields_by_endpoint:
            required_fields = required_fields_by_endpoint[endpoint]
            
            for field in required_fields:
                if field not in data:
                    issues.append({
                        'address': address,
                        'issue_type': 'MISSING_REQUIRED_FIELD',
                        'severity': 'HIGH',
                        'field': field,
                        'description': f'Required field missing: {field}'
                    })
        
        return issues
    
    def _analyze_data_patterns(self, responses: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in successful responses"""
        if not responses:
            return {'no_data': True}
        
        # Count field presence
        field_counts = Counter()
        field_values = {}
        
        for response in responses:
            data = response['data']
            self._count_fields_recursive(data, field_counts, field_values, prefix='')
        
        # Calculate field presence percentages
        total_responses = len(responses)
        field_presence = {
            field: {'count': count, 'percentage': (count / total_responses) * 100}
            for field, count in field_counts.items()
        }
        
        return {
            'total_successful_responses': total_responses,
            'field_presence': field_presence,
            'common_fields': [f for f, stats in field_presence.items() if stats['percentage'] > 90],
            'rare_fields': [f for f, stats in field_presence.items() if stats['percentage'] < 10],
            'value_patterns': self._analyze_value_patterns(field_values)
        }
    
    def _count_fields_recursive(self, data: Any, field_counts: Counter, field_values: Dict, prefix: str):
        """Recursively count fields in nested data structures"""
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                field_counts[full_key] += 1
                
                if full_key not in field_values:
                    field_values[full_key] = []
                field_values[full_key].append(value)
                
                if isinstance(value, (dict, list)):
                    self._count_fields_recursive(value, field_counts, field_values, full_key)
        
        elif isinstance(data, list) and data:
            # For lists, analyze the first few items
            for i, item in enumerate(data[:3]):  # Limit to first 3 items
                item_prefix = f"{prefix}[{i}]"
                self._count_fields_recursive(item, field_counts, field_values, item_prefix)
    
    def _analyze_value_patterns(self, field_values: Dict) -> Dict[str, Any]:
        """Analyze patterns in field values"""
        patterns = {}
        
        for field, values in field_values.items():
            if len(values) > 1:  # Only analyze fields with multiple values
                # Remove None and 'N/A' values for analysis
                valid_values = [v for v in values if v is not None and v != 'N/A']
                
                if valid_values:
                    pattern_analysis = {
                        'total_values': len(values),
                        'valid_values': len(valid_values),
                        'null_or_na_count': len(values) - len(valid_values),
                        'unique_values': len(set(str(v) for v in valid_values)),
                        'data_type': self._determine_data_type(valid_values[0]) if valid_values else 'unknown'
                    }
                    
                    # Add type-specific analysis
                    if pattern_analysis['data_type'] == 'numeric':
                        numeric_values = [float(v) for v in valid_values if self._is_numeric(v)]
                        if numeric_values:
                            pattern_analysis['numeric_stats'] = {
                                'min': min(numeric_values),
                                'max': max(numeric_values),
                                'mean': statistics.mean(numeric_values),
                                'median': statistics.median(numeric_values)
                            }
                    
                    patterns[field] = pattern_analysis
        
        return patterns
    
    def _determine_data_type(self, value: Any) -> str:
        """Determine the data type of a value"""
        if self._is_numeric(value):
            return 'numeric'
        elif isinstance(value, str):
            if re.match(r'^\d{4}-\d{2}-\d{2}', str(value)):
                return 'date'
            elif re.match(r'^\$[\d,]+', str(value)):
                return 'currency'
            else:
                return 'string'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, (dict, list)):
            return 'complex'
        else:
            return 'unknown'
    
    def _is_numeric(self, value: Any) -> bool:
        """Check if a value is numeric"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _analyze_field_completeness(self, responses: List[Dict]) -> Dict[str, Any]:
        """Analyze how complete the data fields are"""
        if not responses:
            return {'no_data': True}
        
        field_completeness = {}
        total_responses = len(responses)
        
        for response in responses:
            data = response['data']
            self._analyze_completeness_recursive(data, field_completeness, '', total_responses)
        
        # Calculate completeness scores
        completeness_scores = {}
        for field, stats in field_completeness.items():
            non_empty_count = stats['total'] - stats['empty'] - stats['na']
            completeness_percentage = (non_empty_count / total_responses) * 100
            
            completeness_scores[field] = {
                'completeness_percentage': completeness_percentage,
                'total_responses': total_responses,
                'populated_responses': non_empty_count,
                'empty_responses': stats['empty'],
                'na_responses': stats['na']
            }
        
        return {
            'field_completeness_scores': completeness_scores,
            'highly_complete_fields': [f for f, s in completeness_scores.items() if s['completeness_percentage'] > 90],
            'poorly_complete_fields': [f for f, s in completeness_scores.items() if s['completeness_percentage'] < 50],
            'average_completeness': statistics.mean([s['completeness_percentage'] for s in completeness_scores.values()]) if completeness_scores else 0
        }
    
    def _analyze_completeness_recursive(self, data: Any, completeness_stats: Dict, prefix: str, total_responses: int):
        """Recursively analyze field completeness"""
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if full_key not in completeness_stats:
                    completeness_stats[full_key] = {'total': 0, 'empty': 0, 'na': 0}
                
                completeness_stats[full_key]['total'] += 1
                
                if value is None or value == '':
                    completeness_stats[full_key]['empty'] += 1
                elif str(value) == 'N/A':
                    completeness_stats[full_key]['na'] += 1
                
                if isinstance(value, dict):
                    self._analyze_completeness_recursive(value, completeness_stats, full_key, total_responses)
    
    def _calculate_endpoint_quality_metrics(self, responses: List[Dict], issues: List[Dict]) -> Dict[str, Any]:
        """Calculate quality metrics for an endpoint"""
        if not responses:
            return {'quality_score': 0, 'issues_per_response': float('inf')}
        
        total_responses = len(responses)
        total_issues = len(issues)
        
        # Count issues by severity
        high_issues = len([i for i in issues if i['severity'] == 'HIGH'])
        medium_issues = len([i for i in issues if i['severity'] == 'MEDIUM'])
        low_issues = len([i for i in issues if i['severity'] == 'LOW'])
        
        # Calculate weighted quality score (0-100)
        # Start with 100 and deduct points for issues
        quality_score = 100
        quality_score -= (high_issues * 10)    # -10 points per high severity issue
        quality_score -= (medium_issues * 5)   # -5 points per medium severity issue
        quality_score -= (low_issues * 1)      # -1 point per low severity issue
        
        quality_score = max(0, quality_score)  # Don't go below 0
        
        return {
            'quality_score': quality_score,
            'total_issues': total_issues,
            'issues_per_response': total_issues / total_responses,
            'issue_breakdown': {
                'high_severity': high_issues,
                'medium_severity': medium_issues,
                'low_severity': low_issues
            },
            'quality_rating': self._get_quality_rating(quality_score)
        }
    
    def _get_quality_rating(self, score: float) -> str:
        """Convert numeric quality score to rating"""
        if score >= 95:
            return 'Excellent'
        elif score >= 85:
            return 'Good'
        elif score >= 70:
            return 'Fair'
        elif score >= 50:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def _analyze_cross_endpoint_consistency(self, addresses: List[str], endpoints: List[str]) -> Dict[str, Any]:
        """Analyze consistency of data across different endpoints"""
        print("🔍 Checking cross-endpoint data consistency...")
        
        consistency_results = {
            'addresses_checked': 0,
            'consistency_issues': [],
            'field_consistency': {},
            'overall_consistency_score': 0
        }
        
        for address in addresses[:5]:  # Limit to first 5 addresses for performance
            endpoint_data = {}
            
            # Get data from each endpoint
            for endpoint in endpoints:
                try:
                    response = requests.post(
                        f"{self.api_base_url}{endpoint}",
                        json={'address': address},
                        timeout=10
                    )
                    if response.status_code == 200:
                        endpoint_data[endpoint] = response.json()
                except Exception as e:
                    print(f"Error getting {endpoint} data for {address}: {e}")
            
            # Compare common fields across endpoints
            if len(endpoint_data) >= 2:
                consistency_results['addresses_checked'] += 1
                issues = self._compare_endpoint_data(address, endpoint_data)
                consistency_results['consistency_issues'].extend(issues)
        
        # Calculate overall consistency score
        if consistency_results['addresses_checked'] > 0:
            total_checks = consistency_results['addresses_checked'] * len(endpoints) * (len(endpoints) - 1) / 2
            issue_count = len(consistency_results['consistency_issues'])
            consistency_score = max(0, 100 - (issue_count / total_checks) * 100)
            consistency_results['overall_consistency_score'] = consistency_score
        
        return consistency_results
    
    def _compare_endpoint_data(self, address: str, endpoint_data: Dict[str, Dict]) -> List[Dict]:
        """Compare data consistency between endpoints for a single address"""
        issues = []
        
        # Common fields that should be consistent across endpoints
        comparable_fields = ['address', 'property_size', 'year_built', 'bedrooms', 'bathrooms']
        
        endpoints = list(endpoint_data.keys())
        for i in range(len(endpoints)):
            for j in range(i + 1, len(endpoints)):
                endpoint1, endpoint2 = endpoints[i], endpoints[j]
                data1, data2 = endpoint_data[endpoint1], endpoint_data[endpoint2]
                
                for field in comparable_fields:
                    if field in data1 and field in data2:
                        val1, val2 = data1[field], data2[field]
                        
                        if val1 != val2 and val1 != 'N/A' and val2 != 'N/A':
                            # Check if it's a reasonable difference (for numeric fields)
                            if field in ['bedrooms', 'bathrooms', 'year_built']:
                                try:
                                    if abs(float(val1) - float(val2)) > 0.1:  # Allow small floating point differences
                                        issues.append({
                                            'address': address,
                                            'issue_type': 'INCONSISTENT_DATA',
                                            'severity': 'MEDIUM',
                                            'field': field,
                                            'description': f'{field} differs: {endpoint1}={val1}, {endpoint2}={val2}'
                                        })
                                except (ValueError, TypeError):
                                    issues.append({
                                        'address': address,
                                        'issue_type': 'INCONSISTENT_DATA',
                                        'severity': 'MEDIUM',
                                        'field': field,
                                        'description': f'{field} differs: {endpoint1}={val1}, {endpoint2}={val2}'
                                    })
                            else:
                                issues.append({
                                    'address': address,
                                    'issue_type': 'INCONSISTENT_DATA',
                                    'severity': 'LOW',
                                    'field': field,
                                    'description': f'{field} differs: {endpoint1}={val1}, {endpoint2}={val2}'
                                })
        
        return issues
    
    def _analyze_data_completeness(self, endpoint_analysis: Dict) -> Dict[str, Any]:
        """Analyze overall data completeness across all endpoints"""
        completeness_summary = {
            'endpoint_completeness': {},
            'overall_completeness_score': 0,
            'completeness_insights': []
        }
        
        endpoint_scores = []
        
        for endpoint, analysis in endpoint_analysis.items():
            if 'field_completeness' in analysis and 'average_completeness' in analysis['field_completeness']:
                avg_completeness = analysis['field_completeness']['average_completeness']
                completeness_summary['endpoint_completeness'][endpoint] = {
                    'average_completeness': avg_completeness,
                    'rating': self._get_completeness_rating(avg_completeness)
                }
                endpoint_scores.append(avg_completeness)
        
        if endpoint_scores:
            overall_score = statistics.mean(endpoint_scores)
            completeness_summary['overall_completeness_score'] = overall_score
            completeness_summary['completeness_insights'] = self._generate_completeness_insights(
                completeness_summary['endpoint_completeness'], overall_score
            )
        
        return completeness_summary
    
    def _get_completeness_rating(self, score: float) -> str:
        """Convert completeness score to rating"""
        if score >= 95:
            return 'Excellent'
        elif score >= 85:
            return 'Good'
        elif score >= 70:
            return 'Fair'
        elif score >= 50:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def _generate_completeness_insights(self, endpoint_completeness: Dict, overall_score: float) -> List[str]:
        """Generate insights about data completeness"""
        insights = []
        
        if overall_score >= 90:
            insights.append("Data completeness is excellent across all endpoints")
        elif overall_score >= 75:
            insights.append("Data completeness is good with minor gaps")
        elif overall_score >= 50:
            insights.append("Data completeness is moderate - some important fields may be missing")
        else:
            insights.append("Data completeness is poor - significant data gaps detected")
        
        # Find best and worst performing endpoints
        if len(endpoint_completeness) > 1:
            scores = [(ep, data['average_completeness']) for ep, data in endpoint_completeness.items()]
            best_endpoint = max(scores, key=lambda x: x[1])
            worst_endpoint = min(scores, key=lambda x: x[1])
            
            if best_endpoint[1] - worst_endpoint[1] > 20:
                insights.append(f"Significant completeness variation: {best_endpoint[0]} ({best_endpoint[1]:.1f}%) vs {worst_endpoint[0]} ({worst_endpoint[1]:.1f}%)")
        
        return insights
    
    def _calculate_overall_quality_score(self, analysis_results: Dict) -> Dict[str, Any]:
        """Calculate overall quality score combining all metrics"""
        scores = []
        
        # Collect endpoint quality scores
        for endpoint, analysis in analysis_results['endpoint_analysis'].items():
            if 'quality_metrics' in analysis and 'quality_score' in analysis['quality_metrics']:
                scores.append(analysis['quality_metrics']['quality_score'])
        
        # Include consistency score
        if 'cross_endpoint_consistency' in analysis_results:
            consistency_score = analysis_results['cross_endpoint_consistency'].get('overall_consistency_score', 0)
            scores.append(consistency_score)
        
        # Include completeness score
        if 'data_completeness' in analysis_results:
            completeness_score = analysis_results['data_completeness'].get('overall_completeness_score', 0)
            scores.append(completeness_score)
        
        if scores:
            overall_score = statistics.mean(scores)
            return {
                'overall_quality_score': overall_score,
                'quality_rating': self._get_quality_rating(overall_score),
                'component_scores': {
                    'endpoint_quality': statistics.mean([s for s in scores[:-2]]) if len(scores) > 2 else 0,
                    'data_consistency': consistency_score if 'consistency_score' in locals() else 0,
                    'data_completeness': completeness_score if 'completeness_score' in locals() else 0
                },
                'quality_insights': self._generate_quality_insights(overall_score, analysis_results)
            }
        else:
            return {'overall_quality_score': 0, 'quality_rating': 'No Data', 'quality_insights': ['No data available for quality assessment']}
    
    def _generate_quality_insights(self, overall_score: float, analysis_results: Dict) -> List[str]:
        """Generate overall quality insights"""
        insights = []
        
        # Overall assessment
        if overall_score >= 90:
            insights.append("Excellent data quality - API provides reliable, consistent data")
        elif overall_score >= 75:
            insights.append("Good data quality - minor issues detected but generally reliable")
        elif overall_score >= 60:
            insights.append("Moderate data quality - some issues may affect reliability")
        else:
            insights.append("Poor data quality - significant issues detected requiring attention")
        
        # Specific issue insights
        total_issues = sum(
            len(ep_analysis.get('validation_issues', []))
            for ep_analysis in analysis_results['endpoint_analysis'].values()
        )
        
        if total_issues > 0:
            insights.append(f"Total validation issues found: {total_issues}")
            
            # Count by severity
            high_issues = sum(
                len([i for i in ep_analysis.get('validation_issues', []) if i['severity'] == 'HIGH'])
                for ep_analysis in analysis_results['endpoint_analysis'].values()
            )
            
            if high_issues > 0:
                insights.append(f"Critical issues requiring immediate attention: {high_issues}")
        
        return insights
    
    def export_quality_report(self, quality_data: Dict, output_path: str = "data_quality_report.json"):
        """Export quality analysis results to JSON report"""
        quality_data['export_timestamp'] = datetime.now().isoformat()
        quality_data['agent_version'] = "1.0.0"
        
        with open(output_path, 'w') as f:
            json.dump(quality_data, f, indent=2, default=str)
        
        print(f"📄 Data quality report exported to: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="Data Quality & Validation Agent")
    parser.add_argument('--api-url', default='http://localhost:5000', help='API base URL')
    parser.add_argument('--addresses', nargs='+', required=True, help='Property addresses to analyze')
    parser.add_argument('--endpoints', nargs='+', 
                       default=['/property/combined', '/property/avm', '/property/basic'],
                       help='API endpoints to test')
    parser.add_argument('--output', default='data_quality_report.json', help='Output file path')
    
    args = parser.parse_args()
    
    agent = DataQualityAgent(args.api_url)
    
    print("🔍 Data Quality & Validation Agent Starting...")
    print(f"🌐 API URL: {args.api_url}")
    print(f"🏘️  Addresses: {len(args.addresses)}")
    print(f"🔗 Endpoints: {args.endpoints}")
    print()
    
    # Run comprehensive quality analysis
    results = agent.analyze_data_quality(args.addresses, args.endpoints)
    
    # Export results
    agent.export_quality_report(results, args.output)
    
    print("✅ Data Quality Analysis Complete!")
    print(f"📄 Report saved to: {args.output}")
    print(f"🎯 Overall Quality Score: {results.get('quality_score', {}).get('overall_quality_score', 0):.1f}/100")
    print(f"📊 Quality Rating: {results.get('quality_score', {}).get('quality_rating', 'Unknown')}")


if __name__ == '__main__':
    main()