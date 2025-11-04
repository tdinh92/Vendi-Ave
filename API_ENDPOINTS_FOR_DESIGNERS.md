# API Endpoints for Designers & Developers

## 🚀 Base URL
```
http://localhost:5000
```

## 📊 Endpoints for Value Range Visualization

### 1. Get AVM Data (Raw) - **RECOMMENDED FOR VALUE RANGE**
Get AVM market estimate with confidence score and value range.

**Endpoint:** `POST /property/raw/avm`

**Request:**
```json
{
  "address": "4 Fiorenza Drive, Wilmington, MA 01887"
}
```

**Response (contains value range data):**
```json
{
  "property": [
    {
      "avm": {
        "amount": {
          "value": {
            "value": 1327564,          // AVM Market Value
            "valueLow": 1261185,       // Low Estimate
            "valueHigh": 1393942,      // High Estimate
            "confidence": 95,          // Confidence Score (0-100)
            "fsd": 5.0                 // Forecast Standard Deviation
          }
        },
        "eventDate": "2025-09-22"      // Valuation Date
      }
    }
  ]
}
```

**JavaScript Example:**
```javascript
async function getValueRangeData(address) {
  const response = await fetch('http://localhost:5000/property/raw/avm', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ address: address })
  });

  const data = await response.json();
  const avm = data.property[0].avm.amount.value;

  return {
    avmValue: avm.value,
    lowValue: avm.valueLow,
    highValue: avm.valueHigh,
    confidence: avm.confidence,
    fsd: avm.fsd
  };
}

// Usage:
getValueRangeData('4 Fiorenza Drive, Wilmington, MA 01887')
  .then(data => {
    console.log('AVM Value:', data.avmValue);
    console.log('Range:', data.lowValue, '-', data.highValue);
    console.log('Confidence:', data.confidence);
  });
```

---

## 📋 All Available Endpoints

### Core Endpoints

#### Health Check
```
GET /health
```
Returns API status.

#### Home / Documentation
```
GET /
```
Returns API documentation.

---

### Property Reports (Clean/Formatted)

#### 1. Combined Report (AVM + Basic Profile)
```
POST /property/combined
Body: {"address": "123 Main St, Boston, MA 02101"}
```
Returns AVM data with basic profile fallback.

#### 2. AVM Report Only
```
POST /property/avm
Body: {"address": "123 Main St, Boston, MA 02101"}
```
Returns formatted AVM report.

#### 3. Basic Profile Report
```
POST /property/basic
Body: {"address": "123 Main St, Boston, MA 02101"}
```
Returns basic property information.

#### 4. Complete Report (AVM + Basic Profile)
```
POST /property/complete
Body: {"address": "123 Main St, Boston, MA 02101"}
```
Returns both AVM and basic profile data.

#### 5. Comprehensive Analysis
```
POST /property/comprehensive
Body: {"address": "123 Main St, Boston, MA 02101"}
```
Returns ultimate analysis with all data sources + opens charts in browser.

#### 6. All Events Snapshot
```
POST /property/allevents
Body: {"address": "123 Main St, Boston, MA 02101"}
```
Returns property event timeline (sales, refinances, etc.).

#### 7. Assessment History (For Charts)
```
POST /property/assessmenthistory
Body: {"address": "123 Main St, Boston, MA 02101"}
```
Returns 14+ years of assessment history **formatted for D3.js charts**.

**Response Example:**
```json
{
  "address": "4 FIORENZA DR, WILMINGTON, MA 01887",
  "total_assessments": 14,
  "assessment_years": ["2025", "2024", "2023", "..."],
  "assessments": [
    {
      "tax_year": "2025",
      "total_assessed_value": "$1,131,800",
      "tax_amount": "$12,959.0",
      "assessed_per_sqft": "$370.60",
      "raw_total_assessed": 1131800,
      "raw_tax_amount": 12959.0,
      "raw_assessed_per_sqft": 370.60
    }
  ]
}
```

#### 8. Sales Comparables
```
POST /property/salescomparables
Body: {
  "street": "4 Fiorenza Drive",
  "city": "Wilmington",
  "county": "",
  "state": "MA",
  "zip_code": "01887"
}
```
Returns recently sold comparable properties with smart filtering.

