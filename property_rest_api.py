"""
REST API wrapper for Property API Service
Provides HTTP endpoints for property valuation services
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from property_api_service import PropertyAPIService
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the service once
property_service = PropertyAPIService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Property Valuation API'
    })

@app.route('/property/combined', methods=['POST'])
def get_combined_report():
    """
    Get combined property report (AVM + Basic Profile fallback)
    
    POST /property/combined
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Address is required',
                'example': {'address': '123 Main St, Boston, MA 02101'}
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        result = property_service.get_combined_report(address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/avm', methods=['POST'])
def get_avm_report():
    """
    Get AVM-only property report
    
    POST /property/avm
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Address is required',
                'example': {'address': '123 Main St, Boston, MA 02101'}
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        result = property_service.get_property_report(address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/basic', methods=['POST'])
def get_basic_profile_report():
    """
    Get basic profile property report
    
    POST /property/basic
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Address is required',
                'example': {'address': '123 Main St, Boston, MA 02101'}
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        result = property_service.get_basic_profile_report(address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/raw/avm', methods=['POST'])
def get_raw_avm():
    """
    Get raw AVM data from Attom API
    
    POST /property/raw/avm
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Address is required',
                'example': {'address': '123 Main St, Boston, MA 02101'}
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        result = property_service.get_avm_history(address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/raw/basic', methods=['POST'])
def get_raw_basic():
    """
    Get raw basic profile data from Attom API
    
    POST /property/raw/basic
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Address is required',
                'example': {'address': '123 Main St, Boston, MA 02101'}
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        result = property_service.get_basic_profile(address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/complete', methods=['POST'])
def get_complete_report():
    """
    Get complete property report (both AVM and Basic Profile data)
    
    POST /property/complete
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Address is required',
                'example': {'address': '123 Main St, Boston, MA 02101'}
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        result = property_service.get_complete_report(address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/allevents', methods=['POST'])
def get_all_events_report():
    """
    Get comprehensive all events snapshot (sales, mortgages, assessments, permits, market events)
    
    POST /property/allevents
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Address is required',
                'example': {'address': '123 Main St, Boston, MA 02101'}
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        result = property_service.get_all_events_report(address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/raw/allevents', methods=['POST'])
def get_raw_all_events():
    """
    Get raw all events snapshot data (unprocessed API response)
    
    POST /property/raw/allevents
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Address is required',
                'example': {'address': '123 Main St, Boston, MA 02101'}
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        result = property_service.get_all_events_snapshot(address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/assessmenthistory', methods=['POST'])
def get_assessment_history_report():
    """
    Get property assessment history with historical tax and value data
    
    POST /property/assessmenthistory
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Address is required',
                'example': {'address': '123 Main St, Boston, MA 02101'}
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        result = property_service.get_assessment_history_report(address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/raw/assessmenthistory', methods=['POST'])
def get_raw_assessment_history():
    """
    Get raw assessment history data (unprocessed API response)
    
    POST /property/raw/assessmenthistory
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Address is required',
                'example': {'address': '123 Main St, Boston, MA 02101'}
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        result = property_service.get_assessment_history(address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/batch', methods=['POST'])
def get_batch_reports():
    """
    Get property reports for multiple addresses
    
    POST /property/batch
    Body: {
        "addresses": ["123 Main St, Boston, MA 02101", "456 Oak Ave, Springfield, IL 62701"],
        "report_type": "combined"  // "combined", "avm", or "basic"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'addresses' not in data:
            return jsonify({
                'error': 'Addresses array is required',
                'example': {
                    'addresses': ['123 Main St, Boston, MA 02101'],
                    'report_type': 'combined'
                }
            }), 400
        
        addresses = data['addresses']
        report_type = data.get('report_type', 'combined')
        
        if not isinstance(addresses, list) or len(addresses) == 0:
            return jsonify({'error': 'Addresses must be a non-empty array'}), 400
        
        if len(addresses) > 10:
            return jsonify({'error': 'Maximum 10 addresses per batch request'}), 400
        
        if report_type not in ['combined', 'avm', 'basic']:
            return jsonify({'error': 'report_type must be: combined, avm, or basic'}), 400
        
        results = []
        for address in addresses:
            if not isinstance(address, str) or not address.strip():
                results.append({
                    'address': str(address),
                    'error': 'Invalid address format'
                })
                continue
                
            try:
                if report_type == 'combined':
                    result = property_service.get_combined_report(address.strip())
                elif report_type == 'avm':
                    result = property_service.get_property_report(address.strip())
                elif report_type == 'basic':
                    result = property_service.get_basic_profile_report(address.strip())
                
                results.append(result)
            except Exception as e:
                results.append({
                    'address': address,
                    'error': f'Processing failed: {str(e)}'
                })
        
        return jsonify({
            'report_type': report_type,
            'total_addresses': len(addresses),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/', methods=['GET'])
def api_documentation():
    """API documentation endpoint"""
    return jsonify({
        'service': 'Property Valuation API',
        'version': '1.0.0',
        'endpoints': {
            'GET /health': 'Health check',
            'POST /property/complete': 'Complete report (both AVM and Basic Profile)',
            'POST /property/combined': 'Combined report (AVM + Basic Profile fallback)',
            'POST /property/avm': 'AVM report only',
            'POST /property/basic': 'Basic profile report only',
            'POST /property/allevents': 'All events snapshot (sales, assessments, permits, market events)',
            'POST /property/assessmenthistory': 'Historical property assessments and tax data',
            'POST /property/comprehensive': 'Ultimate analysis (Basic + AVM + Timeline + Auto-Charts)',
            'POST /property/raw/avm': 'Raw AVM data from Attom',
            'POST /property/raw/basic': 'Raw basic profile data from Attom',
            'POST /property/raw/allevents': 'Raw all events data from Attom',
            'POST /property/raw/assessmenthistory': 'Raw assessment history data from Attom',
            'POST /property/batch': 'Batch processing (up to 10 addresses)',
            'GET /charts': 'Interactive D3.js charts for assessment history visualization',
            'GET /salescomparables/address/{street}/{city}/{county}/{state}/{zip}': 'Sales comparables for specific address'
        },
        'request_format': {
            'address': '123 Main St, Boston, MA 02101'
        },
        'batch_format': {
            'addresses': ['123 Main St, Boston, MA 02101', '456 Oak Ave, Springfield, IL 62701'],
            'report_type': 'combined'
        }
    })

@app.route('/charts', methods=['GET'])
def assessment_charts():
    """
    Interactive D3.js charts for property assessment history visualization
    
    GET /charts
    """
    return render_template('assessment_charts.html')

@app.route('/property/comprehensive', methods=['POST'])
def get_comprehensive_analysis():
    """
    Get comprehensive property analysis (Basic + AVM + Timeline + Auto-Charts)
    
    POST /property/comprehensive
    Body: {"address": "123 Main St, Boston, MA 02101"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Address is required',
                'example': {'address': '123 Main St, Boston, MA 02101'}
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        result = property_service.get_comprehensive_analysis(address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/salescomparables', methods=['POST'])
def get_sales_comparables_post():
    """
    Get sales comparables for a property (POST method)

    POST /property/salescomparables
    Body: {
        "street": "4 Fiorenza Drive",
        "city": "Wilmington",
        "county": "Middlesex",
        "state": "MA",
        "zip_code": "01887"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Request body is required',
                'example': {
                    'street': '4 Fiorenza Drive',
                    'city': 'Wilmington',
                    'county': 'Middlesex',
                    'state': 'MA',
                    'zip_code': '01887'
                }
            }), 400

        # County is optional, other fields are required
        required_fields = ['street', 'city', 'state', 'zip_code']
        missing_fields = [field for field in required_fields if field not in data or not data[field].strip()]

        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'required_fields': required_fields
            }), 400

        result = property_service.get_sales_comparables(
            data['street'].strip(),
            data['city'].strip(),
            data.get('county', '').strip(),  # Optional
            data['state'].strip(),
            data['zip_code'].strip()
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/property/similar', methods=['POST'])
def get_similar_properties_with_sales():
    """
    Get 15 closest similar properties with sale history

    POST /property/similar
    Body: {
        "street": "4 Fiorenza Drive",
        "city": "Wilmington",
        "county": "",
        "state": "MA",
        "zip_code": "01887",
        "sqft_tolerance": 10.0,  // Optional, default 10.0 (±10%)
        "radius_miles": 5.0      // Optional, default 5.0
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Request body is required',
                'example': {
                    'street': '4 Fiorenza Drive',
                    'city': 'Wilmington',
                    'county': '',
                    'state': 'MA',
                    'zip_code': '01887',
                    'sqft_tolerance': 10.0,
                    'radius_miles': 5.0
                }
            }), 400

        # Required fields
        required_fields = ['street', 'city', 'state', 'zip_code']
        missing_fields = [field for field in required_fields if field not in data or not data[field].strip()]

        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'required_fields': required_fields
            }), 400

        # Optional parameters with defaults
        sqft_tolerance = float(data.get('sqft_tolerance', 10.0))
        radius_miles = float(data.get('radius_miles', 5.0))

        result = property_service.get_similar_properties_with_sales(
            data['street'].strip(),
            data['city'].strip(),
            data.get('county', '').strip(),
            data['state'].strip(),
            data['zip_code'].strip(),
            sqft_tolerance=sqft_tolerance,
            radius_miles=radius_miles
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    from flask import send_from_directory
    import os
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), filename)

@app.route('/salescomparables/address/<street>/<city>/<county>/<state>/<zip_code>', methods=['GET'])
def get_sales_comparables_get(street, city, county, state, zip_code):
    """
    Get sales comparables for a specific address
    
    GET /salescomparables/address/{street}/{city}/{county}/{state}/{zip}
    """
    try:
        result = property_service.get_sales_comparables(street, city, county, state, zip_code)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Property Valuation REST API")
    print("📍 Available at: http://localhost:5001")
    print("📚 Documentation: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)