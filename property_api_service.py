"""
Property API Service
Combines RentCast's property records/AVM data with RealtyAPI.io listing history
Provides a clean REST API interface for external consumers
"""

import requests
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List, Any
import json
from datetime import datetime
import re
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv(os.path.join(os.path.expanduser('~'), '.vendi-ave', '.env'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class PropertyAPIService:
    """
    Service that combines RentCast property/AVM data and RealtyAPI.io listing
    history into a unified REST API response format
    """

    def __init__(self):
        self.rentcast_api_key = os.environ.get('RENTCAST_API_KEY')
        self.rentcast_base_url = "https://api.rentcast.io/v1"

        self.realtyapi_key = os.environ.get('REALTYAPI_KEY')
        self.realtyapi_base_url = "https://realtor.realtyapi.io"

        if not self.rentcast_api_key:
            raise ValueError("RENTCAST_API_KEY not found in environment variables")
        if not self.realtyapi_key:
            raise ValueError("REALTYAPI_KEY not found in environment variables")

        if len(self.rentcast_api_key) < 10 or len(self.realtyapi_key) < 10:
            raise ValueError("Invalid API key format")

        self.rentcast_headers = {
            "accept": "application/json",
            "X-Api-Key": self.rentcast_api_key
        }
        self.realtyapi_headers = {
            "accept": "application/json",
            "x-realtyapi-key": self.realtyapi_key
        }

        # Setup session with connection pooling and timeouts
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default timeout
        self.timeout = 10

    def _rentcast_get(self, path: str, params: Dict) -> requests.Response:
        """GET request against the RentCast API"""
        url = f"{self.rentcast_base_url}{path}"
        return self.session.get(url, headers=self.rentcast_headers, params=params, timeout=self.timeout)

    def _realtyapi_get(self, path: str, params: Dict) -> requests.Response:
        """GET request against the RealtyAPI.io API"""
        url = f"{self.realtyapi_base_url}{path}"
        return self.session.get(url, headers=self.realtyapi_headers, params=params, timeout=self.timeout)
    
    def validate_and_sanitize_address(self, address: str) -> str:
        """Validate and sanitize address input"""
        if not address:
            raise ValueError("Address cannot be empty")
        
        # Remove leading/trailing whitespace
        address = address.strip()
        
        if not address:
            raise ValueError("Address cannot be empty")
        
        # Check length limits
        if len(address) > 200:
            raise ValueError("Address too long (max 200 characters)")
        
        if len(address) < 5:
            raise ValueError("Address too short (min 5 characters)")
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", ';', '&', '|', '$', '`']
        for char in dangerous_chars:
            if char in address:
                address = address.replace(char, '')
        
        # Check for script injection attempts
        script_patterns = [
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'eval\(',
            r'alert\(',
        ]
        
        for pattern in script_patterns:
            if re.search(pattern, address.lower()):
                raise ValueError("Address contains invalid characters")
        
        # Basic US address format validation
        # Should have at least: street, city, state (optional zip)
        if not re.match(r'.+,.+', address):
            raise ValueError("Please use format: Street, City, State [Zip]")
        
        return address
    
    def parse_address(self, address: str) -> Dict[str, str]:
        """Parse and validate address string into components for API calls"""
        # First validate and sanitize
        clean_address = self.validate_and_sanitize_address(address)
        
        parts = [part.strip() for part in clean_address.split(',')]
        
        if len(parts) >= 3:
            street = parts[0]
            city = parts[1]
            state_zip = parts[2].split()
            state = state_zip[0] if state_zip else ""
            zip_code = state_zip[1] if len(state_zip) > 1 else ""
            
            # Validate components
            if not street or len(street) < 2:
                raise ValueError("Invalid street address")
            if not city or len(city) < 2:
                raise ValueError("Invalid city name")
            if state and len(state) != 2:
                logger.warning(f"State '{state}' may not be in standard format")
            
            return {
                'street': street,
                'city': city,
                'state': state,
                'zip': zip_code,
                'address1': street,
                'address2': f"{city}, {state} {zip_code}".strip()
            }
        elif len(parts) == 2:
            # Handle "Street, City State" format
            street = parts[0]
            city_state = parts[1].strip()
            
            # Try to split city and state
            city_state_parts = city_state.rsplit(' ', 1)
            if len(city_state_parts) == 2:
                city = city_state_parts[0]
                state = city_state_parts[1]
            else:
                city = city_state
                state = ""
            
            return {
                'street': street,
                'city': city,
                'state': state,
                'zip': '',
                'address1': street,
                'address2': f"{city}, {state}".strip()
            }
        else:
            # Fallback for single part address
            return {
                'street': clean_address,
                'city': '',
                'state': '',
                'zip': '',
                'address1': clean_address,
                'address2': ''
            }
    
    def get_basic_profile(self, address: str) -> Optional[Dict]:
        """
        Get basic property profile from RentCast
        Uses the /properties endpoint
        """
        logger.info(f"Fetching basic profile for address")

        clean_address = self.validate_and_sanitize_address(address)

        try:
            params = {'address': clean_address}

            logger.debug("Basic Profile API request to RentCast /properties")
            response = self._rentcast_get('/properties', params)

            if response.status_code == 200:
                records = response.json()
                logger.debug("Basic Profile response received")

                if records and isinstance(records, list) and len(records) > 0:
                    logger.info("Basic profile retrieved successfully")
                    return {
                        'success': True,
                        'data': {'property': records},
                        'property': records
                    }
                else:
                    logger.warning("No basic profile found")
                    return {
                        'success': False,
                        'error': 'No basic profile found',
                        'message': 'No data available'
                    }
            else:
                logger.error(f"Basic Profile API Error {response.status_code}")
                return {
                    'success': False,
                    'error': f"Basic Profile API Error {response.status_code}",
                    'message': 'Unable to retrieve property profile'
                }

        except Exception as e:
            logger.error(f"Basic profile request failed: {str(e)[:100]}")
            return {
                'success': False,
                'error': 'Basic profile request failed',
                'message': 'Unable to process request'
            }

    def get_avm_history(self, address: str) -> Optional[Dict]:
        """
        Get valuation estimate(s) + listing details from RealtyAPI.io
        Uses the /details/byaddress endpoint, which surfaces AVM estimates
        RealtyAPI.io picks up from the underlying listing platforms
        (Quantarium, Collateral Analytics, etc.) it aggregates.
        """
        logger.info(f"Fetching valuation details for address")

        clean_address = self.validate_and_sanitize_address(address)

        try:
            params = {'address': clean_address}

            logger.debug("Valuation API request to RealtyAPI.io /details/byaddress")
            response = self._realtyapi_get('/details/byaddress', params)

            if response.status_code == 200:
                data = response.json()
                detail = data.get('detail', {})
                current_values = (detail.get('estimates', {}) or {}).get('current_values', []) or []
                logger.debug("Valuation response received")

                if detail and current_values:
                    logger.info("Valuation estimate retrieved successfully")
                    return {
                        'success': True,
                        'data': detail,
                        'estimates': current_values
                    }
                elif detail:
                    logger.warning("Listing found but no valuation estimate available")
                    return {
                        'success': False,
                        'error': 'No valuation estimate found',
                        'message': 'Listing details available but no AVM estimate'
                    }
                else:
                    logger.warning("No listing details found")
                    return {
                        'success': False,
                        'error': 'No listing details found',
                        'message': 'No data available'
                    }
            else:
                logger.error(f"RealtyAPI Details Error {response.status_code}")
                return {
                    'success': False,
                    'error': f"RealtyAPI Details Error {response.status_code}",
                    'message': 'Unable to retrieve valuation data'
                }

        except Exception as e:
            logger.error(f"Valuation request failed: {str(e)[:100]}")
            return {
                'success': False,
                'error': 'Valuation request failed',
                'message': 'Unable to process valuation request'
            }
    
    def clean_basic_profile_for_homeowners(self, profile_data: Dict) -> Dict:
        """
        Clean basic profile data (RentCast /properties record) into simple,
        homeowner-friendly format
        """
        try:
            if not profile_data.get('success'):
                return {
                    'error': profile_data.get('error', 'No basic profile data available'),
                    'address': 'Unknown',
                    'date': datetime.now().strftime('%Y-%m-%d')
                }

            record = profile_data['property'][0]

            tax_assessments = record.get('taxAssessments', {}) or {}
            latest_year = max(tax_assessments.keys(), key=lambda y: int(y)) if tax_assessments else None
            latest_assessment = tax_assessments.get(latest_year, {}) if latest_year else {}

            owner_names = (record.get('owner') or {}).get('names') or []

            cleaned_data = {
                'address': record.get('formattedAddress', 'N/A'),
                'property_size': f"{record.get('squareFootage'):,} sqft" if record.get('squareFootage') else 'N/A',
                'year_built': record.get('yearBuilt', 'N/A'),
                'bedrooms': record.get('bedrooms', 'N/A'),
                'bathrooms': record.get('bathrooms', 'N/A'),
                'lot_size': f"{record.get('lotSize', 0) / 43560:.2f} acres" if record.get('lotSize') else 'N/A',
                'property_type': record.get('propertyType', 'N/A'),
                'current_assessment': f"${latest_assessment.get('value'):,}" if latest_assessment.get('value') else 'N/A',
                'last_sale_price': f"${record.get('lastSalePrice'):,}" if record.get('lastSalePrice') else 'N/A',
                'last_sale_date': record.get('lastSaleDate', 'N/A'),
                'owner': owner_names[0] if owner_names else 'N/A',
                'latitude': record.get('latitude'),
                'longitude': record.get('longitude'),
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Validate and sanitize financial data
            return self._sanitize_financial_data(cleaned_data)

        except Exception as e:
            return {
                'error': f'Could not process basic profile data: {str(e)}',
                'address': 'Unknown',
                'date': datetime.now().strftime('%Y-%m-%d')
            }

    def clean_data_for_homeowners(self, avm_data: Dict) -> Dict:
        """
        Clean valuation data (RealtyAPI.io /details/byaddress) into simple,
        homeowner-friendly format. Perfect for CSV export or easy reading.
        """
        try:
            if not avm_data.get('success'):
                return {
                    'error': avm_data.get('error', 'No data available'),
                    'address': 'Unknown',
                    'current_value': 'N/A',
                    'date': datetime.now().strftime('%Y-%m-%d')
                }

            detail = avm_data['data']
            address_info = detail.get('address', {}) or {}
            details = detail.get('details', {}) or {}
            estimates = avm_data.get('estimates', [])

            best_estimate = next((e for e in estimates if e.get('isbest_homevalue')), estimates[0] if estimates else {})
            current_value = best_estimate.get('estimate')
            all_values = [e.get('estimate') for e in estimates if e.get('estimate')]

            tax_history = detail.get('tax_history', []) or []
            latest_tax = max(tax_history, key=lambda t: t.get('year', 0)) if tax_history else None

            cleaned_data = {
                'address': f"{address_info.get('line', '')}, {address_info.get('city', '')}, {address_info.get('state_code', '')} {address_info.get('postal_code', '')}".strip(),
                'current_estimated_value': f"${current_value:,}" if current_value else 'N/A',
                'value_range_low': f"${min(all_values):,}" if all_values else 'N/A',
                'value_range_high': f"${max(all_values):,}" if all_values else 'N/A',
                'confidence_score': f"{len(estimates)} valuation source(s)" if estimates else 'N/A',
                'value_source': (best_estimate.get('source') or {}).get('name', 'N/A'),
                'property_size': f"{details.get('sqft'):,} sqft" if details.get('sqft') else 'N/A',
                'year_built': details.get('year_built', 'N/A'),
                'bedrooms': details.get('beds', 'N/A'),
                'bathrooms': details.get('baths', 'N/A'),
                'lot_size': f"{details.get('lot_sqft', 0) / 43560:.2f} acres" if details.get('lot_sqft') else 'N/A',
                'last_sale_price': f"${detail.get('last_sold_price'):,}" if detail.get('last_sold_price') else 'N/A',
                'last_sale_date': detail.get('last_sold_date', 'N/A'),
                'current_assessment': f"${latest_tax['assessment']['total']:,}" if latest_tax and (latest_tax.get('assessment') or {}).get('total') else 'N/A',
                'list_price': f"${detail.get('list_price'):,}" if detail.get('list_price') else 'N/A',
                'listing_status': detail.get('status', 'N/A'),
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Validate and sanitize financial data
            return self._sanitize_financial_data(cleaned_data)

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
        logger.info("Getting basic profile report")
        
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
    
    def _validate_financial_value(self, value: Any, field_name: str) -> bool:
        """Validate financial values for reasonableness"""
        if not value or value == 'N/A' or value == '':
            return True
        
        try:
            # Convert string values to numeric
            if isinstance(value, str):
                numeric_value = float(value.replace('$', '').replace(',', ''))
            else:
                numeric_value = float(value)
            
            # Define reasonable ranges for different value types
            ranges = {
                'property_value': (1000, 100000000),      # $1K to $100M
                'assessment_value': (500, 50000000),      # $500 to $50M
                'tax_amount': (10, 1000000),              # $10 to $1M
                'sale_price': (1000, 100000000),          # $1K to $100M
                'per_sqft': (10, 10000),                  # $10 to $10K per sq ft
            }
            
            # Determine which range to use
            range_key = 'property_value'  # default
            if 'tax' in field_name.lower():
                range_key = 'tax_amount'
            elif 'assessment' in field_name.lower() or 'assessed' in field_name.lower():
                range_key = 'assessment_value'
            elif 'sale' in field_name.lower():
                range_key = 'sale_price'
            elif 'sqft' in field_name.lower() or 'per_sq_ft' in field_name.lower():
                range_key = 'per_sqft'
            
            if range_key in ranges:
                min_val, max_val = ranges[range_key]
                is_valid = min_val <= numeric_value <= max_val
                
                if not is_valid:
                    logger.warning(f"Suspicious {field_name} value: ${numeric_value:,} (range: ${min_val:,}-${max_val:,})")
                
                return is_valid
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid {field_name} value: {value} - {e}")
            return False
    
    def _sanitize_financial_data(self, data: Dict, property_type: str = '') -> Dict:
        """Sanitize and validate financial data in property responses"""
        if not isinstance(data, dict):
            return data
        
        sanitized_data = {}
        
        for key, value in data.items():
            # Skip non-financial fields (dates/sources/status share substrings like
            # "sale" and "value" with financial fields but aren't numeric amounts)
            if key in ['address', 'owner', 'property_type', 'year_built', 'bedrooms', 'bathrooms'] or \
               key.endswith(('_date', '_source', '_status')):
                sanitized_data[key] = value
                continue

            # Validate financial fields
            if any(financial_term in key.lower() for financial_term in
                   ['value', 'price', 'amount', 'tax', 'assessment', 'sale']):
                
                if self._validate_financial_value(value, key):
                    sanitized_data[key] = value
                else:
                    logger.warning(f"Removing invalid financial data for {key}: {value}")
                    sanitized_data[key] = 'N/A'
            else:
                sanitized_data[key] = value
        
        return sanitized_data

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
        Get comprehensive property event snapshot from RealtyAPI.io
        Uses the /details/byaddress endpoint (listing history, sale history, tax history)
        """
        logger.info(f"Fetching all events snapshot for address")

        clean_address = self.validate_and_sanitize_address(address)

        try:
            params = {'address': clean_address}

            response = self._realtyapi_get('/details/byaddress', params)

            if response.status_code == 200:
                data = response.json()
                detail = data.get('detail', {})

                if detail:
                    logger.info("All events snapshot retrieved")
                    return {
                        'success': True,
                        'data': detail
                    }
                else:
                    logger.warning("No events found")
                    return {
                        'success': False,
                        'error': 'No events found',
                        'message': 'No event data available'
                    }
            else:
                logger.error(f"RealtyAPI Details Error {response.status_code}")
                return {
                    'success': False,
                    'error': f"RealtyAPI Details Error {response.status_code}",
                    'details': response.text[:200]
                }

        except Exception as e:
            logger.error(f"All events request failed: {str(e)[:100]}")
            return {
                'success': False,
                'error': 'All events request failed',
                'details': str(e)
            }

    def clean_all_events_for_homeowners(self, events_data: Dict) -> Dict:
        """
        Clean all events data (RealtyAPI.io /details/byaddress) into homeowner-friendly
        format with raw values preserved for analysis
        """
        try:
            if not events_data.get('success'):
                return {
                    'error': events_data.get('error', 'No events data available'),
                    'address': 'Unknown',
                    'total_events': 0,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }

            detail = events_data['data']
            address_info = detail.get('address', {}) or {}
            address = f"{address_info.get('line', '')}, {address_info.get('city', '')}, {address_info.get('state_code', '')} {address_info.get('postal_code', '')}".strip()

            cleaned_events = {}
            total_events = 0

            # Listing history events (price changes, status changes, etc.)
            property_history = detail.get('property_history', []) or []
            if property_history:
                history_events = []
                for h in property_history:
                    history_events.append({
                        'date': h.get('date', 'N/A'),
                        'event': h.get('event', 'N/A'),
                        'price': f"${h.get('price'):,}" if h.get('price') else 'N/A',
                        'raw_price': h.get('price', 0)
                    })
                cleaned_events['listing_history'] = history_events
                total_events += len(history_events)

            # Last known sale
            if detail.get('last_sold_price'):
                cleaned_events['sales'] = [{
                    'date': detail.get('last_sold_date', 'N/A'),
                    'price': f"${detail.get('last_sold_price'):,}",
                    'raw_sale_amount': detail.get('last_sold_price')
                }]
                total_events += 1

            # Assessment/tax events
            tax_history = detail.get('tax_history', []) or []
            if tax_history:
                assessment_events = []
                for record in tax_history:
                    assessment = record.get('assessment', {}) or {}
                    assessment_events.append({
                        'year': str(record.get('year', 'N/A')),
                        'total_value': f"${assessment.get('total'):,}" if assessment.get('total') else 'N/A',
                        'tax_amount': f"${record.get('tax'):,}" if record.get('tax') else 'N/A',
                        'raw_assessed_value': assessment.get('total', 0),
                        'raw_tax_amount': record.get('tax', 0)
                    })
                cleaned_events['assessments'] = assessment_events
                total_events += len(assessment_events)

            # Current snapshot from listing details
            details = detail.get('details', {}) or {}
            current_snapshot = {
                'property_type': details.get('type', 'N/A'),
                'year_built': details.get('year_built', 'N/A'),
                'size_sqft': details.get('sqft', 'N/A'),
                'bedrooms': details.get('beds', 'N/A'),
                'bathrooms': details.get('baths', 'N/A'),
                'lot_size_sqft': details.get('lot_sqft', 'N/A'),
                'listing_status': detail.get('status', 'N/A')
            }

            current_values = (detail.get('estimates', {}) or {}).get('current_values', []) or []
            if current_values:
                best = next((e for e in current_values if e.get('isbest_homevalue')), current_values[0])
                current_snapshot['avm'] = {
                    'estimated_value': f"${best.get('estimate'):,}" if best.get('estimate') else 'N/A',
                    'source': (best.get('source') or {}).get('name', 'N/A'),
                    'raw_estimated_value': best.get('estimate', 0)
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
        Get historical tax assessment data from RealtyAPI.io
        Uses the /details/byaddress endpoint's tax_history field, which
        goes back much further than RentCast's basic property record.
        """
        logger.info(f"Fetching assessment history for address")

        clean_address = self.validate_and_sanitize_address(address)

        try:
            params = {'address': clean_address}

            response = self._realtyapi_get('/details/byaddress', params)

            if response.status_code == 200:
                data = response.json()
                detail = data.get('detail', {})
                tax_history = detail.get('tax_history', []) or []

                if detail and tax_history:
                    logger.info("Assessment history retrieved")
                    return {
                        'success': True,
                        'data': detail,
                        'tax_history': tax_history
                    }
                else:
                    logger.warning("No assessment history found")
                    return {
                        'success': False,
                        'error': 'No assessment history found',
                        'message': 'No assessment data available'
                    }
            else:
                logger.error(f"RealtyAPI Details Error {response.status_code}")
                return {
                    'success': False,
                    'error': f"RealtyAPI Details Error {response.status_code}",
                    'details': response.text[:200]
                }

        except Exception as e:
            logger.error(f"Assessment history request failed: {str(e)[:100]}")
            return {
                'success': False,
                'error': 'Assessment history request failed',
                'details': str(e)
            }

    def clean_assessment_history_for_homeowners(self, assessment_data: Dict) -> Dict:
        """
        Clean assessment history data (RealtyAPI.io tax_history) into
        homeowner-friendly format with raw values preserved for analysis
        """
        try:
            if not assessment_data.get('success'):
                return {
                    'error': assessment_data.get('error', 'No assessment data available'),
                    'address': 'Unknown',
                    'total_assessments': 0,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }

            detail = assessment_data['data']
            address_info = detail.get('address', {}) or {}
            address = f"{address_info.get('line', '')}, {address_info.get('city', '')}, {address_info.get('state_code', '')} {address_info.get('postal_code', '')}".strip()

            building_size = (detail.get('details', {}) or {}).get('sqft', 0) or 0
            tax_history = assessment_data.get('tax_history', [])

            assessment_records = []
            for record in tax_history:
                year = record.get('year', 'N/A')
                assessment = record.get('assessment', {}) or {}
                total_value = assessment.get('total', 0)
                land_value = assessment.get('land', 0)
                improvement_value = assessment.get('building', 0)
                tax_amount = record.get('tax', 0)

                assessment_records.append({
                    'tax_year': str(year),
                    'assessment_year': str(year),

                    'total_assessed_value': f"${total_value:,}" if total_value else 'N/A',
                    'land_value': f"${land_value:,}" if land_value else 'N/A',
                    'improvement_value': f"${improvement_value:,}" if improvement_value else 'N/A',
                    'tax_amount': f"${tax_amount:,}" if tax_amount else 'N/A',
                    'assessed_per_sqft': f"${total_value / building_size:.2f}" if building_size > 0 and total_value else 'N/A',

                    'raw_total_assessed': total_value,
                    'raw_land_value': land_value,
                    'raw_improvement_value': improvement_value,
                    'raw_tax_amount': tax_amount,
                    'raw_assessed_per_sqft': total_value / building_size if building_size > 0 and total_value else 0
                })

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
    
    def get_sales_comparables(self, street: str, city: str, county: str, state: str, zip_code: str,
                               sqft_tolerance: float = 20.0, bed_bath_tolerance: float = 1.0,
                               value_tolerance: float = 20.0) -> Dict:
        """
        Get comparable properties centered on subject property location

        Subject property (beds/baths/sqft/coordinates) comes from RentCast's
        single /properties call. The subject's own valuation estimate comes
        from RealtyAPI.io (same AVM source used by get_avm_history). Comparable
        search is done via RealtyAPI.io's /search/bycoordinates.

        Filters (all approximate, not exact match):
        - Square footage within ±sqft_tolerance% of subject
        - Bedrooms within ±bed_bath_tolerance of subject
        - Bathrooms within ±bed_bath_tolerance of subject (if subject has bathroom data)
        - Estimated value within ±value_tolerance% of subject's own estimated value
          (skipped if either subject or comp has no value estimate available)
        - Expanding radius: 0.5-5.5 miles until 10+ properties found

        Args:
            street: Street address (e.g., "123 Main St")
            city: City name (e.g., "Boston")
            county: County name (optional)
            state: State abbreviation (e.g., "MA")
            zip_code: ZIP code (e.g., "02101")
            sqft_tolerance: Percentage tolerance for square footage (default 20.0 = ±20%)
            bed_bath_tolerance: Allowed +/- difference in bedroom/bathroom count (default 1.0)
            value_tolerance: Percentage tolerance for estimated value (default 20.0 = ±20%)

        Returns:
            Dict: Comparable properties data or error message
        """
        try:
            # Validate inputs - county is optional
            if not all([street, city, state, zip_code]):
                raise ValueError("Street, city, state, and ZIP code are required")

            # Basic sanitization
            street = street.strip()
            city = city.strip()
            county = county.strip() if county else ''
            state = state.strip()
            zip_code = zip_code.strip()

            full_address = f"{street}, {city}, {state} {zip_code}"
            logger.info(f"Fetching sales comparables for {full_address}")

            # Step 1: Get subject property details (lat/long, beds, baths, sqft) from RentCast
            subject_property = self.get_basic_profile(full_address)

            if not subject_property or not subject_property.get('success'):
                return {
                    'error': 'Could not retrieve subject property details',
                    'address': full_address,
                    'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

            property_list = subject_property.get('property', [])
            if not property_list:
                return {
                    'error': 'No property data found',
                    'address': full_address,
                    'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

            prop = property_list[0]
            subject_beds = prop.get('bedrooms')
            subject_baths = prop.get('bathrooms')
            subject_sqft = prop.get('squareFootage')
            subject_lat = prop.get('latitude')
            subject_lon = prop.get('longitude')

            if not all([subject_beds, subject_lat, subject_lon]):
                logger.warning(f"Missing critical data - Beds: {subject_beds}, Lat: {subject_lat}, Lon: {subject_lon}")
                return {
                    'error': 'Incomplete subject property data (missing beds or coordinates)',
                    'address': full_address,
                    'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

            if not subject_baths:
                logger.warning("Missing optional bathroom data - will search without bathroom filter")

            # Step 1b: Get the subject's own valuation estimate (average across sources)
            subject_value = None
            avm_result = self.get_avm_history(full_address)
            if avm_result.get('success'):
                subject_values = [e.get('estimate') for e in avm_result.get('estimates', []) if e.get('estimate')]
                if subject_values:
                    subject_value = sum(subject_values) / len(subject_values)

            logger.info(f"Subject: {subject_beds} beds, {subject_baths} baths, {subject_sqft} sqft, "
                        f"~${subject_value:,.0f} est. value @ ({subject_lat}, {subject_lon})" if subject_value
                        else f"Subject: {subject_beds} beds, {subject_baths} baths, {subject_sqft} sqft @ ({subject_lat}, {subject_lon})")

            sqft_min = subject_sqft * (1 - sqft_tolerance / 100) if subject_sqft else None
            sqft_max = subject_sqft * (1 + sqft_tolerance / 100) if subject_sqft else None
            value_min = subject_value * (1 - value_tolerance / 100) if subject_value else None
            value_max = subject_value * (1 + value_tolerance / 100) if subject_value else None

            # Step 2: Search RealtyAPI.io with expanding radius centered on subject property
            min_properties = 10
            radius_miles = 0.5
            max_radius = 5.5
            all_filtered_comps = []

            while radius_miles <= max_radius:
                logger.info(f"Searching {radius_miles} mile radius from subject property...")

                params = {
                    'latitude': subject_lat,
                    'longitude': subject_lon,
                    'radius': radius_miles
                }

                response = self._realtyapi_get('/search/bycoordinates', params)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get('searchResults', [])
                    logger.info(f"Received {len(results)} properties from API")

                    filtered = []
                    for p in results:
                        try:
                            beds = p.get('beds')
                            baths = p.get('baths')
                            sqft = p.get('sqft') or 0
                            estimate = p.get('estimate')

                            if beds is None or abs(beds - subject_beds) > bed_bath_tolerance:
                                continue

                            if subject_baths and baths:
                                try:
                                    if abs(float(baths) - float(subject_baths)) > bed_bath_tolerance:
                                        continue
                                except (TypeError, ValueError):
                                    pass

                            if sqft_min is not None and sqft:
                                if not (sqft_min <= sqft <= sqft_max):
                                    continue

                            if value_min is not None and estimate:
                                if not (value_min <= estimate <= value_max):
                                    continue

                            addr = p.get('address', {}) or {}
                            p_lat, p_lon = addr.get('latitude'), addr.get('longitude')
                            p['_distance_miles'] = (
                                self._haversine_miles(subject_lat, subject_lon, p_lat, p_lon)
                                if p_lat and p_lon else 999
                            )

                            filtered.append(p)
                        except Exception as e:
                            logger.debug(f"Error filtering property: {str(e)}")
                            continue

                    all_filtered_comps = filtered
                    logger.info(f"After filtering: {len(all_filtered_comps)} matching comparables")

                    if len(all_filtered_comps) >= min_properties:
                        logger.info(f"Found {len(all_filtered_comps)} comparables (>= {min_properties} required)")
                        break
                    else:
                        radius_miles += 0.25 if radius_miles < 1.0 else 0.5
                else:
                    logger.error(f"API error {response.status_code}, expanding radius...")
                    radius_miles += 0.5

            # Prepare results
            if len(all_filtered_comps) > 0:
                result_data = {
                    'searchResults': all_filtered_comps,
                    'search_radius': radius_miles,
                    'subject_property': {
                        'address': full_address,
                        'bedrooms': subject_beds,
                        'bathrooms': subject_baths,
                        'sqft': subject_sqft,
                        'estimated_value': f"${subject_value:,.0f}" if subject_value else 'N/A'
                    },
                    'filters_applied': {
                        'bedrooms': f"{subject_beds} ±{bed_bath_tolerance}",
                        'bathrooms': f"{subject_baths} ±{bed_bath_tolerance}" if subject_baths else 'Not filtered',
                        'sqft_range': f'{int(sqft_min):,} - {int(sqft_max):,}' if sqft_min else 'Not filtered',
                        'value_range': f'${int(value_min):,} - ${int(value_max):,}' if value_min else 'Not filtered (no subject valuation available)'
                    }
                }
                return self.clean_sales_comparables_for_homeowners(result_data)
            else:
                return {
                    'error': f'No comparable properties found matching criteria (searched up to {radius_miles} miles)',
                    'address': full_address,
                    'filters_applied': {
                        'bedrooms': f"{subject_beds} ±{bed_bath_tolerance}",
                        'bathrooms': f"{subject_baths} ±{bed_bath_tolerance}" if subject_baths else 'Not filtered',
                        'sqft_range': f'{int(sqft_min):,} - {int(sqft_max):,}' if sqft_min else 'Not filtered',
                        'value_range': f'${int(value_min):,} - ${int(value_max):,}' if value_min else 'Not filtered'
                    },
                    'search_radius_miles': radius_miles,
                    'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

        except Exception as e:
            error_msg = f"Failed to get sales comparables: {str(e)[:100]}"
            logger.error(error_msg)
            return {
                'error': error_msg,
                'address': f"{street}, {city}, {county}, {state} {zip_code}",
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    def clean_sales_comparables_for_homeowners(self, raw_data: Dict) -> Dict:
        """
        Clean sales comparables data (RealtyAPI.io /search/bycoordinates results)
        for homeowner-friendly display

        Args:
            raw_data: Pre-filtered search results plus search metadata

        Returns:
            Dict: Cleaned and formatted sales comparables data
        """
        try:
            results = raw_data.get('searchResults', [])

            if not results:
                return {
                    'error': 'No comparable sales found',
                    'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

            cleaned_comparables = []

            for prop in results:
                try:
                    address_data = prop.get('address', {}) or {}
                    formatted_address = f"{address_data.get('line', '')}, {address_data.get('city', '')}, {address_data.get('state_code', '')} {address_data.get('postal_code', '')}".strip()

                    sale_amount = prop.get('last_sold_price') or 0
                    sale_date = prop.get('last_sold_date') or ''
                    building_size = prop.get('sqft') or 0
                    estimate = prop.get('estimate') or 0

                    formatted_sale_amount = f"${sale_amount:,}" if sale_amount else "Not disclosed"

                    comparable = {
                        'address': formatted_address or 'Address unavailable',
                        'distance_miles': round(prop['_distance_miles'], 2) if '_distance_miles' in prop else None,
                        'listing_status': prop.get('status', 'N/A'),
                        'estimated_value': f"${estimate:,}" if estimate else "N/A",
                        'raw_estimated_value': estimate,
                        'sale_price': formatted_sale_amount,
                        'raw_sale_price': sale_amount,
                        'sale_date': sale_date,
                        'building_size_sqft': building_size,
                        'lot_size_sqft': prop.get('lot_sqft', 0),
                        'bedrooms': prop.get('beds', 'N/A'),
                        'bathrooms': prop.get('baths', 'N/A'),
                        'price_per_sqft': f"${sale_amount / building_size:.2f}" if building_size and sale_amount else "N/A",
                        'estimated_value_per_sqft': f"${estimate / building_size:.2f}" if building_size and estimate else "N/A"
                    }

                    cleaned_comparables.append(comparable)

                except Exception as e:
                    logger.warning(f"Error processing comparable property: {str(e)}")
                    continue

            # Sort by distance (closest first)
            cleaned_comparables.sort(key=lambda x: x.get('distance_miles') if x.get('distance_miles') is not None else 999)

            # Build response with search metadata
            response = {
                'total_comparables': len(cleaned_comparables),
                'comparables': cleaned_comparables,
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            if 'search_radius' in raw_data:
                response['search_radius_miles'] = raw_data['search_radius']

            if 'subject_property' in raw_data:
                response['subject_property'] = raw_data['subject_property']

            if 'filters_applied' in raw_data:
                response['filters_applied'] = raw_data['filters_applied']

            return response

        except Exception as e:
            logger.error(f"Error cleaning sales comparables data: {str(e)}")
            return {
                'error': f'Error processing sales comparables data: {str(e)[:100]}',
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    def _haversine_miles(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance between two lat/long points, in miles"""
        import math
        radius_earth_miles = 3958.8
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)
        a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        return radius_earth_miles * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def get_similar_properties_with_sales(self, street: str, city: str, county: str, state: str, zip_code: str, sqft_tolerance: float = 10.0, radius_miles: float = 5.0) -> Dict:
        """
        Get up to 15 closest properties with similar characteristics and their valuation

        Process:
        1. Get subject property details (beds, baths, sqft, lat/long) from RentCast
        2. Search RealtyAPI.io /search/bycoordinates for similar properties
           (same beds/baths, ±sqft_tolerance) - estimate/list price come back
           in the same call, no per-property follow-up requests needed
        3. Sort by distance, take 15 closest

        Args:
            street: Street address
            city: City name
            county: County name (optional)
            state: State abbreviation
            zip_code: ZIP code
            sqft_tolerance: Percentage tolerance for square footage (default 10.0 = ±10%)
            radius_miles: Maximum search radius in miles (default 5.0)

        Returns:
            Dict: 15 closest similar properties with property details and valuation
        """
        try:
            # Step 1: Get subject property details from RentCast
            full_address = f"{street}, {city}, {state} {zip_code}"
            logger.info(f"Finding similar properties for {full_address}")

            subject_property = self.get_basic_profile(full_address)

            if not subject_property or not subject_property.get('success'):
                return {
                    'error': 'Could not retrieve subject property details',
                    'address': full_address,
                    'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

            property_list = subject_property.get('property', [])
            if not property_list:
                return {
                    'error': 'No property data found',
                    'address': full_address,
                    'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

            prop = property_list[0]
            subject_beds = prop.get('bedrooms')
            subject_baths = prop.get('bathrooms')
            subject_sqft = prop.get('squareFootage')
            subject_lat = prop.get('latitude')
            subject_lon = prop.get('longitude')

            if not all([subject_beds, subject_lat, subject_lon, subject_sqft]):
                logger.warning(f"Missing data - Beds: {subject_beds}, Lat: {subject_lat}, Lon: {subject_lon}, Sqft: {subject_sqft}")
                return {
                    'error': 'Incomplete subject property data',
                    'address': full_address,
                    'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

            # Calculate sqft range
            sqft_min = int(subject_sqft * (1 - sqft_tolerance / 100))
            sqft_max = int(subject_sqft * (1 + sqft_tolerance / 100))

            logger.info(f"Subject: {subject_beds} beds, {subject_baths} baths, {subject_sqft} sqft @ ({subject_lat}, {subject_lon})")
            logger.info(f"Sqft range: {sqft_min:,} - {sqft_max:,} (±{sqft_tolerance}%)")

            # Step 2: Search RealtyAPI.io for similar properties near the subject,
            # expanding the radius until we have candidates or hit the cap
            min_properties = 5
            max_radius = 15.0
            search_radius = radius_miles
            filtered = []

            while search_radius <= max_radius:
                params = {
                    'latitude': subject_lat,
                    'longitude': subject_lon,
                    'radius': search_radius
                }

                response = self._realtyapi_get('/search/bycoordinates', params)

                if response.status_code != 200:
                    logger.error(f"API error {response.status_code}, expanding radius...")
                    search_radius += 5.0
                    continue

                data = response.json()
                results = data.get('searchResults', [])
                logger.info(f"Found {len(results)} nearby properties within {search_radius} miles")

                # Client-side filtering: exact beds, ±sqft tolerance, baths if available
                filtered = []
                for p in results:
                    beds = p.get('beds')
                    sqft = p.get('sqft') or 0
                    baths = p.get('baths')

                    if beds != subject_beds:
                        continue
                    if not (sqft_min <= sqft <= sqft_max):
                        continue
                    if subject_baths and baths and str(baths) != str(subject_baths):
                        continue

                    filtered.append(p)

                if len(filtered) >= min_properties:
                    radius_miles = search_radius
                    break

                search_radius += 5.0
            else:
                radius_miles = min(search_radius, max_radius)

            if not filtered:
                return {
                    'error': 'No similar properties found',
                    'address': full_address,
                    'filters_applied': {
                        'bedrooms': subject_beds,
                        'bathrooms': subject_baths,
                        'sqft_range': f'{sqft_min:,} - {sqft_max:,}'
                    },
                    'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

            # Step 3: Sort by distance and take 15 closest
            for p in filtered:
                addr = p.get('address', {}) or {}
                p_lat = addr.get('latitude')
                p_lon = addr.get('longitude')
                p['_distance_miles'] = (
                    self._haversine_miles(subject_lat, subject_lon, p_lat, p_lon)
                    if p_lat and p_lon else 999
                )

            filtered_sorted = sorted(filtered, key=lambda p: p['_distance_miles'])
            closest_15 = filtered_sorted[:15]

            logger.info(f"Selected {len(closest_15)} closest properties")

            # Step 4: Format the response
            formatted_comparables = []

            for p in closest_15:
                addr = p.get('address', {}) or {}
                address = f"{addr.get('line', '')}, {addr.get('city', '')}, {addr.get('state_code', '')} {addr.get('postal_code', '')}".strip()

                sqft = p.get('sqft') or 0
                estimate = p.get('estimate') or 0
                estimate_per_sqft = estimate / sqft if sqft and estimate else 0

                formatted_comparables.append({
                    'address': address or 'N/A',
                    'distance_miles': round(p['_distance_miles'], 2),
                    'bedrooms': p.get('beds', 'N/A'),
                    'bathrooms': p.get('baths', 'N/A'),
                    'building_size_sqft': sqft,
                    'listing_status': p.get('status', 'N/A'),
                    'estimated_value': f"${estimate:,}" if estimate else "N/A",
                    'raw_estimated_value': estimate,
                    'estimated_value_per_sqft': f"${estimate_per_sqft:.2f}" if estimate_per_sqft else "N/A",
                    'raw_estimated_value_per_sqft': estimate_per_sqft,
                    'list_price': f"${p.get('list_price'):,}" if p.get('list_price') else "N/A",
                    'last_sale_price': f"${p.get('last_sold_price'):,}" if p.get('last_sold_price') else "N/A",
                    'last_sale_date': p.get('last_sold_date', 'N/A'),
                    'property_id': p.get('property_id')
                })

            return {
                'subject_property': {
                    'address': full_address,
                    'bedrooms': subject_beds,
                    'bathrooms': subject_baths,
                    'sqft': subject_sqft
                },
                'filters_applied': {
                    'bedrooms': subject_beds,
                    'bathrooms': subject_baths if subject_baths else 'Not filtered',
                    'sqft_range': f'{sqft_min:,} - {sqft_max:,}',
                    'sqft_tolerance': f'±{sqft_tolerance}%',
                    'radius_miles': radius_miles
                },
                'total_comparables': len(formatted_comparables),
                'comparables': formatted_comparables,
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            error_msg = f"Failed to get similar properties: {str(e)[:100]}"
            logger.error(error_msg)
            return {
                'error': error_msg,
                'address': f"{street}, {city}, {state} {zip_code}",
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    def _format_address_from_components(self, address_components: Dict) -> str:
        """Format address from API components"""
        try:
            street_num = address_components.get('streetNumber', '')
            street_name = address_components.get('streetName', '')
            city = address_components.get('locality', '')
            state = address_components.get('countrySubd', '')
            zip_code = address_components.get('postal1', '')
            
            # Build formatted address
            address_parts = []
            if street_num:
                address_parts.append(str(street_num))
            if street_name:
                address_parts.append(street_name)
            
            street_address = ' '.join(address_parts)
            
            location_parts = []
            if city:
                location_parts.append(city)
            if state:
                location_parts.append(state)
            if zip_code:
                location_parts.append(zip_code)
            
            if street_address and location_parts:
                return f"{street_address}, {', '.join(location_parts)}"
            elif street_address:
                return street_address
            else:
                return "Address unavailable"
                
        except Exception as e:
            logger.warning(f"Error formatting address: {str(e)}")
            return "Address formatting error"
    
    def get_comprehensive_analysis(self, address: str) -> Dict:
        """
        Complete comprehensive analysis: Basic Profile + AVM + Timeline + Charts
        This is the ultimate property analysis combining all data sources
        """
        print(f"🎯 Starting comprehensive analysis for: {address}")
        print("📊 This will gather ALL available data and open interactive charts...")
        
        try:
            # Get all data sources
            print("📋 1/4 - Getting basic property profile...")
            basic_profile = self.get_basic_profile_report(address)
            
            print("💰 2/4 - Getting AVM valuation data...")
            avm_data = self.get_property_report(address)
            
            print("🎯 3/4 - Getting comprehensive timeline...")
            timeline_data = self.get_all_events_report(address)
            
            print("📊 4/4 - Getting assessment history for charts...")
            assessment_history = self.get_assessment_history_report(address)
            
            # Combine all data
            comprehensive_report = {
                'address': basic_profile.get('address', address),
                'analysis_type': 'comprehensive',
                'data_sources': {
                    'basic_profile': {
                        'available': 'error' not in basic_profile,
                        'data': basic_profile
                    },
                    'avm_valuation': {
                        'available': 'error' not in avm_data,
                        'data': avm_data
                    },
                    'comprehensive_timeline': {
                        'available': 'error' not in timeline_data,
                        'data': timeline_data
                    },
                    'assessment_history': {
                        'available': 'error' not in assessment_history,
                        'data': assessment_history
                    }
                },
                'summary': self._create_comprehensive_summary(basic_profile, avm_data, timeline_data, assessment_history),
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Auto-open charts in browser
            print("🌐 Opening interactive charts in your browser...")
            self._open_charts_in_browser(address)
            
            return comprehensive_report
            
        except Exception as e:
            return {
                'error': f'Comprehensive analysis failed: {str(e)}',
                'address': address,
                'data_retrieved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def _create_comprehensive_summary(self, basic_profile: Dict, avm_data: Dict, timeline_data: Dict, assessment_history: Dict) -> Dict:
        """Create a summary of all available data"""
        summary = {
            'property_overview': {},
            'valuation_summary': {},
            'timeline_summary': {},
            'assessment_trends': {}
        }
        
        # Basic property info
        if 'error' not in basic_profile:
            if 'property_size' in basic_profile:
                summary['property_overview']['size'] = basic_profile['property_size']
            if 'year_built' in basic_profile:
                summary['property_overview']['year_built'] = basic_profile['year_built']
            if 'property_type' in basic_profile:
                summary['property_overview']['type'] = basic_profile['property_type']
        
        # AVM valuation
        if 'error' not in avm_data:
            if 'current_estimated_value' in avm_data:
                summary['valuation_summary']['current_estimate'] = avm_data['current_estimated_value']
            if 'confidence_score' in avm_data:
                summary['valuation_summary']['confidence'] = avm_data['confidence_score']
        
        # Timeline events
        if 'error' not in timeline_data:
            if 'total_events' in timeline_data:
                summary['timeline_summary']['total_events'] = timeline_data['total_events']
            if 'event_categories' in timeline_data:
                summary['timeline_summary']['categories'] = timeline_data['event_categories']
        
        # Assessment history
        if 'error' not in assessment_history:
            if 'total_assessments' in assessment_history:
                summary['assessment_trends']['total_records'] = assessment_history['total_assessments']
            if 'assessment_years' in assessment_history:
                summary['assessment_trends']['year_range'] = f"{assessment_history['assessment_years'][-1]} - {assessment_history['assessment_years'][0]}"
                
                # Calculate growth if we have multiple assessments
                assessments = assessment_history.get('assessments', [])
                if len(assessments) >= 2:
                    first = assessments[-1]['raw_total_assessed']  # Oldest
                    last = assessments[0]['raw_total_assessed']    # Most recent
                    growth = ((last - first) / first) * 100 if first > 0 else 0
                    summary['assessment_trends']['value_growth'] = f"{growth:.1f}%"
        
        return summary
    
    def _open_charts_in_browser(self, address: str):
        """Open the interactive charts in the default web browser"""
        import webbrowser
        import urllib.parse
        
        try:
            # URL encode the address for the query parameter
            encoded_address = urllib.parse.quote(address)
            chart_url = f"http://localhost:5000/charts?address={encoded_address}"
            
            print(f"🌐 Opening: {chart_url}")
            webbrowser.open(chart_url)
            print("✅ Charts opened in your default browser!")
            print("💡 If charts don't auto-load, make sure the Flask server is running:")
            print("   python3 property_rest_api.py")
            
        except Exception as e:
            print(f"⚠️  Could not auto-open browser: {e}")
            print("🌐 Manually visit: http://localhost:5000/charts")
            print(f"📍 Then enter address: {address}")


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
        print("5. Comprehensive analysis (Basic + AVM + Timeline + Charts)")
        print("6. All events snapshot (comprehensive timeline)")
        print("7. Assessment history (charts data)")
        print("8. Similar properties with AVM data")
        print("9. Quit")

        choice = input("\nSelect option (1-9): ").strip()
        
        if choice in ['9', 'quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if choice not in ['1', '2', '3', '4', '5', '6', '7', '8']:
            print("Please select a valid option (1-9)")
            continue

        # Get address input (all options now use the same input)
        address = input("Enter property address: ").strip()
        if not address:
            print("Please enter a valid address")
            continue

        # Special handling for similar properties - parse address into components
        if choice == '8':
            print(f"\n🔍 Finding similar properties with AVM data...")
            try:
                # Parse address into components
                addr_parts = service.parse_address(address)
                street = addr_parts.get('street', '')
                city = addr_parts.get('city', '')
                state = addr_parts.get('state', '')
                zip_code = addr_parts.get('zip', '')
                county = ''  # County not required

                report = service.get_similar_properties_with_sales(street, city, county, state, zip_code)
            except Exception as e:
                print(f"❌ Error parsing address: {str(e)}")
                continue
        else:
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
                # Comprehensive analysis - get all data and open charts
                report = service.get_comprehensive_analysis(address)
            elif choice == '6':
                report = service.get_all_events_report(address)
            elif choice == '7':
                report = service.get_assessment_history_report(address)
        
        print("\n" + "=" * 60)
        print("🏠 PROPERTY REPORT")
        print("=" * 60)
        
        # Special handling for comprehensive analysis
        if choice == '5' and 'analysis_type' in report and report['analysis_type'] == 'comprehensive':
            print("🎯 COMPREHENSIVE PROPERTY ANALYSIS")
            print("=" * 60)
            
            if 'error' in report:
                print(f"❌ Error: {report['error']}")
            else:
                print(f"📍 Address: {report['address']}")
                
                # Show data source availability
                print("\n📊 DATA SOURCES:")
                sources = report.get('data_sources', {})
                for source_name, source_info in sources.items():
                    status = "✅ Available" if source_info.get('available') else "❌ Not available"
                    print(f"   {source_name.replace('_', ' ').title()}: {status}")
                
                # Show comprehensive summary
                if 'summary' in report:
                    summary = report['summary']
                    
                    if summary.get('property_overview'):
                        print("\n🏡 PROPERTY OVERVIEW:")
                        overview = summary['property_overview']
                        if 'size' in overview:
                            print(f"   Size: {overview['size']}")
                        if 'year_built' in overview:
                            print(f"   Built: {overview['year_built']}")
                        if 'type' in overview:
                            print(f"   Type: {overview['type']}")
                    
                    if summary.get('valuation_summary'):
                        print("\n💰 VALUATION SUMMARY:")
                        valuation = summary['valuation_summary']
                        if 'current_estimate' in valuation:
                            print(f"   Current Estimate: {valuation['current_estimate']}")
                        if 'confidence' in valuation:
                            print(f"   Confidence: {valuation['confidence']}")
                    
                    if summary.get('timeline_summary'):
                        print("\n🎯 TIMELINE SUMMARY:")
                        timeline = summary['timeline_summary']
                        if 'total_events' in timeline:
                            print(f"   Total Events: {timeline['total_events']}")
                        if 'categories' in timeline:
                            print(f"   Event Categories: {timeline['categories']}")
                    
                    if summary.get('assessment_trends'):
                        print("\n📊 ASSESSMENT TRENDS:")
                        trends = summary['assessment_trends']
                        if 'total_records' in trends:
                            print(f"   Assessment Records: {trends['total_records']}")
                        if 'year_range' in trends:
                            print(f"   Year Range: {trends['year_range']}")
                        if 'value_growth' in trends:
                            print(f"   Value Growth: {trends['value_growth']}")
                
                print(f"\n✅ Comprehensive analysis complete!")
                print(f"🌐 Interactive charts should open automatically in your browser")
                print(f"⏰ Data retrieved: {report['data_retrieved']}")

        # Special handling for sales comparables
        elif choice == '8':
            print("🏘️  SIMILAR PROPERTIES WITH ASSESSMENT DATA")
            print("=" * 60)

            if 'error' in report:
                print(f"❌ Error: {report['error']}")
            else:
                # Show subject property info
                if 'subject_property' in report:
                    subject = report['subject_property']
                    print(f"\n🏠 Subject Property:")
                    print(f"   Address: {subject.get('address', 'N/A')}")
                    if subject.get('bedrooms'):
                        print(f"   Bedrooms: {subject['bedrooms']}")
                    if subject.get('bathrooms'):
                        print(f"   Bathrooms: {subject['bathrooms']}")
                    if subject.get('sqft'):
                        print(f"   Square Feet: {subject['sqft']:,}")

                # Show filters applied
                if 'filters_applied' in report:
                    filters = report['filters_applied']
                    print(f"\n🔍 Filters Applied:")
                    print(f"   Bedrooms: {filters.get('bedrooms', 'N/A')}")
                    print(f"   Bathrooms: {filters.get('bathrooms', 'N/A')}")
                    print(f"   Sqft Range: {filters.get('sqft_range', 'N/A')} ({filters.get('sqft_tolerance', 'N/A')})")
                    print(f"   Radius: {filters.get('radius_miles', 'N/A')} miles")

                total_comps = report.get('total_comparables', 0)
                print(f"\n📊 Found {total_comps} similar properties (15 closest)")

                if total_comps > 0:
                    comparables = report.get('comparables', [])

                    for i, comp in enumerate(comparables, 1):
                        print(f"\n🏠 Property #{i}")
                        print(f"   Address: {comp.get('address', 'N/A')}")
                        print(f"   Distance: {comp.get('distance_miles', 'N/A')} miles")
                        print(f"   Beds/Baths: {comp.get('bedrooms', 'N/A')}/{comp.get('bathrooms', 'N/A')}")
                        print(f"   Size: {comp.get('building_size_sqft', 'N/A')} sq ft")
                        print(f"   Year Built: {comp.get('year_built', 'N/A')}")
                        print(f"   💰 AVM Value: {comp.get('avm_value', 'N/A')} ({comp.get('avm_per_sqft', 'N/A')}/sqft)")
                        print(f"   📊 Confidence Score: {comp.get('confidence_score', 'N/A')}/100")
                        print(f"   📈 Value Range: {comp.get('avm_value_low', 'N/A')} - {comp.get('avm_value_high', 'N/A')}")
                        print(f"   🏛️ Assessed Value: {comp.get('assessed_value', 'N/A')} ({comp.get('assessed_per_sqft', 'N/A')}/sqft)")
                        print(f"   📅 Event Date: {comp.get('event_date', 'N/A')}")

                        if i >= 15:  # Limit display to 15 comparables
                            break

            print(f"\n⏰ Data retrieved: {report.get('data_retrieved', 'N/A')}")

        elif 'error' in report:
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