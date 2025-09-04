"""
Integration tests for AVM API system
Tests end-to-end functionality with real components
"""

import pytest
import requests
import time
from unittest.mock import patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from property_api_service import PropertyAPIService


class TestIntegration:
    """Integration test suite for AVM API system"""
    
    @pytest.fixture
    def service(self):
        """Create PropertyAPIService instance for testing"""
        return PropertyAPIService()
    
    @pytest.fixture
    def api_base_url(self):
        """Base URL for API testing"""
        return "http://localhost:5000"
    
    @pytest.mark.integration
    def test_end_to_end_api_workflow(self, api_base_url):
        """Test complete end-to-end API workflow"""
        try:
            test_address = "4 Fiorenza Drive, Wilmington, MA 01887"
            
            # Test health check first
            response = requests.get(f"{api_base_url}/health", timeout=5)
            assert response.status_code == 200
            
            # Test combined endpoint
            response = requests.post(
                f"{api_base_url}/property/combined",
                json={"address": test_address},
                timeout=10
            )
            assert response.status_code == 200
            combined_data = response.json()
            assert 'address' in combined_data
            assert 'data_retrieved' in combined_data
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running - skipping integration test")
    
    def test_address_parsing_edge_cases(self, service):
        """Test address parsing with various real-world formats"""
        test_cases = [
            ("123 Main St, Boston, MA 02101", "123 Main St", "Boston, MA 02101"),
            ("456 Oak Avenue Unit 5, Springfield, IL 62701", "456 Oak Avenue Unit 5", "Springfield, IL 62701"),
            ("789 Pine Dr", "789 Pine Dr", ""),
        ]
        
        for full_address, expected_part1, expected_part2 in test_cases:
            result = service.parse_address(full_address)
            assert result['address1'] == expected_part1
            assert result['address2'] == expected_part2