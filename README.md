# avm_api - Property Valuation Service

A REST API service that provides property valuations and detailed property information using Attom Data's real estate APIs.

## 🏠 Overview

This service combines Attom Data's AVM (Automated Valuation Model) and Basic Property Profile APIs to provide comprehensive property reports. It offers both machine-readable raw data and homeowner-friendly formatted responses.

## ✨ Features

- **Professional Sales Comparables**: Smart filtering by property type and price range (±30%)
- **Interactive D3.js Charts**: Professional property assessment visualizations
- **Comprehensive Analysis**: Basic + AVM + Timeline + Auto-Charts in one call
- **Assessment History**: 14+ years of property tax and valuation trends
- **Combined Reports**: AVM valuation with basic profile fallback
- **Multiple Report Types**: AVM-only, basic profile-only, or comprehensive
- **Batch Processing**: Handle up to 10 addresses simultaneously  
- **Developer Library**: JavaScript library for easy chart embedding
- **Auto-Browser Launch**: Seamless chart opening with URL parameters
- **Raw Data Access**: Full API responses for advanced use cases
- **Enhanced Security**: Input validation, secure logging, and financial data validation
- **REST API**: 20+ HTTP endpoints with JSON responses

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Attom Data API key
- Required packages: `requests`, `flask`, `flask-cors`, `python-dotenv`

### Installation

1. **Set up environment variables**:
   Create a `.env` file in the `AVM_Api/` directory:
   ```bash
   cd AVM_Api
   echo "ATTOM_API_KEY=your_api_key_here" > .env
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the API server**:
   ```bash
   cd AVM_Api
   python property_rest_api.py
   ```

The API will be available at: `http://localhost:5000`

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

### Property Reports

#### Combined Report (Recommended)
Gets AVM data if available, falls back to basic profile:
```bash
curl -X POST http://localhost:5000/property/combined \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Boston, MA 02101"}'
```

#### AVM Report Only
```bash
curl -X POST http://localhost:5000/property/avm \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Boston, MA 02101"}'
```

#### Basic Profile Only
```bash
curl -X POST http://localhost:5000/property/basic \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Boston, MA 02101"}'
```

#### Sales Comparables
Get intelligent sales comparables filtered by property type and price range:
```bash
# Get property ID first
curl -X POST http://localhost:5000/property/propid \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Boston, MA 02101"}'

# Get filtered sales comparables
curl -X GET http://localhost:5000/salescomparables/propid/{propertyId}

# Get raw sales comparables data
curl -X GET http://localhost:5000/salescomparables/propid/{propertyId}/raw
```

#### Comprehensive Analysis
Ultimate analysis combining AVM, basic profile, assessment history, and auto-charts:
```bash
curl -X POST http://localhost:5000/property/comprehensive \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Boston, MA 02101"}'
```

#### Batch Processing
Process up to 10 addresses at once:
```bash
curl -X POST http://localhost:5000/property/batch \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "123 Main St, Boston, MA 02101",
      "456 Oak Ave, Springfield, IL 62701"
    ],
    "report_type": "combined"
  }'
```

## 📊 Response Format

### Successful AVM Response
```json
{
  "address": "123 MAIN ST, BOSTON, MA 02101",
  "current_estimated_value": "$1,445,419",
  "value_range_low": "$1,373,148", 
  "value_range_high": "$1,517,689",
  "confidence_score": "95/100",
  "estimate_date": "2024-08-25",
  "property_size": "3,054 sqft",
  "year_built": "1994",
  "bedrooms": "3",
  "bathrooms": "3",
  "lot_size": "0.25 acres",
  "last_sale_price": "$370,000",
  "last_sale_date": "2000-05-15",
  "current_assessment": "$1,200,000",
  "owner": "John Smith",
  "data_retrieved": "2024-08-25 15:30:00"
}
```

### Sales Comparables Response
```json
{
  "total_comparables": 31,
  "average_sale_price": "$1,190,867",
  "search_radius": "5 miles",
  "date": "2025-01-15",
  "comparables": [
    {
      "address": "376 SALEM ST ANDOVER, MA 01810",
      "city": "ANDOVER",
      "state": "MA",
      "zip": "01810",
      "sale_price": "$1,425,000",
      "sale_date": "2022-05-15",
      "square_feet": 2800,
      "bedrooms": 4,
      "bathrooms": 3,
      "lot_size": 0.45,
      "year_built": 1995,
      "price_per_sqft": "$508.93",
      "property_type": "Single Family Residence / Townhouse"
    }
  ]
}
```

