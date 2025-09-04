"""
Unit tests for PropertyAPIService class
Tests core functionality, data processing, and error handling
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from property_api_service import PropertyAPIService


class TestPropertyAPIService:
    """Test suite for PropertyAPIService class"""
    
    @pytest.fixture
    def service(self):
        """Create PropertyAPIService instance for testing"""
        return PropertyAPIService()
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables"""
        with patch.dict(os.environ, {'ATTOM_API_KEY': 'test_api_key_12345'}):
            yield
    
    def test_init(self, mock_env_vars):
        """Test service initialization"""
        service = PropertyAPIService()
        assert service.api_key == 'test_api_key_12345'
        assert service.base_url == 'https://search.onboard-apis.com'
    
    def test_parse_address_valid(self, service):
        """Test address parsing with valid address"""
        address = "123 Main St, Boston, MA 02101"
        result = service.parse_address(address)
        
        assert result['address1'] == "123 Main St"
        assert result['address2'] == "Boston, MA 02101"
    
    def test_parse_address_empty(self, service):
        """Test address parsing with empty address"""
        with pytest.raises(ValueError, match="Address cannot be empty"):
            service.parse_address("")
    
    def test_parse_address_no_comma(self, service):
        """Test address parsing with no comma separator"""
        address = "123 Main Street Boston MA"
        result = service.parse_address(address)
        
        assert result['address1'] == address
        assert result['address2'] == ""
    
    @patch('requests.get')
    def test_get_basic_profile_success(self, mock_get, service, mock_env_vars):
        """Test successful basic profile retrieval"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'property': [{
                'address': {'oneLine': '123 MAIN ST, BOSTON, MA 02101'},
                'building': {'size': {'bldgSize': 2000}},
                'lot': {'lotSize1': 0.25},
                'summary': {'yearBuilt': 1995, 'bedrooms': 3, 'bathsFull': 2}
            }]
        }
        mock_get.return_value = mock_response
        
        result = service.get_basic_profile("123 Main St, Boston, MA 02101")
        
        assert result['status']['msg'] == 'SuccessWithResult'
        assert len(result['property']) == 1
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_basic_profile_api_error(self, mock_get, service, mock_env_vars):
        """Test basic profile with API error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'status': {'msg': 'No records found'}}
        mock_get.return_value = mock_response
        
        result = service.get_basic_profile("123 Nonexistent St, Boston, MA 02101")
        
        assert result['status']['msg'] == 'No records found'
    
    @patch('requests.get')
    def test_get_avm_history_success(self, mock_get, service, mock_env_vars):
        """Test successful AVM history retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': {'msg': 'SuccessWithResult'},
            'avm': [{
                'address': {'oneLine': '123 MAIN ST, BOSTON, MA 02101'},
                'avm': {
                    'avmValue': 500000,
                    'avmConfidenceScore': 95,
                    'avmEstimateDate': '2024-01-15'
                }
            }]
        }
        mock_get.return_value = mock_response
        
        result = service.get_avm_history("123 Main St, Boston, MA 02101")
        
        assert result['status']['msg'] == 'SuccessWithResult'
        assert len(result['avm']) == 1
        assert result['avm'][0]['avm']['avmValue'] == 500000
    
    def test_clean_basic_profile_for_homeowners(self, service):
        """Test basic profile data cleaning for homeowner display"""
        raw_data = {
            'status': {'msg': 'SuccessWithResult'},
            'property': [{
                'address': {'oneLine': '123 MAIN ST, BOSTON, MA 02101'},
                'building': {'size': {'bldgSize': 2000}},
                'lot': {'lotSize1': 0.25},
                'summary': {'yearBuilt': 1995, 'bedrooms': 3, 'bathsFull': 2.5},
                'owner': {'owner1': {'firstName': 'John', 'lastName': 'Doe'}},
                'sale': {'saleRecDate': '2020-05-15', 'amount': {'saleAmt': 450000}},
                'assessment': {'assessed': {'assdTtlValue': 400000}}
            }]
        }
        
        result = service.clean_basic_profile_for_homeowners(raw_data)
        
        assert result['address'] == '123 MAIN ST, BOSTON, MA 02101'
        assert result['property_size'] == '2,000 sqft'
        assert result['lot_size'] == '0.25 acres'
        assert result['year_built'] == '1995'
        assert result['bedrooms'] == 3
        assert result['bathrooms'] == 2.5
        assert result['owner'] == 'John Doe'
        assert result['last_sale_price'] == '$450,000'
        assert result['current_assessment'] == '$400,000'
    
    def test_clean_basic_profile_empty_data(self, service):
        """Test basic profile cleaning with empty/missing data"""
        raw_data = {
            'status': {'msg': 'SuccessWithResult'},
            'property': [{}]
        }
        
        result = service.clean_basic_profile_for_homeowners(raw_data)
        
        assert result['address'] == 'N/A'
        assert result['property_size'] == 'N/A'
        assert result['year_built'] == 'N/A'
        assert result['owner'] == 'N/A'
    
    def test_clean_data_for_homeowners_avm(self, service):
        """Test AVM data cleaning for homeowner display"""
        raw_data = {
            'status': {'msg': 'SuccessWithResult'},
            'avm': [{
                'address': {'oneLine': '123 MAIN ST, BOSTON, MA 02101'},
                'avm': {
                    'avmValue': 500000,
                    'avmConfidenceScore': 95,
                    'avmEstimateDate': '2024-01-15',
                    'avmFsdLow': 475000,
                    'avmFsdHigh': 525000
                },
                'building': {'size': {'bldgSize': 2000}},
                'summary': {'yearBuilt': 1995, 'bedrooms': 3, 'bathsFull': 2.5},
                'lot': {'lotSize1': 0.25}
            }]
        }
        
        result = service.clean_data_for_homeowners(raw_data)
        
        assert result['current_estimated_value'] == '$500,000'
        assert result['confidence_score'] == '95/100'
        assert result['value_range_low'] == '$475,000'
        assert result['value_range_high'] == '$525,000'
        assert result['property_size'] == '2,000 sqft'
        assert result['bedrooms'] == 3
    
    @patch('property_api_service.PropertyAPIService.get_basic_profile')
    def test_get_basic_profile_report_success(self, mock_get_basic, service):
        """Test basic profile report generation"""
        mock_get_basic.return_value = {
            'status': {'msg': 'SuccessWithResult'},
            'property': [{'address': {'oneLine': '123 MAIN ST, BOSTON, MA 02101'}}]
        }
        
        result = service.get_basic_profile_report("123 Main St, Boston, MA 02101")
        
        assert 'address' in result
        assert 'data_retrieved' in result
        mock_get_basic.assert_called_once_with("123 Main St, Boston, MA 02101")
    
    @patch('property_api_service.PropertyAPIService.get_avm_history')
    def test_get_property_report_success(self, mock_get_avm, service):
        """Test AVM property report generation"""
        mock_get_avm.return_value = {
            'status': {'msg': 'SuccessWithResult'},
            'avm': [{'address': {'oneLine': '123 MAIN ST, BOSTON, MA 02101'}}]
        }
        
        result = service.get_property_report("123 Main St, Boston, MA 02101")
        
        assert 'address' in result
        assert 'data_retrieved' in result
        mock_get_avm.assert_called_once_with("123 Main St, Boston, MA 02101")
    
    @patch('property_api_service.PropertyAPIService.get_property_report')
    @patch('property_api_service.PropertyAPIService.get_basic_profile_report')
    def test_get_combined_report_avm_available(self, mock_basic, mock_avm, service):
        """Test combined report when AVM data is available"""
        mock_avm.return_value = {
            'address': '123 MAIN ST, BOSTON, MA 02101',
            'current_estimated_value': '$500,000'
        }
        mock_basic.return_value = {
            'address': '123 MAIN ST, BOSTON, MA 02101',
            'property_size': '2,000 sqft'
        }
        
        result = service.get_combined_report("123 Main St, Boston, MA 02101")
        
        assert result['current_estimated_value'] == '$500,000'
        assert result['property_size'] == '2,000 sqft'
        mock_avm.assert_called_once()
        mock_basic.assert_called_once()
    
    @patch('property_api_service.PropertyAPIService.get_property_report')
    @patch('property_api_service.PropertyAPIService.get_basic_profile_report')
    def test_get_combined_report_avm_error(self, mock_basic, mock_avm, service):
        """Test combined report when AVM has error (falls back to basic)"""
        mock_avm.return_value = {'error': 'AVM data not available'}
        mock_basic.return_value = {
            'address': '123 MAIN ST, BOSTON, MA 02101',
            'property_size': '2,000 sqft'
        }
        
        result = service.get_combined_report("123 Main St, Boston, MA 02101")
        
        assert 'valuation_note' in result
        assert result['property_size'] == '2,000 sqft'
    
    @patch('requests.get')
    def test_get_assessment_history_success(self, mock_get, service, mock_env_vars):
        """Test successful assessment history retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': {'msg': 'SuccessWithResult'},
            'property': [{
                'assessmenthistory': [{
                    'taxyear': '2024',
                    'assessed': {'assdTtlValue': 500000},
                    'tax': {'taxAmt': 12000}
                }]
            }]
        }
        mock_get.return_value = mock_response
        
        result = service.get_assessment_history("123 Main St, Boston, MA 02101")
        
        assert result['status']['msg'] == 'SuccessWithResult'
        assert len(result['property'][0]['assessmenthistory']) == 1
    
    def test_clean_assessment_history_for_homeowners(self, service):
        """Test assessment history data cleaning"""
        raw_data = {
            'status': {'msg': 'SuccessWithResult'},
            'property': [{
                'address': {'oneLine': '123 MAIN ST, BOSTON, MA 02101'},
                'building': {'size': {'bldgSize': 2000}},
                'assessmenthistory': [{
                    'taxyear': '2024',
                    'assessed': {'assdTtlValue': 500000, 'assdLandValue': 100000, 'assdImpValue': 400000},
                    'tax': {'taxAmt': 12000}
                }, {
                    'taxyear': '2023',
                    'assessed': {'assdTtlValue': 480000, 'assdLandValue': 95000, 'assdImpValue': 385000},
                    'tax': {'taxAmt': 11500}
                }]
            }]
        }
        
        result = service.clean_assessment_history_for_homeowners(raw_data)
        
        assert result['address'] == '123 MAIN ST, BOSTON, MA 02101'
        assert result['total_assessments'] == 2
        assert len(result['assessments']) == 2
        assert result['assessments'][0]['tax_year'] == '2024'
        assert result['assessments'][0]['total_assessed_value'] == '$500,000'
        assert result['assessments'][0]['raw_total_assessed'] == 500000
    
    @patch('webbrowser.open')
    def test_open_charts_in_browser(self, mock_browser, service):
        """Test opening charts in browser"""
        service._open_charts_in_browser("123 Main St, Boston, MA 02101")
        
        expected_url = "http://localhost:5000/charts?address=123%20Main%20St%2C%20Boston%2C%20MA%2002101"
        mock_browser.assert_called_once_with(expected_url)
    
    @patch('property_api_service.PropertyAPIService.get_basic_profile_report')
    @patch('property_api_service.PropertyAPIService.get_property_report')
    @patch('property_api_service.PropertyAPIService.get_all_events_report')
    @patch('property_api_service.PropertyAPIService.get_assessment_history_report')
    @patch('property_api_service.PropertyAPIService._open_charts_in_browser')
    def test_get_comprehensive_analysis(self, mock_charts, mock_assessment, mock_events, mock_avm, mock_basic, service):
        """Test comprehensive analysis combining all data sources"""
        # Setup mock returns
        mock_basic.return_value = {'address': '123 MAIN ST', 'property_size': '2,000 sqft'}
        mock_avm.return_value = {'address': '123 MAIN ST', 'current_estimated_value': '$500,000'}
        mock_events.return_value = {'address': '123 MAIN ST', 'total_events': 5}
        mock_assessment.return_value = {'address': '123 MAIN ST', 'total_assessments': 10}
        
        result = service.get_comprehensive_analysis("123 Main St, Boston, MA 02101")
        
        assert result['analysis_type'] == 'comprehensive'
        assert 'data_sources' in result
        assert 'summary' in result
        assert result['data_sources']['basic_profile']['available'] is True
        
        # Verify all methods were called
        mock_basic.assert_called_once()
        mock_avm.assert_called_once()
        mock_events.assert_called_once()
        mock_assessment.assert_called_once()
        mock_charts.assert_called_once()

    def test_error_handling_invalid_address(self, service):
        """Test error handling for invalid addresses"""
        with pytest.raises(ValueError):
            service.parse_address(None)
        
        with pytest.raises(ValueError):
            service.parse_address("")
    
    @patch('requests.get')
    def test_api_timeout_handling(self, mock_get, service, mock_env_vars):
        """Test handling of API timeouts"""
        mock_get.side_effect = Exception("Request timeout")
        
        result = service.get_basic_profile("123 Main St, Boston, MA 02101")
        
        assert 'error' in result
    
    @patch('requests.get')
    def test_api_rate_limit_handling(self, mock_get, service, mock_env_vars):
        """Test handling of API rate limits"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {'error': 'Rate limit exceeded'}
        mock_get.return_value = mock_response
        
        result = service.get_basic_profile("123 Main St, Boston, MA 02101")
        
        assert result.get('error') == 'Rate limit exceeded'
    
    def test_data_validation_empty_response(self, service):
        """Test validation of empty API responses"""
        empty_data = {'status': {'msg': 'SuccessWithResult'}, 'property': []}
        
        result = service.clean_basic_profile_for_homeowners(empty_data)
        
        # Should handle gracefully with N/A values
        assert result['address'] == 'N/A'
        assert result['property_size'] == 'N/A'
    
    def test_currency_formatting(self, service):
        """Test currency formatting in data cleaning"""
        raw_data = {
            'status': {'msg': 'SuccessWithResult'},
            'avm': [{
                'avm': {'avmValue': 1234567.89},
                'address': {'oneLine': '123 MAIN ST'}
            }]
        }
        
        result = service.clean_data_for_homeowners(raw_data)
        
        assert result['current_estimated_value'] == '$1,234,568'  # Rounded to nearest dollar
    
    def test_date_formatting(self, service):
        """Test date formatting in cleaned data"""
        result = service.clean_basic_profile_for_homeowners({
            'status': {'msg': 'SuccessWithResult'},
            'property': [{}]
        })
        
        # Should have current timestamp
        assert 'data_retrieved' in result
        assert len(result['data_retrieved']) > 10  # Should be a formatted datetime string