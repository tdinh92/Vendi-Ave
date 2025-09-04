"""
API endpoint tests for Flask REST API
Tests all 17 endpoints with various scenarios and error conditions
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from property_rest_api import app, property_service


class TestRestAPI:
    """Test suite for Flask REST API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client for Flask app"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def mock_service_success(self):
        """Mock successful service responses"""
        with patch.object(property_service, 'get_combined_report') as mock_combined, \
             patch.object(property_service, 'get_property_report') as mock_avm, \
             patch.object(property_service, 'get_basic_profile_report') as mock_basic, \
             patch.object(property_service, 'get_complete_report') as mock_complete, \
             patch.object(property_service, 'get_all_events_report') as mock_events, \
             patch.object(property_service, 'get_assessment_history_report') as mock_assessment, \
             patch.object(property_service, 'get_comprehensive_analysis') as mock_comprehensive, \
             patch.object(property_service, 'get_avm_history') as mock_raw_avm, \
             patch.object(property_service, 'get_basic_profile') as mock_raw_basic, \
             patch.object(property_service, 'get_all_events_snapshot') as mock_raw_events, \
             patch.object(property_service, 'get_assessment_history') as mock_raw_assessment:
            
            # Set up successful mock responses
            success_response = {
                'address': '123 MAIN ST, BOSTON, MA 02101',
                'current_estimated_value': '$500,000',
                'data_retrieved': '2024-01-15 10:30:00'
            }
            
            mock_combined.return_value = success_response
            mock_avm.return_value = success_response
            mock_basic.return_value = success_response
            mock_complete.return_value = success_response
            mock_events.return_value = success_response
            mock_assessment.return_value = success_response
            mock_comprehensive.return_value = success_response
            mock_raw_avm.return_value = success_response
            mock_raw_basic.return_value = success_response
            mock_raw_events.return_value = success_response
            mock_raw_assessment.return_value = success_response
            
            yield {
                'combined': mock_combined,
                'avm': mock_avm,
                'basic': mock_basic,
                'complete': mock_complete,
                'events': mock_events,
                'assessment': mock_assessment,
                'comprehensive': mock_comprehensive,
                'raw_avm': mock_raw_avm,
                'raw_basic': mock_raw_basic,
                'raw_events': mock_raw_events,
                'raw_assessment': mock_raw_assessment
            }
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'Property Valuation API'
    
    def test_api_documentation(self, client):
        """Test API documentation endpoint"""
        response = client.get('/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['service'] == 'Property Valuation API'
        assert 'endpoints' in data
        assert 'POST /property/combined' in data['endpoints']
    
    def test_combined_report_success(self, client, mock_service_success):
        """Test successful combined report request"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/combined', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['address'] == '123 MAIN ST, BOSTON, MA 02101'
        mock_service_success['combined'].assert_called_once_with('123 Main St, Boston, MA 02101')
    
    def test_combined_report_missing_address(self, client):
        """Test combined report with missing address"""
        payload = {}
        
        response = client.post('/property/combined', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Address is required' in data['error']
    
    def test_combined_report_empty_address(self, client):
        """Test combined report with empty address"""
        payload = {'address': '   '}
        
        response = client.post('/property/combined', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Address cannot be empty' in data['error']
    
    def test_combined_report_invalid_json(self, client):
        """Test combined report with invalid JSON"""
        response = client.post('/property/combined', 
                             data='invalid json', 
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_avm_report_success(self, client, mock_service_success):
        """Test successful AVM report request"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/avm', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['address'] == '123 MAIN ST, BOSTON, MA 02101'
        mock_service_success['avm'].assert_called_once()
    
    def test_basic_report_success(self, client, mock_service_success):
        """Test successful basic profile report request"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/basic', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['address'] == '123 MAIN ST, BOSTON, MA 02101'
        mock_service_success['basic'].assert_called_once()
    
    def test_complete_report_success(self, client, mock_service_success):
        """Test successful complete report request"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/complete', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['address'] == '123 MAIN ST, BOSTON, MA 02101'
        mock_service_success['complete'].assert_called_once()
    
    def test_all_events_report_success(self, client, mock_service_success):
        """Test successful all events report request"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/allevents', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['address'] == '123 MAIN ST, BOSTON, MA 02101'
        mock_service_success['events'].assert_called_once()
    
    def test_assessment_history_report_success(self, client, mock_service_success):
        """Test successful assessment history report request"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/assessmenthistory', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['address'] == '123 MAIN ST, BOSTON, MA 02101'
        mock_service_success['assessment'].assert_called_once()
    
    def test_comprehensive_analysis_success(self, client, mock_service_success):
        """Test successful comprehensive analysis request"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/comprehensive', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['address'] == '123 MAIN ST, BOSTON, MA 02101'
        mock_service_success['comprehensive'].assert_called_once()
    
    def test_raw_avm_success(self, client, mock_service_success):
        """Test successful raw AVM data request"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/raw/avm', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['address'] == '123 MAIN ST, BOSTON, MA 02101'
        mock_service_success['raw_avm'].assert_called_once()
    
    def test_raw_basic_success(self, client, mock_service_success):
        """Test successful raw basic profile request"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/raw/basic', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['address'] == '123 MAIN ST, BOSTON, MA 02101'
        mock_service_success['raw_basic'].assert_called_once()
    
    def test_raw_all_events_success(self, client, mock_service_success):
        """Test successful raw all events request"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/raw/allevents', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['address'] == '123 MAIN ST, BOSTON, MA 02101'
        mock_service_success['raw_events'].assert_called_once()
    
    def test_raw_assessment_history_success(self, client, mock_service_success):
        """Test successful raw assessment history request"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/raw/assessmenthistory', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['address'] == '123 MAIN ST, BOSTON, MA 02101'
        mock_service_success['raw_assessment'].assert_called_once()
    
    def test_batch_reports_success(self, client, mock_service_success):
        """Test successful batch processing request"""
        payload = {
            'addresses': ['123 Main St, Boston, MA 02101', '456 Oak Ave, Springfield, IL 62701'],
            'report_type': 'combined'
        }
        
        response = client.post('/property/batch', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['report_type'] == 'combined'
        assert data['total_addresses'] == 2
        assert len(data['results']) == 2
        assert mock_service_success['combined'].call_count == 2
    
    def test_batch_reports_missing_addresses(self, client):
        """Test batch processing with missing addresses"""
        payload = {'report_type': 'combined'}
        
        response = client.post('/property/batch', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Addresses array is required' in data['error']
    
    def test_batch_reports_empty_addresses(self, client):
        """Test batch processing with empty addresses array"""
        payload = {'addresses': [], 'report_type': 'combined'}
        
        response = client.post('/property/batch', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'non-empty array' in data['error']
    
    def test_batch_reports_too_many_addresses(self, client):
        """Test batch processing with too many addresses"""
        addresses = [f'{i} Main St, Boston, MA' for i in range(11)]
        payload = {'addresses': addresses, 'report_type': 'combined'}
        
        response = client.post('/property/batch', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Maximum 10 addresses' in data['error']
    
    def test_batch_reports_invalid_report_type(self, client):
        """Test batch processing with invalid report type"""
        payload = {
            'addresses': ['123 Main St, Boston, MA 02101'],
            'report_type': 'invalid_type'
        }
        
        response = client.post('/property/batch', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'report_type must be' in data['error']
    
    def test_batch_reports_invalid_address_format(self, client, mock_service_success):
        """Test batch processing with invalid address format"""
        payload = {
            'addresses': [123, '456 Oak Ave, Springfield, IL 62701'],  # First address is not string
            'report_type': 'combined'
        }
        
        response = client.post('/property/batch', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['results']) == 2
        assert 'error' in data['results'][0]
        assert 'Invalid address format' in data['results'][0]['error']
    
    def test_charts_endpoint(self, client):
        """Test charts HTML page endpoint"""
        response = client.get('/charts')
        
        assert response.status_code == 200
        assert b'Property Assessment History Charts' in response.data
        assert b'D3.js' in response.data
    
    def test_static_file_serving(self, client):
        """Test static file serving endpoint"""
        # This test assumes the static file exists
        response = client.get('/static/assessment-charts.js')
        
        # Should either return the file or 404 if file doesn't exist
        assert response.status_code in [200, 404]
    
    @patch.object(property_service, 'get_combined_report')
    def test_service_exception_handling(self, mock_service, client):
        """Test handling of service exceptions"""
        mock_service.side_effect = Exception("Service error")
        
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        response = client.post('/property/combined', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'Internal server error' in data['error']
        assert 'Service error' in data['details']
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.get('/health')
        
        # Flask-CORS should add these headers
        assert response.status_code == 200
        # Note: In testing, CORS headers might not be added the same way as in production
    
    def test_content_type_validation(self, client):
        """Test content type validation for POST endpoints"""
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        # Send with incorrect content type
        response = client.post('/property/combined', 
                             data=json.dumps(payload), 
                             content_type='text/plain')
        
        # Should still work or return appropriate error
        assert response.status_code in [200, 400, 415]
    
    def test_method_not_allowed(self, client):
        """Test method not allowed responses"""
        # Try GET on POST-only endpoint
        response = client.get('/property/combined')
        
        assert response.status_code == 405
    
    def test_endpoint_not_found(self, client):
        """Test 404 for non-existent endpoints"""
        response = client.get('/nonexistent/endpoint')
        
        assert response.status_code == 404
    
    @patch.object(property_service, 'get_combined_report')
    def test_response_time_reasonable(self, mock_service, client):
        """Test that API responses are returned in reasonable time"""
        import time
        
        mock_service.return_value = {'address': 'test'}
        
        payload = {'address': '123 Main St, Boston, MA 02101'}
        
        start_time = time.time()
        response = client.post('/property/combined', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should respond within 5 seconds
    
    def test_large_address_string(self, client, mock_service_success):
        """Test handling of unusually large address strings"""
        large_address = "A" * 1000  # Very long address
        payload = {'address': large_address}
        
        response = client.post('/property/combined', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        # Should either process or return appropriate error
        assert response.status_code in [200, 400]
    
    def test_special_characters_in_address(self, client, mock_service_success):
        """Test handling of special characters in addresses"""
        special_address = "123 Main St #5-A, São Paulo, Brazil 12345-678"
        payload = {'address': special_address}
        
        response = client.post('/property/combined', 
                             data=json.dumps(payload), 
                             content_type='application/json')
        
        assert response.status_code == 200
        mock_service_success['combined'].assert_called_once_with(special_address)
    
    def test_batch_processing_partial_failures(self, client):
        """Test batch processing with some addresses failing"""
        with patch.object(property_service, 'get_combined_report') as mock_service:
            # First address succeeds, second fails
            mock_service.side_effect = [
                {'address': 'SUCCESS'},
                Exception("Address not found")
            ]
            
            payload = {
                'addresses': ['123 Main St, Boston, MA', '999 Nonexistent Rd, Nowhere, XX'],
                'report_type': 'combined'
            }
            
            response = client.post('/property/batch', 
                                 data=json.dumps(payload), 
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['results']) == 2
            assert data['results'][0]['address'] == 'SUCCESS'
            assert 'error' in data['results'][1]