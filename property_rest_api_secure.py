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

@app.route('/', methods=['GET'])
def api_documentation():
    """API documentation endpoint"""
    return jsonify({
        'service': 'Property API Service (Secure)',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'This documentation',
            'GET /health': 'Health check',
            'POST /property/combined': 'Combined property report with fallback',
            'POST /property/avm': 'AVM property report only',
            'POST /property/basic': 'Basic property profile only',
            'POST /property/comprehensive': 'Comprehensive analysis (AVM + Basic + Assessment History + Auto-Charts)',
            'GET /salescomparables/address/{street}/{city}/{county}/{state}/{zip}': 'Sales comparables by address path',
            'GET /salescomparables/propid/{propId}': 'Sales comparables by property ID (recommended)'
        },
        'request_format': {
            'address': '123 Main St, Boston, MA 02101'
        },
        'security_features': [
            'Input validation and sanitization',
            'Request timeouts and DoS protection',
            'API key security',
            'Secure logging',
            'Financial data validation',
            'Generic error handling'
        ]
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

@app.route('/property/comprehensive', methods=['POST'])
@validate_address_input
def get_comprehensive_analysis():
    """
    Get comprehensive property analysis (AVM + Basic + Assessment History + Auto-Charts)
    
    POST /property/comprehensive
    Body: {"address": "123 Main St, Boston, MA 02101"}
    
    This endpoint provides the ultimate analysis combining:
    - AVM property valuation
    - Basic property profile
    - Assessment history timeline
    - Automatic chart opening in browser
    """
    try:
        data = request.validated_data
        address = data['address']
        
        result = property_service.get_comprehensive_analysis(address)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Comprehensive analysis error: {str(e)[:100]}")
        return jsonify({
            'error': 'Failed to get comprehensive analysis',
            'message': 'Unable to process comprehensive property analysis'
        }), 500

@app.route('/salescomparables/address/<path:street>/<city>/<county>/<state>/<zip>', methods=['GET'])
def get_sales_comparables_by_path(street, city, county, state, zip):
    """
    Get sales comparables by address path parameters
    
    GET /salescomparables/address/{street}/{city}/{county}/{state}/{zip}
    
    Example: /salescomparables/address/123 Main St/Boston/Suffolk/MA/02101
    """
    try:
        # Construct address from path parameters
        address = f"{street}, {city}, {state} {zip}"
        
        # Validate address using the service's validation method
        try:
            validated_address = property_service.validate_and_sanitize_address(address)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        
        # Get sales comparables
        result = property_service.get_sales_comparables_report(validated_address)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Sales comparables error: {str(e)[:100]}")
        return jsonify({
            'error': 'Failed to get sales comparables',
            'message': 'Unable to process sales comparables request'
        }), 500

@app.route('/salescomparables/propid/<propId>', methods=['GET'])
def get_sales_comparables_by_propid(propId):
    """
    Get sales comparables by property ID
    
    GET /salescomparables/propid/{propId}
    
    Example: /salescomparables/propid/12345678
    """
    try:
        # Validate propId (basic validation)
        if not propId or not propId.isdigit():
            return jsonify({'error': 'Invalid property ID format'}), 400
        
        # Get sales comparables using propId (no address available for price filtering in this endpoint)
        result = property_service.get_sales_comparables_by_propid(propId)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Sales comparables by propId error: {str(e)[:100]}")
        return jsonify({
            'error': 'Failed to get sales comparables',
            'message': 'Unable to process sales comparables request by property ID'
        }), 500

@app.route('/property/propid', methods=['POST'])
@validate_address_input
def get_property_id():
    """
    Get property ID for a given address
    
    POST /property/propid
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.validated_data
        address = data['address']
        
        result = property_service.get_property_id(address)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Property ID error: {str(e)[:100]}")
        return jsonify({
            'error': 'Failed to get property ID',
            'message': 'Unable to retrieve property identifier'
        }), 500

@app.route('/salescomparables/propid/<propId>/raw', methods=['GET'])
def get_raw_sales_comparables_by_propid(propId):
    """
    Get RAW sales comparables data by property ID (for debugging)
    
    GET /salescomparables/propid/{propId}/raw
    """
    try:
        if not propId or not propId.isdigit():
            return jsonify({'error': 'Invalid property ID format'}), 400
        
        # Get raw sales comparables data
        result = property_service.get_sales_comparables_by_propid_raw(propId)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Raw sales comparables error: {str(e)[:100]}")
        return jsonify({
            'error': 'Failed to get raw sales comparables',
            'message': str(e)[:100]
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)