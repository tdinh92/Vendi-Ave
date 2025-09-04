"""
REST API wrapper for Property API Service
Provides HTTP endpoints for property valuation services with enhanced security
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from property_api_service import PropertyAPIService
import json
import logging
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the service once
property_service = PropertyAPIService()

def validate_address_input(f):
    """Decorator to validate address input for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            data = request.get_json()
            
            if not data or 'address' not in data:
                return jsonify({
                    'error': 'Address is required',
                    'example': {'address': '123 Main St, Boston, MA 02101'}
                }), 400
            
            address = data['address']
            if not isinstance(address, str):
                return jsonify({'error': 'Address must be a string'}), 400
            
            # Use the service's validation method
            try:
                validated_address = property_service.validate_and_sanitize_address(address)
                # Store the validated address back in request data
                data['address'] = validated_address
                request.validated_data = data
            except ValueError as ve:
                return jsonify({'error': str(ve)}), 400
            
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Address validation error: {str(e)[:100]}")
            return jsonify({'error': 'Invalid request format'}), 400
    
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Property Valuation API'
    })

@app.route('/property/combined', methods=['POST'])
@validate_address_input
def get_combined_report():
    """
    Get combined property report (AVM + Basic Profile fallback)
    
    POST /property/combined
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.validated_data
        address = data['address']
        
        result = property_service.get_combined_report(address)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Combined report error: {str(e)[:100]}")
        return jsonify({
            'error': 'Failed to get combined report',
            'message': 'Unable to process property data'
        }), 500

@app.route('/property/avm', methods=['POST'])
@validate_address_input
def get_avm_report():
    """
    Get AVM property report only
    
    POST /property/avm
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.validated_data
        address = data['address']
        
        result = property_service.get_property_report(address)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AVM report error: {str(e)[:100]}")
        return jsonify({
            'error': 'Failed to get AVM report',
            'message': 'Unable to process valuation data'
        }), 500

@app.route('/property/basic', methods=['POST'])
@validate_address_input
def get_basic_profile():
    """
    Get basic property profile only
    
    POST /property/basic
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.validated_data
        address = data['address']
        
        result = property_service.get_basic_profile_report(address)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Basic profile error: {str(e)[:100]}")
        return jsonify({
            'error': 'Failed to get basic profile',
            'message': 'Unable to process property profile'
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)