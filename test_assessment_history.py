#!/usr/bin/env python3
"""
Test the /assessmenthistory/detail endpoint
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from property_api_service import PropertyAPIService

def test_assessment_history():
    """Test assessment history for both addresses"""
    addresses = [
        "4 Fiorenza Drive, Wilmington, MA 01887",
        "208 Ashmont St, Dorchester, MA 02124"
    ]
    
    service = PropertyAPIService()
    
    for address in addresses:
        print(f"\n🏛️ TESTING ASSESSMENT HISTORY")
        print("=" * 60)
        print(f"📍 Address: {address}")
        print()
        
        try:
            # First get raw data to inspect
            raw_data = service.get_assessment_history(address)
            print(f"🔍 FULL RAW RESPONSE:")
            print(f"   Keys: {list(raw_data.keys())}")
            if 'property' in raw_data:
                print(f"   Property count: {len(raw_data['property'])}")
                for i, prop in enumerate(raw_data['property'][:1]):
                    print(f"   Property {i+1} keys: {list(prop.keys())}")
            else:
                print(f"   Full response: {raw_data}")
            print()
            
            report = service.get_assessment_history_report(address)
            
            print("📊 ASSESSMENT HISTORY REPORT:")
            print("-" * 40)
            
            if 'error' in report:
                print(f"❌ Error: {report['error']}")
                continue
                
            print(f"📍 Address: {report['address']}")
            print(f"🏛️ Total Assessment Records: {report.get('total_assessments', 0)}")
            print(f"📅 Years Available: {', '.join(map(str, report.get('assessment_years', [])))}")
            
            # Show assessment records
            assessments = report.get('assessments', [])
            for i, assessment in enumerate(assessments[:5], 1):  # Show first 5 years
                print(f"\n📋 Assessment #{i} - Tax Year {assessment.get('tax_year')}:")
                print(f"   Total Assessed: {assessment.get('total_assessed_value')}")
                print(f"   Land Value: {assessment.get('land_value')}")
                print(f"   Improvement: {assessment.get('improvement_value')}")
                print(f"   Market Value: {assessment.get('market_value')}")
                print(f"   Tax Amount: {assessment.get('tax_amount')}")
                print(f"   Per Sq Ft: {assessment.get('assessed_per_sqft')}")
                
                # Show raw values for first record
                if i == 1:
                    print(f"   📊 RAW VALUES:")
                    print(f"      Raw Assessed: ${assessment.get('raw_total_assessed', 0):,}")
                    print(f"      Raw Land: ${assessment.get('raw_land_value', 0):,}")
                    print(f"      Raw Improvement: ${assessment.get('raw_improvement_value', 0):,}")
                    print(f"      Raw Tax: ${assessment.get('raw_tax_amount', 0):,}")
                    print(f"      Per Sq Ft: ${assessment.get('raw_assessed_per_sqft', 0):.2f}")
            
            if len(assessments) > 5:
                print(f"\n   ... and {len(assessments) - 5} more assessment records")
            
            print(f"\n⏰ Retrieved: {report.get('data_retrieved', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_assessment_history()