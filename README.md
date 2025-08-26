# avm_api - Property Valuation Service

A REST API service that provides property valuations and detailed property information using Attom Data's real estate APIs.

## 🏠 Overview

This service combines Attom Data's AVM (Automated Valuation Model) and Basic Property Profile APIs to provide comprehensive property reports. It offers both machine-readable raw data and homeowner-friendly formatted responses.

## ✨ Features

- **Combined Reports**: AVM valuation with basic profile fallback
- **Multiple Report Types**: AVM-only, basic profile-only, or combined
- **Batch Processing**: Handle up to 10 addresses simultaneously  
- **Homeowner-Friendly**: Clean, readable output format
- **Raw Data Access**: Full API responses for advanced use cases
- **REST API**: Standard HTTP endpoints with JSON responses

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
├── property_api_service.py    # Core service logic
├── property_rest_api.py       # Flask REST API wrapper  
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (API key)
├── API_USAGE_GUIDE.md        # Detailed usage examples
└── README.md                 # This file
```

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

For detailed usage examples and integration patterns, see [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md).

## 🔗 Dependencies

- **Attom Data API**: Real estate data provider
- **Flask**: Web framework for REST API
- **Flask-CORS**: Cross-origin resource sharing
- **requests**: HTTP client library
- **python-dotenv**: Environment variable management

## 📄 License

This project integrates with Attom Data's commercial APIs. Ensure you have appropriate licensing and API access before use.