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
        Get complete property report with both AVM and Basic Profile data
        Returns both datasets with availability flags
        """
        print(f"🏠 Getting complete property report for: {address}")
        
        # Get both datasets
        avm_result = self.get_avm_history(address)
        profile_result = self.get_basic_profile(address)
        
        # Clean both datasets
        avm_clean = self.clean_data_for_homeowners(avm_result) if avm_result.get('success') else None
        profile_clean = self.clean_basic_profile_for_homeowners(profile_result) if profile_result.get('success') else None
        
        # Build response with availability flags
        response = {
            'avm': {
                'available': avm_result.get('success', False),
                'data': avm_clean if avm_clean and 'error' not in avm_clean else None,
                'error': avm_clean.get('error') if avm_clean and 'error' in avm_clean else avm_result.get('error')
            },
            'basic_profile': {
                'available': profile_result.get('success', False), 
                'data': profile_clean if profile_clean and 'error' not in profile_clean else None,
                'error': profile_clean.get('error') if profile_clean and 'error' in profile_clean else profile_result.get('error')
            },
            'address': address,
            'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return response

    def get_all_events_snapshot(self, address: str) -> Optional[Dict]:
        """
        Get comprehensive property event snapshot from Attom API
        Uses the /allevents/snapshot endpoint
        """
        print(f"🎯 Fetching all events snapshot for: {address}")
        
        address_parts = self.parse_address(address)
        
        try:
            url = f"{self.base_url}/allevents/snapshot"
            
            params = {
                'address1': address_parts['address1'],
                'address2': address_parts['address2']
            }
            
            print(f"📡 All Events API Request: {params}")
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"🔍 All Events Response status: {data.get('status', {})}")
                
                if data and data.get('status', {}).get('total', 0) > 0:
                    print("✅ All events snapshot retrieved")
                    return {
                        'success': True,
                        'data': data,
                        'status': data['status'],
                        'property_events': data.get('property', [])
                    }
                else:
                    print("❌ No events found")
                    return {
                        'success': False,
                        'error': 'No events found',
                        'status': data.get('status', {}),
                        'message': data.get('status', {}).get('msg', 'No event data available')
                    }
            else:
                print(f"❌ All Events API Error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f"All Events API Error {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            print(f"❌ All events request failed: {e}")
            return {
                'success': False,
                'error': 'All events request failed',
                'details': str(e)
            }
    
    def clean_all_events_for_homeowners(self, events_data: Dict) -> Dict:
        """
        Clean all events data into homeowner-friendly format with raw assessment data preservation
        """
        try:
            if not events_data.get('success'):
                return {
                    'error': events_data.get('error', 'No events data available'),
                    'address': 'Unknown',
                    'total_events': 0,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
            
            # Get the property data
            property_data = events_data['data']['property'][0]
            address = property_data['address']['oneLine']
            
            # For the current format, we extract assessment data directly from the main structure
            cleaned_events = {}
            total_events = 0
            
            # Extract assessment data from the main property structure
            if 'assessment' in property_data:
                assessment = property_data['assessment']
                assessment_events = []
                
                # Create a single assessment record from the current data
                if 'assessed' in assessment or 'tax' in assessment:
                    assessed = assessment.get('assessed', {})
                    tax = assessment.get('tax', {})
                    
                    assessment_record = {
                        'year': str(tax.get('taxyear', 'N/A')),
                        'total_value': f"${assessed.get('assdttlvalue', 0):,}" if assessed.get('assdttlvalue') else 'N/A',
                        'land_value': f"${assessed.get('assdlandvalue', 0):,}" if assessed.get('assdlandvalue') else 'N/A',
                        'improvement_value': f"${assessed.get('assdimprvalue', 0):,}" if assessed.get('assdimprvalue') else 'N/A',
                        'tax_amount': f"${tax.get('taxamt', 0):,}" if tax.get('taxamt') else 'N/A',
                        'per_sq_ft': f"${assessed.get('assdttlpersizeunit', 0):.2f}" if assessed.get('assdttlpersizeunit') else 'N/A',
                        
                        # Raw values for analysis
                        'raw_assessed_value': assessed.get('assdttlvalue', 0),
                        'raw_land_value': assessed.get('assdlandvalue', 0), 
                        'raw_improvement_value': assessed.get('assdimprvalue', 0),
                        'raw_tax_amount': tax.get('taxamt', 0),
                        'raw_per_sq_ft': assessed.get('assdttlpersizeunit', 0),
                        'raw_tax_per_sq_ft': tax.get('taxpersizeunit', 0)
                    }
                    
                    assessment_events.append(assessment_record)
                    total_events += 1
                    
                cleaned_events['assessments'] = assessment_events
            
            # Extract sale data 
            if 'sale' in property_data:
                sale = property_data['sale']
                sale_events = []
                
                if 'amount' in sale and sale['amount'].get('saleamt'):
                    amount = sale['amount']
                    sale_record = {
                        'date': amount.get('salerecdate', 'N/A'),
                        'price': f"${amount.get('saleamt', 0):,}" if amount.get('saleamt') else 'N/A',
                        'document_type': amount.get('saledoctype', 'N/A'),
                        'transaction_type': amount.get('saletranstype', 'N/A'),
                        'raw_sale_amount': amount.get('saleamt', 0)
                    }
                    sale_events.append(sale_record)
                    total_events += 1
                
                if sale_events:
                    cleaned_events['sales'] = sale_events
            
            # Current snapshot from property data
            current_snapshot = {}
            if 'summary' in property_data:
                summary = property_data['summary']
                building = property_data.get('building', {})
                lot = property_data.get('lot', {})
                
                current_snapshot = {
                    'property_type': summary.get('propertyType', 'N/A'),
                    'year_built': summary.get('yearbuilt', 'N/A'),
                    'size_sqft': building.get('size', {}).get('universalsize', 'N/A'),
                    'bedrooms': building.get('rooms', {}).get('beds', 'N/A'),
                    'bathrooms': building.get('rooms', {}).get('bathstotal', 'N/A'),
                    'lot_size_acres': lot.get('lotSize1', 'N/A')
                }
                
                # Add AVM data if available
                if 'avm' in property_data:
                    avm = property_data['avm']
                    amount = avm.get('amount', {})
                    current_snapshot['avm'] = {
                        'estimated_value': f"${amount.get('value', 0):,}" if amount.get('value') else 'N/A',
                        'confidence_score': f"{amount.get('scr', 0)}/100" if amount.get('scr') else 'N/A',
                        'value_range': f"${amount.get('low', 0):,} - ${amount.get('high', 0):,}" if amount.get('low') and amount.get('high') else 'N/A',
                        'raw_estimated_value': amount.get('value', 0),
                        'raw_confidence_score': amount.get('scr', 0)
                    }
            
            # Build final response
            cleaned_data = {
                'address': address,
                'total_events': total_events,
                'event_categories': len([k for k, v in cleaned_events.items() if v]),
                'events': cleaned_events,
                'current_snapshot': current_snapshot,
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return cleaned_data
            
        except Exception as e:
            return {
                'error': f'Could not process all events data: {str(e)}',
                'address': 'Unknown',
                'total_events': 0,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
    
    def get_all_events_report(self, address: str) -> Dict:
        """
        Complete workflow: Get all events data and clean it for homeowners
        """
        print(f"🎯 Getting comprehensive events report for: {address}")
        
        # Get all events data
        events_result = self.get_all_events_snapshot(address)
        
        # Clean it for homeowners
        clean_data = self.clean_all_events_for_homeowners(events_result)
        
        return clean_data

    def get_assessment_history(self, address: str) -> Optional[Dict]:
        """
        Get historical assessment data from Attom API
        Uses the /assessmenthistory/detail endpoint
        """
        print(f"🏛️ Fetching assessment history for: {address}")
        
        address_parts = self.parse_address(address)
        
        try:
            url = f"{self.base_url}/assessmenthistory/detail"
            
            params = {
                'address1': address_parts['address1'],
                'address2': address_parts['address2']
            }
            
            print(f"📡 Assessment History API Request: {params}")
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"🔍 Assessment History Response status: {data.get('status', {})}")
                
                if data and data.get('status', {}).get('total', 0) > 0:
                    print("✅ Assessment history retrieved")
                    return {
                        'success': True,
                        'data': data,
                        'status': data['status'],
                        'assessments': data.get('property', [])
                    }
                else:
                    print("❌ No assessment history found")
                    return {
                        'success': False,
                        'error': 'No assessment history found',
                        'status': data.get('status', {}),
                        'message': data.get('status', {}).get('msg', 'No assessment data available')
                    }
            else:
                print(f"❌ Assessment History API Error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f"Assessment History API Error {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            print(f"❌ Assessment history request failed: {e}")
            return {
                'success': False,
                'error': 'Assessment history request failed',
                'details': str(e)
            }
    
    def clean_assessment_history_for_homeowners(self, assessment_data: Dict) -> Dict:
        """
        Clean assessment history data into homeowner-friendly format with raw values
        """
        try:
            if not assessment_data.get('success'):
                return {
                    'error': assessment_data.get('error', 'No assessment data available'),
                    'address': 'Unknown',
                    'total_assessments': 0,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
            
            # Get the property data
            property_data = assessment_data['data']['property'][0]
            address = property_data['address']['oneLine']
            
            # Get building size for per sqft calculations
            building_size = 0
            if 'building' in property_data and 'size' in property_data['building']:
                size_data = property_data['building']['size']
                building_size = size_data.get('bldgSize') or size_data.get('universalSize') or size_data.get('livingSize', 0)
            
            # Extract assessment history
            assessment_records = []
            
            # Look for assessment data in various possible locations
            if 'assessmenthistory' in property_data:
                assessments = property_data['assessmenthistory']
                
                # Handle both single assessment and array of assessments
                if isinstance(assessments, list):
                    assessment_list = assessments
                else:
                    assessment_list = [assessments]
                
                for assessment in assessment_list:
                    if isinstance(assessment, dict):
                        # Extract assessment data
                        assessed = assessment.get('assessed', {})
                        market = assessment.get('market', {})
                        tax = assessment.get('tax', {})
                        appraised = assessment.get('appraised', {})
                        
                        # Determine the year
                        year = (tax.get('taxYear') or 
                               tax.get('assessorYear') or 
                               assessment.get('assessmentYear') or 
                               assessment.get('year') or 'N/A')
                        
                        assessment_record = {
                            'tax_year': str(year),
                            'assessment_year': str(year),
                            
                            # Formatted values
                            'total_assessed_value': f"${assessed.get('assdTtlValue', 0):,}" if assessed.get('assdTtlValue') else 'N/A',
                            'land_value': f"${assessed.get('assdLandValue', 0):,}" if assessed.get('assdLandValue') else 'N/A',
                            'improvement_value': f"${assessed.get('assdImprValue', 0):,}" if assessed.get('assdImprValue') else 'N/A',
                            'market_value': f"${market.get('mktTtlValue', 0):,}" if market.get('mktTtlValue') else 'N/A',
                            'appraised_value': f"${appraised.get('apprTtlValue', 0):,}" if appraised.get('apprTtlValue') else 'N/A',
                            'tax_amount': f"${tax.get('taxAmt', 0):,}" if tax.get('taxAmt') else 'N/A',
                            
                            # Per square foot rates (calculated if size available)
                            'assessed_per_sqft': f"${assessed.get('assdTtlValue', 0) / building_size:.2f}" if building_size > 0 and assessed.get('assdTtlValue') else 'N/A',
                            'market_per_sqft': f"${market.get('mktTtlValue', 0) / building_size:.2f}" if building_size > 0 and market.get('mktTtlValue') else 'N/A',
                            'tax_per_sqft': f"${tax.get('taxAmt', 0) / building_size:.2f}" if building_size > 0 and tax.get('taxAmt') else 'N/A',
                            
                            # Raw values for analysis
                            'raw_total_assessed': assessed.get('assdTtlValue', 0),
                            'raw_land_value': assessed.get('assdLandValue', 0),
                            'raw_improvement_value': assessed.get('assdImprValue', 0),
                            'raw_market_value': market.get('mktTtlValue', 0),
                            'raw_appraised_value': appraised.get('apprTtlValue', 0),
                            'raw_tax_amount': tax.get('taxAmt', 0),
                            'raw_assessed_per_sqft': assessed.get('assdTtlValue', 0) / building_size if building_size > 0 else 0,
                            'raw_market_per_sqft': market.get('mktTtlValue', 0) / building_size if building_size > 0 else 0,
                            'raw_tax_per_sqft': tax.get('taxAmt', 0) / building_size if building_size > 0 else 0,
                            
                            # Additional details
                            'mill_rate': tax.get('millrate', 'N/A'),
                            'exemptions': f"${tax.get('exemptions', 0):,}" if tax.get('exemptions') else 'N/A',
                            'taxable_value': f"${tax.get('taxablevalue', 0):,}" if tax.get('taxablevalue') else 'N/A',
                            'assessment_date': assessment.get('assessmentDate', 'N/A'),
                            'effective_date': assessment.get('effectiveDate', 'N/A')
                        }
                        
                        assessment_records.append(assessment_record)
            
            # Sort by year (most recent first)
            assessment_records.sort(key=lambda x: str(x['tax_year']), reverse=True)
            
            # Build final response
            cleaned_data = {
                'address': address,
                'total_assessments': len(assessment_records),
                'assessment_years': [record['tax_year'] for record in assessment_records],
                'assessments': assessment_records,
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return cleaned_data
            
        except Exception as e:
            return {
                'error': f'Could not process assessment history data: {str(e)}',
                'address': 'Unknown',
                'total_assessments': 0,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
    
    def get_assessment_history_report(self, address: str) -> Dict:
        """
        Complete workflow: Get assessment history and clean it for homeowners
        """
        print(f"🏛️ Getting assessment history report for: {address}")
        
        # Get assessment history data
        assessment_result = self.get_assessment_history(address)
        
        # Clean it for homeowners
        clean_data = self.clean_assessment_history_for_homeowners(assessment_result)
        
        return clean_data


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
        print("4. Complete report (both AVM and Basic Profile)")
        print("5. All events snapshot (comprehensive timeline)")
        print("6. Quit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice in ['6', 'quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if choice not in ['1', '2', '3', '4', '5']:
            print("Please select a valid option (1-6)")
            continue
            
        address = input("Enter property address: ").strip()
        if not address:
            print("Please enter a valid address")
            continue
        
        print(f"\n📊 Getting property report...")
        
        if choice == '1':
            report = service.get_combined_report(address)
        elif choice == '2':
            report = service.get_property_report(address)
        elif choice == '3':
            report = service.get_basic_profile_report(address)
        elif choice == '4':
            report = service.get_complete_report(address)
        elif choice == '5':
            report = service.get_all_events_report(address)
        
        print("\n" + "=" * 60)
        print("🏠 PROPERTY REPORT")
        print("=" * 60)
        
        if 'error' in report:
            print(f"❌ Error: {report['error']}")
        else:
            print(f"📍 Address: {report['address']}")
            
            # Handle all events report (choice 5)
            if choice == '5' and 'events' in report:
                print(f"🎯 Total Events: {report.get('total_events', 0)}")
                print(f"📊 Event Categories: {report.get('event_categories', 0)}")
                
                # Show events by category
                events = report.get('events', {})
                for category, event_list in events.items():
                    if event_list:
                        print(f"\n📋 {category.upper().replace('_', ' ')} ({len(event_list)} events):")
                        for i, event in enumerate(event_list[:5], 1):  # Show first 5
                            if category == 'sales':
                                print(f"   {i}. {event.get('date')}: {event.get('price')} ({event.get('transaction_type')})")
                            elif category == 'assessments':
                                print(f"   {i}. {event.get('year')}: {event.get('total_value')} (Tax: {event.get('tax_amount')})")
                                # Show raw assessment data
                                if i == 1:  # Show raw data for most recent assessment
                                    print(f"      📊 RAW ASSESSMENT DATA:")
                                    print(f"         Raw Assessed Value: ${event.get('raw_assessed_value', 0):,}")
                                    print(f"         Raw Land Value: ${event.get('raw_land_value', 0):,}")
                                    print(f"         Raw Improvement Value: ${event.get('raw_improvement_value', 0):,}")
                                    print(f"         Raw Tax Amount: ${event.get('raw_tax_amount', 0):,}")
                                    print(f"         Per Sq Ft: ${event.get('raw_per_sq_ft', 0):.2f}")
                        
                        if len(event_list) > 5:
                            print(f"   ... and {len(event_list) - 5} more events")
                
                # Show current snapshot
                if 'current_snapshot' in report:
                    snapshot = report['current_snapshot']
                    print(f"\n📸 CURRENT SNAPSHOT:")
                    print(f"   Property Type: {snapshot.get('property_type', 'N/A')}")
                    print(f"   Year Built: {snapshot.get('year_built', 'N/A')}")
                    print(f"   Size: {snapshot.get('size_sqft', 'N/A')} sq ft")
                    print(f"   Bedrooms: {snapshot.get('bedrooms', 'N/A')}")
                    print(f"   Bathrooms: {snapshot.get('bathrooms', 'N/A')}")
                    print(f"   Lot Size: {snapshot.get('lot_size_acres', 'N/A')} acres")
                    
                    if 'avm' in snapshot:
                        avm = snapshot['avm']
                        print(f"   AVM Value: {avm.get('estimated_value', 'N/A')}")
                        print(f"   Confidence: {avm.get('confidence_score', 'N/A')}")
            
            # Handle complete report (choice 4)
            elif choice == '4' and 'avm' in report:
                print(f"🔍 Data Availability:")
                print(f"   AVM Data: {'✅ Available' if report['avm']['available'] else '❌ Not Available'}")
                print(f"   Basic Profile: {'✅ Available' if report['basic_profile']['available'] else '❌ Not Available'}")
                
                if report['avm']['available'] and report['avm']['data']:
                    avm_data = report['avm']['data']
                    print(f"\n💰 AVM Data:")
                    print(f"   Current Value: {avm_data.get('current_estimated_value', 'N/A')}")
                    print(f"   Confidence: {avm_data.get('confidence_score', 'N/A')}")
                
                if report['basic_profile']['available'] and report['basic_profile']['data']:
                    profile_data = report['basic_profile']['data']
                    print(f"\n🏠 Property Data:")
                    print(f"   Size: {profile_data.get('property_size', 'N/A')}")
                    print(f"   Year Built: {profile_data.get('year_built', 'N/A')}")
            
            # Handle other report types (1, 2, 3)
            else:
                # Show valuation data if available (AVM report)
                if 'current_estimated_value' in report:
                    print(f"💰 Current Value: {report['current_estimated_value']}")
                    print(f"📈 Value Range: {report['value_range_low']} - {report['value_range_high']}")
                    print(f"🎯 Confidence: {report['confidence_score']}")
                    print(f"📅 Estimate Date: {report['estimate_date']}")
                
                # Show basic property data (available in most reports)
                if 'property_size' in report:
                    print(f"🏡 Size: {report['property_size']}")
                if 'year_built' in report:
                    print(f"🗓️ Built: {report['year_built']}")
                if 'bedrooms' in report:
                    print(f"🛏️ Bedrooms: {report['bedrooms']}")
                if 'bathrooms' in report:
                    print(f"🚿 Bathrooms: {report['bathrooms']}")
                if 'lot_size' in report:
                    print(f"📐 Lot Size: {report['lot_size']}")
                
                # Show additional basic profile data if available
                if 'property_type' in report:
                    print(f"🏠 Type: {report['property_type']}")
                if 'property_subtype' in report:
                    print(f"📝 Subtype: {report['property_subtype']}")
                
                if 'last_sale_price' in report:
                    print(f"💵 Last Sale: {report['last_sale_price']} ({report.get('last_sale_date', 'N/A')})")
                if 'current_assessment' in report:
                    print(f"🏛️ Assessment: {report['current_assessment']}")
                if 'owner' in report:
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
            if choice == '1':  # Combined report
                avm_result = service.get_avm_history(address)
                profile_result = service.get_basic_profile(address)
                print("AVM Data:")
                print(json.dumps(avm_result, indent=2))
                print("\nBasic Profile Data:")
                print(json.dumps(profile_result, indent=2))
            elif choice == '2':  # AVM data only
                avm_result = service.get_avm_history(address)
                print("AVM Data:")
                print(json.dumps(avm_result, indent=2))
            elif choice == '3':  # Basic profile data only
                profile_result = service.get_basic_profile(address)
                print("Basic Profile Data:")
                print(json.dumps(profile_result, indent=2))
            elif choice == '4':  # Complete report
                avm_result = service.get_avm_history(address)
                profile_result = service.get_basic_profile(address)
                print("AVM Data:")
                print(json.dumps(avm_result, indent=2))
                print("\nBasic Profile Data:")
                print(json.dumps(profile_result, indent=2))
            elif choice == '5':  # All events data
                events_result = service.get_all_events_snapshot(address)
                print("All Events Data:")
                print(json.dumps(events_result, indent=2))