#### 9. Similar Properties (AVM + Assessment Data)
```
POST /property/similar
Body: {"address": "4 Fiorenza Drive, Wilmington, MA 01887"}
```
Returns 15 similar properties with BOTH AVM market estimates AND tax assessed values.

**Response Example:**
```json
{
  "subject_property": {
    "address": "4 FIORENZA DR, WILMINGTON, MA 01887",
    "bedrooms": 3,
    "bathrooms": 3.0,
    "sqft": 3053
  },
  "filters_applied": {
    "bedrooms": 3,
    "bathrooms": 3.0,
    "sqft_min": 2748,
    "sqft_max": 3358
  },
  "total_properties": 15,
  "similar_properties": [
    {
      "address": "123 Main St, Wilmington, MA 01887",
      "distance_miles": 0.8,
      "avm_value": "$1,250,000",
      "avm_value_per_sqft": "$425.50",
      "assessed_value": "$1,100,000",
      "assessed_value_per_sqft": "$374.15",
      "confidence_score": 92,
      "value_range_high": "$1,312,500",
      "value_range_low": "$1,187,500",
      "bedrooms": 3,
      "bathrooms": 3.0,
      "sqft": 2938,
      "year_built": 2005
    }
  ]
}
```

#### 10. Batch Processing (Up to 10 Addresses)
```
POST /property/batch
Body: {
  "addresses": [
    "123 Main St, Boston, MA 02101",
    "456 Oak Ave, Cambridge, MA 02138"
  ]
}
```

---

### Raw Data Endpoints (Unformatted Attom API Responses)

#### Raw AVM Data
```
POST /property/raw/avm
Body: {"address": "123 Main St, Boston, MA 02101"}
```
Returns raw Attom AVM API response (use this for value range slider).

#### Raw Basic Profile Data
```
POST /property/raw/basic
Body: {"address": "123 Main St, Boston, MA 02101"}
```

#### Raw All Events Data
```
POST /property/raw/allevents
Body: {"address": "123 Main St, Boston, MA 02101"}
```

#### Raw Assessment History Data
```
POST /property/raw/assessmenthistory
Body: {"address": "123 Main St, Boston, MA 02101"}
```

---

### Visualization Endpoints

#### Interactive Charts Interface
```
GET /charts
```
Opens D3.js charts interface in browser.

**With Query Parameter:**
```
GET /charts?address=4%20Fiorenza%20Drive,%20Wilmington,%20MA%2001887
```

#### Static Files (JS Library, SVGs, etc.)
```
GET /static/<filename>
```

Examples:
- `GET /static/assessment-charts.js` - D3.js charts library
- `GET /static/value-range-slider.html` - Interactive value range demo
- `GET /static/value-range-slider-exact.svg` - SVG for Figma
- `GET /static/avm-confidence-dashboard.html` - Full AVM dashboard

---

## 🎨 Integration Examples for Designers

### Example 1: Update Value Range Slider with Live Data

```javascript
// Fetch AVM data and update the visualization
async function updateValueRangeSlider(address) {
  try {
    const response = await fetch('http://localhost:5000/property/raw/avm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address: address })
    });

    const data = await response.json();
    const avm = data.property[0].avm.amount.value;

    // Update your UI elements
    document.getElementById('mostLikelyValue').textContent =
      `$${avm.value.toLocaleString()}`;
    document.getElementById('lowValue').textContent =
      `$${avm.valueLow.toLocaleString()}`;
    document.getElementById('highValue').textContent =
      `$${avm.valueHigh.toLocaleString()}`;

    // Calculate marker position (0-100%)
    const range = avm.valueHigh - avm.valueLow;
    const position = ((avm.value - avm.valueLow) / range) * 100;
    document.getElementById('rangeMarker').style.left = position + '%';

    // Update metrics
    document.getElementById('fsdValue').textContent = avm.fsd.toFixed(1) + '%';
    const valueRange = avm.valueHigh - avm.valueLow;
    document.getElementById('valueRange').textContent =
      `$${valueRange.toLocaleString()}`;

  } catch (error) {
    console.error('Error fetching AVM data:', error);
  }
}

// Usage
updateValueRangeSlider('4 Fiorenza Drive, Wilmington, MA 01887');
```

