#!/usr/bin/env python3
"""
Property Data Analysis Agent
Specialized agent for analyzing property data, market trends, and valuation accuracy
Designed for real estate APIs, property datasets, and market analysis
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import requests
import argparse
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns


class PropertyDataAgent:
    """Agent for comprehensive property data analysis and market insights"""
    
    def __init__(self, api_base_url: str = "http://localhost:5000"):
        self.api_base_url = api_base_url
        self.analysis_results = {}
        self.property_data = []
        self.market_trends = {}
        
    def analyze_property_portfolio(self, addresses: List[str]) -> Dict[str, Any]:
        """Analyze a portfolio of properties for investment insights"""
        print(f"🏠 Analyzing portfolio of {len(addresses)} properties...")
        
        portfolio_data = []
        failed_addresses = []
        
        for address in addresses:
            try:
                # Get comprehensive data for each property
                response = requests.post(
                    f"{self.api_base_url}/property/comprehensive",
                    json={"address": address},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    portfolio_data.append({
                        'address': address,
                        'data': data,
                        'analysis_date': datetime.now().isoformat()
                    })
                    print(f"✅ Analyzed: {address}")
                else:
                    failed_addresses.append(address)
                    print(f"❌ Failed: {address}")
                    
            except Exception as e:
                failed_addresses.append(address)
                print(f"❌ Error with {address}: {str(e)}")
        
        # Perform portfolio analysis
        analysis = self._analyze_portfolio_metrics(portfolio_data)
        analysis['failed_addresses'] = failed_addresses
        analysis['success_rate'] = len(portfolio_data) / len(addresses) * 100
        
        return analysis
    
    def _analyze_portfolio_metrics(self, portfolio_data: List[Dict]) -> Dict[str, Any]:
        """Calculate portfolio-level metrics and insights"""
        if not portfolio_data:
            return {'error': 'No valid property data found'}
        
        valuations = []
        assessments = []
        tax_amounts = []
        property_ages = []
        sizes = []
        
        for prop in portfolio_data:
            data = prop['data']
            
            # Extract AVM valuations
            if 'data_sources' in data and data['data_sources'].get('avm_valuation', {}).get('available'):
                avm_data = data['data_sources']['avm_valuation']['data']
                if 'current_estimated_value' in avm_data:
                    # Extract numeric value from "$1,234,567" format
                    val_str = avm_data['current_estimated_value'].replace('$', '').replace(',', '')
                    try:
                        valuations.append(float(val_str))
                    except:
                        pass
            
            # Extract assessment data
            if 'data_sources' in data and data['data_sources'].get('assessment_history', {}).get('available'):
                hist_data = data['data_sources']['assessment_history']['data']
                if hist_data.get('assessments'):
                    latest = hist_data['assessments'][0]  # Most recent
                    try:
                        assess_val = latest.get('raw_total_assessed', 0)
                        tax_val = latest.get('raw_tax_amount', 0)
                        if assess_val > 0:
                            assessments.append(assess_val)
                        if tax_val > 0:
                            tax_amounts.append(tax_val)
                    except:
                        pass
            
            # Extract property characteristics
            if 'data_sources' in data and data['data_sources'].get('avm_valuation', {}).get('available'):
                avm_data = data['data_sources']['avm_valuation']['data']
                if avm_data.get('year_built'):
                    try:
                        age = 2024 - int(avm_data['year_built'])
                        property_ages.append(age)
                    except:
                        pass
                
                if avm_data.get('property_size'):
                    size_str = avm_data['property_size'].replace(',', '').replace(' sqft', '')
                    try:
                        sizes.append(float(size_str))
                    except:
                        pass
        
        # Calculate portfolio metrics
        metrics = {
            'portfolio_size': len(portfolio_data),
            'analysis_date': datetime.now().isoformat(),
            'valuation_metrics': self._calculate_stats(valuations, 'AVM Valuations'),
            'assessment_metrics': self._calculate_stats(assessments, 'Tax Assessments'),
            'tax_metrics': self._calculate_stats(tax_amounts, 'Annual Taxes'),
            'property_age_metrics': self._calculate_stats(property_ages, 'Property Ages'),
            'size_metrics': self._calculate_stats(sizes, 'Property Sizes'),
            'investment_insights': self._generate_investment_insights(
                valuations, assessments, tax_amounts, property_ages, sizes
            )
        }
        
        return metrics
    
    def _calculate_stats(self, values: List[float], metric_name: str) -> Dict[str, Any]:
        """Calculate statistical metrics for a list of values"""
        if not values:
            return {'error': f'No {metric_name} data available'}
        
        values = [v for v in values if v is not None and v > 0]  # Filter valid values
        
        if not values:
            return {'error': f'No valid {metric_name} data'}
        
        return {
            'count': len(values),
            'mean': np.mean(values),
            'median': np.median(values),
            'std_dev': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'total': np.sum(values),
            'percentile_25': np.percentile(values, 25),
            'percentile_75': np.percentile(values, 75)
        }
    
    def _generate_investment_insights(self, valuations: List[float], assessments: List[float], 
                                    taxes: List[float], ages: List[float], sizes: List[float]) -> Dict[str, Any]:
        """Generate investment insights based on portfolio data"""
        insights = {}
        
        # Valuation vs Assessment Analysis
        if valuations and assessments:
            val_assess_ratios = [v/a for v, a in zip(valuations, assessments) if a > 0]
            if val_assess_ratios:
                avg_ratio = np.mean(val_assess_ratios)
                insights['valuation_assessment_ratio'] = {
                    'average_ratio': avg_ratio,
                    'interpretation': 'Properties valued above assessment' if avg_ratio > 1.1 else 
                                   'Properties valued below assessment' if avg_ratio < 0.9 else 
                                   'Properties fairly assessed'
                }
        
        # Tax Efficiency Analysis
        if taxes and valuations:
            tax_rates = [(t/v)*100 for t, v in zip(taxes, valuations) if v > 0]
            if tax_rates:
                insights['tax_efficiency'] = {
                    'average_tax_rate_percent': np.mean(tax_rates),
                    'tax_burden_analysis': 'High tax burden' if np.mean(tax_rates) > 2.0 else
                                         'Low tax burden' if np.mean(tax_rates) < 1.0 else
                                         'Moderate tax burden'
                }
        
        # Property Age Diversification
        if ages:
            age_diversity = np.std(ages)
            insights['age_diversification'] = {
                'age_diversity_score': age_diversity,
                'portfolio_vintage': 'Well diversified' if age_diversity > 15 else 'Similar age properties'
            }
        
        # Size Distribution
        if sizes:
            size_diversity = np.std(sizes)
            insights['size_diversification'] = {
                'size_diversity_score': size_diversity,
                'portfolio_composition': 'Diverse property sizes' if size_diversity > 500 else 'Similar sized properties'
            }
        
        return insights
    
    def analyze_market_trends(self, addresses: List[str], years_back: int = 5) -> Dict[str, Any]:
        """Analyze market trends using assessment history data"""
        print(f"📊 Analyzing market trends for {len(addresses)} properties over {years_back} years...")
        
        all_assessments = []
        
        for address in addresses:
            try:
                response = requests.post(
                    f"{self.api_base_url}/property/assessmenthistory",
                    json={"address": address},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('assessments'):
                        for assessment in data['assessments']:
                            all_assessments.append({
                                'address': address,
                                'year': int(assessment['tax_year']),
                                'assessed_value': assessment.get('raw_total_assessed', 0),
                                'tax_amount': assessment.get('raw_tax_amount', 0),
                                'value_per_sqft': assessment.get('raw_assessed_per_sqft', 0)
                            })
                    print(f"✅ Retrieved trends for: {address}")
                else:
                    print(f"❌ Failed to get trends for: {address}")
                    
            except Exception as e:
                print(f"❌ Error with {address}: {str(e)}")
        
        if not all_assessments:
            return {'error': 'No assessment data found for trend analysis'}
        
        # Analyze trends
        trends = self._calculate_market_trends(all_assessments)
        return trends
    
    def _calculate_market_trends(self, assessments: List[Dict]) -> Dict[str, Any]:
        """Calculate market trend metrics"""
        df = pd.DataFrame(assessments)
        
        if df.empty:
            return {'error': 'No data for trend calculation'}
        
        # Group by year and calculate averages
        yearly_trends = df.groupby('year').agg({
            'assessed_value': ['mean', 'median', 'count'],
            'tax_amount': ['mean', 'median'],
            'value_per_sqft': ['mean', 'median']
        }).round(2)
        
        # Calculate year-over-year growth rates
        yearly_avg = df.groupby('year')['assessed_value'].mean().sort_index()
        growth_rates = yearly_avg.pct_change().dropna() * 100
        
        # Market trend analysis
        recent_growth = growth_rates.tail(3).mean() if len(growth_rates) >= 3 else 0
        
        trends = {
            'analysis_period': f"{yearly_avg.index.min()} - {yearly_avg.index.max()}",
            'total_properties_analyzed': len(df['address'].unique()),
            'yearly_summary': yearly_trends.to_dict(),
            'growth_analysis': {
                'average_annual_growth_rate': growth_rates.mean(),
                'recent_3year_growth_rate': recent_growth,
                'highest_growth_year': growth_rates.idxmax() if not growth_rates.empty else None,
                'highest_growth_rate': growth_rates.max() if not growth_rates.empty else 0
            },
            'market_insights': self._generate_market_insights(growth_rates, yearly_avg)
        }
        
        return trends
    
    def _generate_market_insights(self, growth_rates: pd.Series, yearly_values: pd.Series) -> List[str]:
        """Generate market insights based on trend analysis"""
        insights = []
        
        if not growth_rates.empty:
            avg_growth = growth_rates.mean()
            
            if avg_growth > 5:
                insights.append("Strong market appreciation - properties gaining value rapidly")
            elif avg_growth > 2:
                insights.append("Steady market growth - consistent property value increases")
            elif avg_growth > 0:
                insights.append("Slow market growth - minimal property value gains")
            else:
                insights.append("Market decline - property values decreasing")
            
            # Volatility analysis
            volatility = growth_rates.std()
            if volatility > 10:
                insights.append("High market volatility - significant year-to-year fluctuations")
            elif volatility > 5:
                insights.append("Moderate market volatility - some year-to-year variation")
            else:
                insights.append("Stable market - consistent growth pattern")
            
            # Recent trend analysis
            if len(growth_rates) >= 3:
                recent_trend = growth_rates.tail(3).mean()
                overall_trend = growth_rates.mean()
                
                if recent_trend > overall_trend + 2:
                    insights.append("Accelerating market - recent growth exceeds historical average")
                elif recent_trend < overall_trend - 2:
                    insights.append("Slowing market - recent growth below historical average")
        
        return insights
    
    def generate_valuation_accuracy_report(self, addresses: List[str]) -> Dict[str, Any]:
        """Compare AVM valuations with tax assessments to analyze accuracy"""
        print(f"🎯 Generating valuation accuracy report for {len(addresses)} properties...")
        
        comparisons = []
        
        for address in addresses:
            try:
                # Get both AVM and assessment data
                response = requests.post(
                    f"{self.api_base_url}/property/complete",
                    json={"address": address},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    comparison = self._extract_valuation_comparison(address, data)
                    if comparison:
                        comparisons.append(comparison)
                        print(f"✅ Compared valuations for: {address}")
                
            except Exception as e:
                print(f"❌ Error with {address}: {str(e)}")
        
        if not comparisons:
            return {'error': 'No valuation comparisons available'}
        
        # Analyze accuracy metrics
        accuracy_analysis = self._analyze_valuation_accuracy(comparisons)
        return accuracy_analysis
    
    def _extract_valuation_comparison(self, address: str, data: Dict) -> Optional[Dict]:
        """Extract AVM vs assessment comparison data"""
        comparison = {'address': address}
        
        # Extract AVM valuation
        if ('avm_data' in data and data['avm_data'].get('available') and 
            'current_estimated_value' in data['avm_data']):
            avm_str = data['avm_data']['current_estimated_value'].replace('$', '').replace(',', '')
            try:
                comparison['avm_value'] = float(avm_str)
            except:
                return None
        else:
            return None
        
        # Extract assessment value
        if ('basic_profile_data' in data and data['basic_profile_data'].get('available') and
            'current_assessment' in data['basic_profile_data']):
            assess_str = data['basic_profile_data']['current_assessment'].replace('$', '').replace(',', '')
            try:
                comparison['assessment_value'] = float(assess_str)
            except:
                return None
        else:
            return None
        
        # Calculate comparison metrics
        if comparison.get('avm_value') and comparison.get('assessment_value'):
            comparison['difference'] = comparison['avm_value'] - comparison['assessment_value']
            comparison['percentage_difference'] = (comparison['difference'] / comparison['assessment_value']) * 100
            comparison['ratio'] = comparison['avm_value'] / comparison['assessment_value']
            return comparison
        
        return None
    
    def _analyze_valuation_accuracy(self, comparisons: List[Dict]) -> Dict[str, Any]:
        """Analyze AVM valuation accuracy against assessments"""
        differences = [c['difference'] for c in comparisons]
        percentages = [c['percentage_difference'] for c in comparisons]
        ratios = [c['ratio'] for c in comparisons]
        
        # Calculate accuracy metrics
        accuracy_metrics = {
            'total_comparisons': len(comparisons),
            'average_difference': np.mean(differences),
            'median_difference': np.median(differences),
            'average_percentage_difference': np.mean(percentages),
            'median_percentage_difference': np.median(percentages),
            'standard_deviation_percentage': np.std(percentages),
            'properties_overvalued': len([p for p in percentages if p > 10]),
            'properties_undervalued': len([p for p in percentages if p < -10]),
            'properties_fairly_valued': len([p for p in percentages if -10 <= p <= 10]),
            'accuracy_insights': self._generate_accuracy_insights(percentages, ratios)
        }
        
        return accuracy_metrics
    
    def _generate_accuracy_insights(self, percentages: List[float], ratios: List[float]) -> List[str]:
        """Generate insights about AVM accuracy"""
        insights = []
        
        avg_percentage = np.mean(percentages)
        std_percentage = np.std(percentages)
        
        # Overall accuracy assessment
        if abs(avg_percentage) < 5:
            insights.append("AVM shows excellent accuracy - average difference under 5%")
        elif abs(avg_percentage) < 10:
            insights.append("AVM shows good accuracy - average difference under 10%")
        else:
            insights.append("AVM shows moderate accuracy - significant differences from assessments")
        
        # Bias analysis
        if avg_percentage > 5:
            insights.append("AVM tends to overvalue properties compared to tax assessments")
        elif avg_percentage < -5:
            insights.append("AVM tends to undervalue properties compared to tax assessments")
        else:
            insights.append("AVM shows minimal bias - balanced over and under valuations")
        
        # Consistency analysis
        if std_percentage < 10:
            insights.append("AVM provides consistent valuations - low variation in accuracy")
        elif std_percentage < 20:
            insights.append("AVM shows moderate consistency in valuations")
        else:
            insights.append("AVM shows high variation in accuracy - inconsistent valuations")
        
        return insights
    
    def export_analysis_report(self, analysis_data: Dict, output_path: str = "property_analysis_report.json"):
        """Export analysis results to JSON report"""
        analysis_data['export_timestamp'] = datetime.now().isoformat()
        analysis_data['agent_version'] = "1.0.0"
        
        with open(output_path, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        print(f"📄 Analysis report exported to: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="Property Data Analysis Agent")
    parser.add_argument('--api-url', default='http://localhost:5000', help='API base URL')
    parser.add_argument('--addresses', nargs='+', required=True, help='Property addresses to analyze')
    parser.add_argument('--analysis-type', choices=['portfolio', 'trends', 'accuracy', 'all'], 
                       default='all', help='Type of analysis to perform')
    parser.add_argument('--output', default='property_analysis_report.json', help='Output file path')
    
    args = parser.parse_args()
    
    agent = PropertyDataAgent(args.api_url)
    
    print("🏠 Property Data Analysis Agent Starting...")
    print(f"📍 API URL: {args.api_url}")
    print(f"🏘️  Addresses: {len(args.addresses)} properties")
    print(f"📊 Analysis Type: {args.analysis_type}")
    print()
    
    results = {
        'analysis_configuration': {
            'addresses': args.addresses,
            'analysis_type': args.analysis_type,
            'api_url': args.api_url
        }
    }
    
    if args.analysis_type in ['portfolio', 'all']:
        print("Running portfolio analysis...")
        results['portfolio_analysis'] = agent.analyze_property_portfolio(args.addresses)
        print()
    
    if args.analysis_type in ['trends', 'all']:
        print("Running market trends analysis...")
        results['market_trends'] = agent.analyze_market_trends(args.addresses)
        print()
    
    if args.analysis_type in ['accuracy', 'all']:
        print("Running valuation accuracy analysis...")
        results['valuation_accuracy'] = agent.generate_valuation_accuracy_report(args.addresses)
        print()
    
    # Export results
    agent.export_analysis_report(results, args.output)
    
    print("✅ Property Data Analysis Complete!")
    print(f"📄 Report saved to: {args.output}")


if __name__ == '__main__':
    main()