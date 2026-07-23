# avm_api - Property Valuation Service

A REST API service that provides property valuations and detailed property information using RentCast and RealtyAPI.io's real estate APIs.

## 🏠 Overview

This service combines RentCast's property records with RealtyAPI.io's aggregated valuation, listing, and tax history data to provide comprehensive property reports. It offers both machine-readable raw data and homeowner-friendly formatted responses.

- **RentCast** supplies the subject property's basic profile (beds/baths/sqft/lot/year built, owner, coordinates) via a single `/properties` call.
- **RealtyAPI.io** supplies valuation estimates, tax assessment history, listing/event history, sales comparables, and similar-property search, aggregated from the underlying listing platforms (Redfin, Realtor.com, Zillow, etc.).

## ✨ Features

- **Interactive D3.js Charts**: Professional property assessment visualizations
- **Comprehensive Analysis**: Basic + AVM + Timeline + Auto-Charts in one call
- **Assessment History**: 14+ years of property tax and valuation trends
- **Combined Reports**: AVM valuation with basic profile fallback
- **Multiple Report Types**: AVM-only, basic profile-only, or comprehensive
- **Batch Processing**: Handle up to 10 addresses simultaneously  
- **Developer Library**: JavaScript library for easy chart embedding
- **Auto-Browser Launch**: Seamless chart opening with URL parameters
- **Raw Data Access**: Full API responses for advanced use cases
- **REST API**: 17 HTTP endpoints with JSON responses

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- A [RentCast](https://developers.rentcast.io/) API key
- A [RealtyAPI.io](https://www.realtyapi.io/) API key
- Required packages: `requests`, `flask`, `flask-cors`, `python-dotenv`

### Installation

1. **Set up environment variables**:
   Create a `.env` file at `~/.vendi-ave/.env` (kept outside the repo so it's never
   at risk of being committed/pushed):
   ```bash
   mkdir -p ~/.vendi-ave
   echo "RENTCAST_API_KEY=your_rentcast_key_here" > ~/.vendi-ave/.env
   echo "REALTYAPI_KEY=your_realtyapi_key_here" >> ~/.vendi-ave/.env
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the API server**:
   ```bash
   python property_rest_api.py
   ```

The API will be available at: `http://localhost:5001`

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:5001/health
```

### Property Reports

#### Combined Report (Recommended)
Gets AVM data if available, falls back to basic profile:
```bash
curl -X POST http://localhost:5001/property/combined \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Boston, MA 02101"}'
```

#### AVM Report Only
```bash
curl -X POST http://localhost:5001/property/avm \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Boston, MA 02101"}'
```

#### Basic Profile Only
```bash
curl -X POST http://localhost:5001/property/basic \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Boston, MA 02101"}'
```

#### Batch Processing
Process up to 10 addresses at once:
```bash
curl -X POST http://localhost:5001/property/batch \
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
  "confidence_score": "2 valuation source(s)",
  "value_source": "Quantarium",
  "property_size": "3,054 sqft",
  "year_built": "1994",
  "bedrooms": "3",
  "bathrooms": "3",
  "lot_size": "0.25 acres",
  "last_sale_price": "$370,000",
  "last_sale_date": "2000-05-15",
  "current_assessment": "$1,200,000",
  "list_price": "$1,399,000",
  "listing_status": "off_market",
  "data_retrieved": "2024-08-25 15:30:00"
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
├── property_api_service.py    # Core service logic
├── property_rest_api.py       # Flask REST API wrapper
├── requirements.txt          # Python dependencies
├── API_USAGE_GUIDE.md        # Detailed usage examples
└── README.md                 # This file
```

API keys live in `~/.vendi-ave/.env`, outside this repo entirely (see Installation above).

## 🛠️ Development

### Running Interactively
```bash
python property_api_service.py
```

This starts an interactive command-line interface for testing the service directly.

### Available Methods
- `get_combined_report(address)` - Combined AVM + basic profile
- `get_property_report(address)` - AVM report only
- `get_basic_profile_report(address)` - Basic profile only
- `get_avm_history(address)` - Raw AVM data
- `get_basic_profile(address)` - Raw basic profile data

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

## 📊 Interactive Charts

Access professional D3.js visualizations at `http://localhost:5001/charts`

Features:
- 14+ years of assessment history trends
- Interactive tooltips and responsive design
- Auto-population with address parameters
- Developer JavaScript library available

## 🔗 Dependencies

- **RentCast API**: Property records data provider
- **RealtyAPI.io**: Valuation, tax history, and listing data provider
- **Flask**: Web framework for REST API
- **Flask-CORS**: Cross-origin resource sharing
- **requests**: HTTP client library
- **python-dotenv**: Environment variable management

## 📄 License

This project integrates with RentCast's and RealtyAPI.io's commercial APIs. Ensure you have appropriate licensing and API access before use.