"""
Property API Service
Combines Attom's basic property profile with AVM history data
Provides a clean REST API interface for external consumers
"""

import requests
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List, Any
import json
from datetime import datetime

load_dotenv()

class PropertyAPIService:
    """
    Service that combines Attom property profile and AVM history data
    into a unified REST API response format
    """
    
    def __init__(self):
        self.api_key = os.environ.get('ATTOM_API_KEY')
        self.base_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"
        self.headers = {
            "accept": "application/json",
            "apikey": self.api_key
        }
        
        if not self.api_key:
            raise ValueError("ATTOM_API_KEY not found in environment variables")
    
    def parse_address(self, address: str) -> Dict[str, str]:
        """Parse address string into components for API calls"""
        parts = [part.strip() for part in address.split(',')]
        
        if len(parts) >= 3:
            street = parts[0]
            city = parts[1]
            state_zip = parts[2].split()
            state = state_zip[0] if state_zip else ""
            zip_code = state_zip[1] if len(state_zip) > 1 else ""
            
            return {
                'street': street,
                'city': city,
                'state': state,
                'zip': zip_code,
                'address1': street,
                'address2': f"{city}, {state} {zip_code}".strip()
            }
        else:
            return {
                'street': address,
                'city': '',
                'state': '',
                'zip': '',
                'address1': address,
                'address2': ''
            }
    
    def get_basic_profile(self, address: str) -> Optional[Dict]:
        """
        Get basic property profile from Attom API
        Uses the /property/basicprofile endpoint
        """
        print(f"🏠 Fetching basic profile for: {address}")
        
        address_parts = self.parse_address(address)
        
        try:
            url = f"{self.base_url}/property/basicprofile"
            
            params = {
                'address1': address_parts['address1'],
                'address2': address_parts['address2']
            }
            
            print(f"📡 Basic Profile API Request: {params}")
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"🔍 Basic Profile Response status: {data.get('status', {})}")
                
                if data and data.get('status', {}).get('total', 0) > 0:
                    print("✅ Basic profile retrieved")
                    return {
                        'success': True,
                        'data': data,
                        'status': data['status'],
                        'property': data.get('property', [])
                    }
                else:
                    print("❌ No basic profile found")
                    return {
                        'success': False,
                        'error': 'No basic profile found',
                        'status': data.get('status', {}),
                        'message': data.get('status', {}).get('msg', 'No data available')
                    }
            else:
                print(f"❌ Basic Profile API Error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f"Basic Profile API Error {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            print(f"❌ Basic profile request failed: {e}")
            return {
                'success': False,
                'error': 'Basic profile request failed',
                'details': str(e)
            }

    def get_avm_history(self, address: str) -> Optional[Dict]:
        """
        Get AVM (Automated Valuation Model) history from Attom API
        Uses the /avm/avmhistory/detail endpoint
        Based on: https://api.developer.attomdata.com/docs#!/Valuation32V1/AvmHistoryDetail
        """
        print(f"📈 Fetching AVM history for: {address}")
        
        address_parts = self.parse_address(address)
        
        try:
            # Using the endpoint you specified
            url = f"{self.base_url}/attomavm/detail"
            
            # Parameters based on the API docs
            params = {
                'address1': address_parts['address1'],
                'address2': address_parts['address2']
            }
            
            # Optional parameters you might want to add:
            # 'radiusvalue': '0.25',  # Search radius in miles
            # 'compcount': '10',      # Number of comparable properties
            # 'geoid': '',            # Geographic ID if available
            
            print(f"📡 AVM API Request: {params}")
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"🔍 AVM Response status: {data.get('status', {})}")
                
                if data and data.get('status', {}).get('total', 0) > 0:
                    print("✅ AVM history retrieved")
                    return {
                        'success': True,
                        'data': data,
                        'status': data['status'],
                        'avm_estimates': data.get('avm', []),
                        'comparable_sales': data.get('compSales', [])
                    }
                else:
                    print("❌ No AVM history found")
                    return {
                        'success': False,
                        'error': 'No AVM history found',
                        'status': data.get('status', {}),
                        'message': data.get('status', {}).get('msg', 'No data available')
                    }
            else:
                print(f"❌ AVM API Error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f"AVM API Error {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            print(f"❌ AVM request failed: {e}")
            return {
                'success': False,
                'error': 'AVM request failed',
                'details': str(e)
            }
    
    def clean_basic_profile_for_homeowners(self, profile_data: Dict) -> Dict:
        """
        Clean basic profile data into simple, homeowner-friendly format
        """
        try:
            if not profile_data.get('success'):
                return {
                    'error': profile_data.get('error', 'No basic profile data available'),
                    'address': 'Unknown',
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
            
            # Get the property data
            property_data = profile_data['data']['property'][0]
            
            # Extract simple, readable information
            cleaned_data = {
                'address': property_data['address']['oneLine'],
                'property_size': f"{property_data.get('building', {}).get('size', {}).get('universalsize', 'N/A'):,} sqft" if property_data.get('building', {}).get('size', {}).get('universalsize') else 'N/A',
                'year_built': property_data.get('summary', {}).get('yearbuilt', 'N/A'),
                'bedrooms': property_data.get('building', {}).get('rooms', {}).get('beds', 'N/A'),
                'bathrooms': property_data.get('building', {}).get('rooms', {}).get('bathstotal', 'N/A'),
                'lot_size': f"{property_data.get('lot', {}).get('lotsize1', 0):.2f} acres" if property_data.get('lot', {}).get('lotsize1') else 'N/A',
                'property_type': property_data.get('summary', {}).get('proptype', 'N/A'),
                'property_subtype': property_data.get('summary', {}).get('propsubtype', 'N/A'),
                'current_assessment': f"${property_data.get('assessment', {}).get('assessed', {}).get('assdttlvalue', 0):,}" if property_data.get('assessment', {}).get('assessed', {}).get('assdttlvalue') else 'N/A',
                'last_sale_price': f"${property_data.get('sale', {}).get('amount', {}).get('saleamt', 0):,}" if property_data.get('sale', {}).get('amount', {}).get('saleamt') else 'N/A',
                'last_sale_date': property_data.get('sale', {}).get('amount', {}).get('salerecdate', 'N/A'),
                'owner': property_data.get('owner', {}).get('owner1', {}).get('fullname', 'N/A'),
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return cleaned_data
            
        except Exception as e:
            return {
                'error': f'Could not process basic profile data: {str(e)}',
                'address': 'Unknown',
                'date': datetime.now().strftime('%Y-%m-%d')
            }

    def clean_data_for_homeowners(self, avm_data: Dict) -> Dict:
        """
        Clean AVM data into simple, homeowner-friendly format
        Perfect for CSV export or easy reading
        """
        try:
            if not avm_data.get('success'):
                return {
                    'error': avm_data.get('error', 'No data available'),
                    'address': 'Unknown',
                    'current_value': 'N/A',
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
            
            # Get the property data
            property_data = avm_data['data']['property'][0]
            
            # Extract simple, readable information
            cleaned_data = {
                'address': property_data['address']['oneLine'],
                'current_estimated_value': f"${property_data['avm']['amount']['value']:,}",
                'value_range_low': f"${property_data['avm']['amount']['low']:,}",
                'value_range_high': f"${property_data['avm']['amount']['high']:,}",
                'confidence_score': f"{property_data['avm']['amount']['scr']}/100",
                'estimate_date': property_data['avm']['eventDate'],
                'property_size': f"{property_data['building']['size']['universalsize']:,} sqft",
                'year_built': property_data['summary']['yearbuilt'],
                'bedrooms': property_data['building']['rooms']['beds'],
                'bathrooms': property_data['building']['rooms']['bathstotal'],
                'lot_size': f"{property_data['lot']['lotsize1']:.2f} acres",
                'last_sale_price': f"${property_data['sale']['amount']['saleamt']:,}",
                'last_sale_date': property_data['sale']['amount']['salerecdate'],
                'current_assessment': f"${property_data['assessment']['assessed']['assdttlvalue']:,}",
                'owner': property_data['owner']['owner1']['fullname'],
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return cleaned_data
            
        except Exception as e:
            return {
                'error': f'Could not process data: {str(e)}',
                'address': 'Unknown',
                'current_value': 'N/A',
                'date': datetime.now().strftime('%Y-%m-%d')
            }
    
    def get_basic_profile_report(self, address: str) -> Dict:
        """
        Complete workflow: Get basic profile data and clean it for homeowners
        """
        print(f"🏠 Getting basic profile report for: {address}")
        
        # Get basic profile data
        profile_result = self.get_basic_profile(address)
        
        # Clean it for homeowners
        clean_data = self.clean_basic_profile_for_homeowners(profile_result)
        
        return clean_data
    
    def get_property_report(self, address: str) -> Dict:
        """
        Complete workflow: Get AVM data and clean it for homeowners
        """
        print(f"🏠 Getting property report for: {address}")
        
        # Get AVM data
        avm_result = self.get_avm_history(address)
        
        # Clean it for homeowners
        clean_data = self.clean_data_for_homeowners(avm_result)
        
        return clean_data
    
    def get_combined_report(self, address: str) -> Dict:
        """
        Get both AVM and basic profile data, with AVM taking priority for valuation
        Falls back to basic profile if AVM is not available
        """
        print(f"🏠 Getting combined property report for: {address}")
        
        # Try AVM first (has valuation data)
        avm_result = self.get_avm_history(address)
        
        if avm_result.get('success'):
            print("✅ Using AVM data for valuation")
            return self.clean_data_for_homeowners(avm_result)
        else:
            print("⚠️ AVM not available, falling back to basic profile")
            profile_result = self.get_basic_profile(address)
            basic_data = self.clean_basic_profile_for_homeowners(profile_result)
            
            # Add a note about no valuation
            if not basic_data.get('error'):
                basic_data['valuation_note'] = 'No current market valuation available - showing basic property data only'
            
            return basic_data
    
    def get_complete_report(self, address: str) -> Dict:
        """
        Get both AVM and basic profile data regardless of availability
        Returns both datasets with clear indicators of what data is available
        """
        print(f"🏠 Getting complete property report (AVM + Basic Profile) for: {address}")
        
        # Get both datasets
        avm_result = self.get_avm_history(address)
        basic_result = self.get_basic_profile(address)
        
        # Build response with both datasets
        response = {
            'address': address,
            'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # AVM data section
        if avm_result.get('success'):
            print("✅ AVM data available")
            avm_clean = self.clean_data_for_homeowners(avm_result)
            response['avm'] = {
                'available': True,
                'current_estimated_value': avm_clean.get('current_estimated_value'),
                'value_range_low': avm_clean.get('value_range_low'),
                'value_range_high': avm_clean.get('value_range_high'),
                'confidence_score': avm_clean.get('confidence_score'),
                'estimate_date': avm_clean.get('estimate_date')
            }
            # Use AVM address as canonical
            response['address'] = avm_clean.get('address', address)
        else:
            print("❌ AVM data not available")
            response['avm'] = {
                'available': False,
                'error': avm_result.get('error', 'AVM data not available')
            }
        
        # Basic profile data section  
        if basic_result.get('success'):
            print("✅ Basic profile data available")
            basic_clean = self.clean_basic_profile_for_homeowners(basic_result)
            response['basic_profile'] = {
                'available': True,
                'property_size': basic_clean.get('property_size'),
                'year_built': basic_clean.get('year_built'),
                'bedrooms': basic_clean.get('bedrooms'),
                'bathrooms': basic_clean.get('bathrooms'),
                'lot_size': basic_clean.get('lot_size'),
                'property_type': basic_clean.get('property_type'),
                'property_subtype': basic_clean.get('property_subtype'),
                'last_sale_price': basic_clean.get('last_sale_price'),
                'last_sale_date': basic_clean.get('last_sale_date'),
                'current_assessment': basic_clean.get('current_assessment'),
                'owner': basic_clean.get('owner')
            }
            # Use basic profile address if AVM not available
            if not response['avm']['available']:
                response['address'] = basic_clean.get('address', address)
        else:
            print("❌ Basic profile data not available")
            response['basic_profile'] = {
                'available': False,
                'error': basic_result.get('error', 'Basic profile data not available')
            }
        
        return response


if __name__ == "__main__":
    print("🏠 Property Valuation Service")
    print("=" * 50)
    
    service = PropertyAPIService()
    
    while True:
        print("\n" + "=" * 50)
        print("Options:")
        print("1. Combined report (AVM + Basic Profile fallback)")
        print("2. AVM report only")
        print("3. Basic profile only")
        print("4. Quit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice in ['4', 'quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if choice not in ['1', '2', '3']:
            print("Please select a valid option (1-4)")
            continue
            
        print("\n📍 Address Format Examples:")
        print("  • 123 Main St, Boston, MA 02101")
        print("  • 456 Oak Ave, Springfield, IL 62701")
        print("  • 789 Elm Dr, Denver, CO 80202")
        print("  • Format: [Street Number] [Street Name], [City], [State] [ZIP]")
        
        address = input("\nEnter property address: ").strip()
        if not address:
            print("Please enter a valid address")
            continue
        
        # Basic address format validation
        if ',' not in address:
            print("⚠️  Address should include commas to separate street, city, and state/zip")
            print("   Example: 123 Main St, Boston, MA 02101")
            retry = input("Continue anyway? (y/n): ").strip().lower()
            if retry != 'y':
                continue
        
        print(f"\n📊 Getting property report...")
        
        if choice == '1':
            report = service.get_combined_report(address)
        elif choice == '2':
            report = service.get_property_report(address)
        elif choice == '3':
            report = service.get_basic_profile_report(address)
        
        print("\n" + "=" * 60)
        print("🏠 PROPERTY REPORT")
        print("=" * 60)
        
        if 'error' in report:
            print(f"❌ Error: {report['error']}")
        else:
            print(f"📍 Address: {report['address']}")
            
            # Show valuation data if available (AVM report)
            if 'current_estimated_value' in report:
                print(f"💰 Current Value: {report['current_estimated_value']}")
                print(f"📈 Value Range: {report['value_range_low']} - {report['value_range_high']}")
                print(f"🎯 Confidence: {report['confidence_score']}")
                print(f"📅 Estimate Date: {report['estimate_date']}")
            
            # Show basic property data (available in both reports)
            print(f"🏡 Size: {report['property_size']}")
            print(f"🗓️ Built: {report['year_built']}")
            print(f"🛏️ Bedrooms: {report['bedrooms']}")
            print(f"🚿 Bathrooms: {report['bathrooms']}")
            print(f"📐 Lot Size: {report['lot_size']}")
            
            # Show additional basic profile data if available
            if 'property_type' in report:
                print(f"🏠 Type: {report['property_type']}")
            if 'property_subtype' in report:
                print(f"📝 Subtype: {report['property_subtype']}")
            
            print(f"💵 Last Sale: {report['last_sale_price']} ({report['last_sale_date']})")
            print(f"🏛️ Assessment: {report['current_assessment']}")
            print(f"👤 Owner: {report['owner']}")
            
            # Show valuation note if present (fallback scenario)
            if 'valuation_note' in report:
                print(f"⚠️ Note: {report['valuation_note']}")
                
            print(f"⏰ Retrieved: {report['data_retrieved']}")
        
        # Ask if they want to see raw data
        show_raw = input("\nShow raw API data? (y/n): ").lower()
        if show_raw == 'y':
            print("\n" + "=" * 60)
            print("🔍 RAW API DATA")
            print("=" * 60)
            if choice == '2' or choice == '1':  # AVM data
                avm_result = service.get_avm_history(address)
                print("AVM Data:")
                print(json.dumps(avm_result, indent=2))
            if choice == '3' or choice == '1':  # Basic profile data
                profile_result = service.get_basic_profile(address)
                print("Basic Profile Data:")
                print(json.dumps(profile_result, indent=2))