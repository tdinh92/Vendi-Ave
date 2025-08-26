# Property Valuation REST API - Usage Guide

## 🚀 Quick Start

### 1. Start the API Server
```bash
cd api
python3 property_rest_api.py
```
The API will be available at: `http://localhost:5000`

### 2. Get API Documentation
```bash
curl http://localhost:5000/
```

## 📡 API Endpoints

### Health Check
```bash
# Check if the API is running
curl http://localhost:5000/health
```

### Single Property Reports

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

### Batch Processing
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

### Raw Data Access
For debugging or advanced use:
```bash
# Raw AVM data
curl -X POST http://localhost:5000/property/raw/avm \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Boston, MA 02101"}'

# Raw basic profile data
curl -X POST http://localhost:5000/property/raw/basic \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Boston, MA 02101"}'
```

## 💻 Programming Language Examples

### JavaScript/Node.js
```javascript
// Single property report
async function getPropertyValue(address) {
  const response = await fetch('http://localhost:5000/property/combined', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address: address })
  });
  
  const data = await response.json();
  return data;
}

// Usage
getPropertyValue('123 Main St, Boston, MA 02101')
  .then(data => console.log(data));

// Batch processing
async function batchPropertyValues(addresses) {
  const response = await fetch('http://localhost:5000/property/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      addresses: addresses,
      report_type: 'combined'
    })
  });
  
  return await response.json();
}
```

### Python
```python
import requests

# Single property report
def get_property_value(address):
    url = 'http://localhost:5000/property/combined'
    payload = {'address': address}
    response = requests.post(url, json=payload)
    return response.json()

# Usage
result = get_property_value('123 Main St, Boston, MA 02101')
print(result)

# Batch processing
def batch_property_values(addresses):
    url = 'http://localhost:5000/property/batch'
    payload = {
        'addresses': addresses,
        'report_type': 'combined'
    }
    response = requests.post(url, json=payload)
    return response.json()

# Usage
addresses = ['123 Main St, Boston, MA 02101', '456 Oak Ave, Springfield, IL 62701']
results = batch_property_values(addresses)
print(results)
```

### PHP
```php
<?php
// Single property report
function getPropertyValue($address) {
    $url = 'http://localhost:5000/property/combined';
    $data = array('address' => $address);
    
    $options = array(
        'http' => array(
            'header'  => "Content-type: application/json\r\n",
            'method'  => 'POST',
            'content' => json_encode($data)
        )
    );
    
    $context  = stream_context_create($options);
    $result = file_get_contents($url, false, $context);
    return json_decode($result, true);
}

// Usage
$result = getPropertyValue('123 Main St, Boston, MA 02101');
print_r($result);
?>
```

### React.js Frontend
```jsx
import React, { useState } from 'react';

function PropertyLookup() {
  const [address, setAddress] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/property/combined', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="123 Main St, Boston, MA 02101"
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Loading...' : 'Get Property Value'}
        </button>
      </form>
      
      {result && (
        <div>
          <h3>Property Report</h3>
          <p>Address: {result.address}</p>
          {result.current_estimated_value && (
            <p>Value: {result.current_estimated_value}</p>
          )}
          <p>Size: {result.property_size}</p>
          <p>Year Built: {result.year_built}</p>
        </div>
      )}
    </div>
  );
}
```

## 📊 Response Formats

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

### Basic Profile Fallback Response
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

### Error Response
```json
{
  "error": "Address is required",
  "example": {
    "address": "123 Main St, Boston, MA 02101"
  }
}
```

### Batch Response
```json
{
  "report_type": "combined",
  "total_addresses": 2,
  "results": [
    {
      "address": "123 MAIN ST, BOSTON, MA 02101",
      "current_estimated_value": "$1,445,419",
      // ... full property data
    },
    {
      "address": "456 OAK AVE, SPRINGFIELD, IL 62701",
      "error": "Property not found"
    }
  ]
}
```

## ⚙️ Integration Patterns

### Web Application
1. **Frontend Form** → **REST API** → **Display Results**
2. Use combined endpoint for best coverage
3. Handle both successful and error responses
4. Show loading states during API calls

### Mobile App
1. **HTTP Client** → **REST API** → **Parse JSON**
2. Cache results locally to reduce API calls
3. Use batch processing for multiple properties

### Data Pipeline
1. **CSV/Database** → **Batch API** → **Process Results** → **Store/Export**
2. Process up to 10 addresses per API call
3. Implement retry logic for failed requests

### Real Estate Website
1. **Property Search** → **API Integration** → **Display Valuations**
2. Integrate with property listing pages
3. Show confidence scores and data freshness

## 🔒 Production Considerations

### Rate Limiting
- Current: 10 addresses per batch request
- Consider implementing API keys for higher limits

### Caching
- Cache successful responses for 24 hours
- Reduce API costs and improve performance

### Error Handling
- Always check for "error" field in responses
- Implement retry logic for 5xx errors
- Handle network timeouts gracefully

### Security
- Use HTTPS in production
- Implement API key authentication
- Add request logging and monitoring

## 📞 Support

For issues or questions:
1. Check the health endpoint: `GET /health`
2. Review error messages in API responses
3. Validate address format: "Street, City, State ZIP"
4. Use batch processing for multiple addresses