### Basic Profile Fallback
```json
{
  "address": "208 ASHMONT ST, DORCHESTER CENTER, MA 02124",
  "property_size": "N/A",
  "year_built": "N/A", 
  "bedrooms": "N/A",
  "bathrooms": "N/A",
  "lot_size": "N/A",
  "property_type": "N/A",
  "property_subtype": "N/A",
  "last_sale_price": "N/A",
  "last_sale_date": "N/A",
  "current_assessment": "N/A",
  "owner": "N/A",
  "valuation_note": "No current market valuation available - showing basic property data only",
  "data_retrieved": "2024-08-25 15:30:00"
}
```

## 🗂️ File Structure

```
AVM_Api/
├── property_api_service.py       # Core service logic with CLI interface
├── property_rest_api_secure.py   # Secure Flask REST API wrapper
├── property_rest_api.py          # Original Flask REST API wrapper  
├── requirements.txt              # Python dependencies
├── requirements_secure.txt       # Secure dependencies
├── .env                          # Environment variables (API key)
├── CLAUDE.md                     # Development log and documentation
├── static/
│   └── assessment-charts.js      # JavaScript library for charts
├── templates/
│   └── assessment_charts.html    # Interactive chart interface
└── README.md                     # This file
```

## 🛠️ Development

### Running Interactively
```bash
python property_api_service.py
```

This starts an interactive command-line interface with 8 options:
1. Combined report (AVM + Basic Profile fallback)
2. AVM report only  
3. Basic profile only
4. Complete report (both AVM and Basic Profile)
5. Comprehensive analysis (Basic + AVM + Timeline + Charts)
6. All events snapshot (comprehensive timeline)
7. Assessment history (charts data)
8. **Sales comparables (within 5-mile radius)** - NEW!

### Available Methods
- `get_combined_report(address)` - Combined AVM + basic profile
- `get_property_report(address)` - AVM report only
- `get_basic_profile_report(address)` - Basic profile only
- `get_comprehensive_analysis(address)` - Ultimate analysis with auto-charts
- `get_sales_comparables_by_propid(prop_id, address)` - Smart filtered comparables
- `get_assessment_history_report(address)` - Assessment history for charts

## 🔒 Production Considerations

### Security
- Use HTTPS in production
- Implement API key authentication
- Add rate limiting
- Enable request logging

### Performance
- Cache successful responses (24 hours recommended)
- Implement connection pooling
- Add request timeouts
- Monitor API quota usage

### Error Handling
- Always check for "error" field in responses
- Implement retry logic for 5xx errors
- Handle network timeouts gracefully
- Log errors for debugging

## 📚 Documentation

## 🏘️ Professional Sales Comparables

Advanced sales comparables with intelligent filtering:

### Smart Filtering Features:
- **Property Type Matching**: Only shows same property types (SFR-to-SFR, Condo-to-Condo, etc.)
- **Price Range Filtering**: ±30% of subject property's AVM value
- **Valid Sales Only**: Excludes foreclosures, family transfers, and invalid data
- **Geographic Proximity**: Within 5-mile radius

### Comprehensive Property Details:
- Square footage, bedrooms, bathrooms
- Lot size, year built, property type
- Price per square foot calculations
- Sale date and distance from subject
- Complete address information

### Example Output:
```
📊 Total Found: 31 comparable sales
💰 Average Sale Price: $1,190,867
📍 Search Radius: 5 miles
🎯 Price Range: ±30% of property AVM value

🏘️ COMPARABLE SALES (PRICE FILTERED):
 1. 376 SALEM ST ANDOVER, MA 01810
    📍 ANDOVER, MA 01810
    💰 $1,425,000 (2022-05-15)
    🏠 2,800 sqft, 4 bed, 3 bath
    📊 0.45 acres, Built 1995, $508.93/sqft, Single Family Residence / Townhouse
```

## 📊 Interactive Charts

Access professional D3.js visualizations at `http://localhost:5000/charts`

Features:
- 14+ years of assessment history trends
- Interactive tooltips and responsive design
- Auto-population with address parameters
- Developer JavaScript library available

## 🔗 Dependencies

- **Attom Data API**: Real estate data provider
- **Flask**: Web framework for REST API
- **Flask-CORS**: Cross-origin resource sharing
- **requests**: HTTP client library
- **python-dotenv**: Environment variable management

## 📄 License

This project integrates with Attom Data's commercial APIs. Ensure you have appropriate licensing and API access before use.