### Example 2: Fetch Similar Properties for Comparison

```javascript
async function getSimilarProperties(address) {
  const response = await fetch('http://localhost:5000/property/similar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address: address })
  });

  const data = await response.json();

  // Display similar properties in your UI
  data.similar_properties.forEach(property => {
    console.log(`${property.address}: ${property.avm_value}`);
    console.log(`  Confidence: ${property.confidence_score}`);
    console.log(`  Distance: ${property.distance_miles} miles`);
  });

  return data;
}
```

### Example 3: Load Assessment History for Charts

```javascript
async function loadAssessmentCharts(address) {
  const response = await fetch('http://localhost:5000/property/assessmenthistory', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address: address })
  });

  const data = await response.json();

  // Data is ready for D3.js charts
  // Each assessment has both formatted strings and raw numbers
  data.assessments.forEach(assessment => {
    console.log(`${assessment.tax_year}: ${assessment.total_assessed_value}`);
  });

  return data;
}
```

---

## 🔐 CORS Configuration

CORS is **enabled** for all routes, so you can call these endpoints from:
- Any localhost port
- Any domain (development mode)
- Browser-based applications
- Frontend frameworks (React, Vue, Angular, etc.)

---

## 🚦 Starting the API Server

```bash
# Navigate to project directory
cd c:\Users\thoma\OneDrive\Documents\GitHub\Vendi-Ave

# Start the Flask server
python property_rest_api.py

# Server runs on:
# http://localhost:5000
```

---

## 📊 Response Format

All endpoints return JSON responses with consistent error handling:

**Success Response:**
```json
{
  "data": { ... },
  "status": "success"
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "details": "Additional details"
}
```

---

## 🎯 Recommended Endpoints for UI/UX Design

### For Value Range Slider:
✅ **`POST /property/raw/avm`**
- Returns: AVM value, low, high, confidence, FSD
- Perfect for the gradient slider visualization

### For Property Comparison:
✅ **`POST /property/similar`**
- Returns: 15 similar properties with AVM + assessed values
- Great for comparison tables/lists

### For Historical Trends:
✅ **`POST /property/assessmenthistory`**
- Returns: 14+ years of assessment data
- Pre-formatted for D3.js charts

### For Complete Property Info:
✅ **`POST /property/comprehensive`**
- Returns: Everything (AVM + Basic + Timeline + Charts)
- One endpoint to get it all

---

## 🧪 Testing Endpoints

### Using cURL:

```bash
# Test AVM endpoint
curl -X POST http://localhost:5000/property/raw/avm \
  -H "Content-Type: application/json" \
  -d '{"address": "4 Fiorenza Drive, Wilmington, MA 01887"}'

# Test similar properties
curl -X POST http://localhost:5000/property/similar \
  -H "Content-Type: application/json" \
  -d '{"address": "4 Fiorenza Drive, Wilmington, MA 01887"}'
```

### Using Postman:
1. Create new POST request
2. URL: `http://localhost:5000/property/raw/avm`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "address": "4 Fiorenza Drive, Wilmington, MA 01887"
   }
   ```
5. Send request

### Using Browser (for GET endpoints):
```
http://localhost:5000/health
http://localhost:5000/charts
http://localhost:5000/static/value-range-slider.html
```

---

## 📚 Additional Resources

- **Main Documentation**: See `README.md`
- **Development Log**: See `CLAUDE.md`
- **Figma Export Guide**: See `FIGMA_EXPORT_GUIDE.md`
- **Charts Integration**: See `CHARTS_INTEGRATION_GUIDE.md`

---

## 🆘 Troubleshooting

**API not starting?**
- Check if `.env` file exists with `ATTOM_API_KEY`
- Verify Python dependencies: `pip install -r requirements.txt`

**CORS errors?**
- CORS is enabled by default
- Check browser console for specific error messages

**No data returned?**
- Verify address format is correct
- Check API key is valid
- Ensure property exists in Attom database

**Server running on different port?**
- Default is 5000
- Check console output when starting server
- Update base URL accordingly

---

**✅ All endpoints are live and ready for your designer to use!**

**Server Status:** Run `python property_rest_api.py` to start
**Base URL:** `http://localhost:5000`
**CORS:** Enabled for all origins
**Response Format:** JSON
