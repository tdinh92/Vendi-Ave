# API Endpoints for Designers & Developers

## 🚀 Base URL
```
http://localhost:5001
```

## 📊 Endpoints for Value Range Visualization

### 1. Get AVM Data (Raw) - **RECOMMENDED FOR VALUE RANGE**
Get valuation estimate(s) sourced from RealtyAPI.io (which aggregates AVM data from
providers like Quantarium and Collateral Analytics via the underlying listing platforms).

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
  "success": true,
  "data": {
    "address": { "line": "4 Fiorenza Dr", "city": "Wilmington", "state_code": "MA", "postal_code": "01887" },
    "list_price": 399000,
    "last_sold_price": 370000,
    "last_sold_date": "2000-04-28",
    "status": "off_market",
    "details": { "beds": 3, "baths": "2.5", "sqft": 2766, "year_built": 1994 },
    "estimates": {
      "current_values": [
        { "source": { "type": "quantarium", "name": "Quantarium" }, "estimate": 1223596, "isbest_homevalue": true },
        { "source": { "type": "collateral", "name": "Collateral Analytics" }, "estimate": 1181000, "isbest_homevalue": false }
      ]
    }
  },
  "estimates": [
    { "source": { "type": "quantarium", "name": "Quantarium" }, "estimate": 1223596, "isbest_homevalue": true },
    { "source": { "type": "collateral", "name": "Collateral Analytics" }, "estimate": 1181000, "isbest_homevalue": false }
  ]
}
```

There's no single confidence score or fixed high/low range field — instead you get a
list of estimates from different sources. Use `Math.min`/`Math.max` across `estimates`
to build a value range, and pick the one with `isbest_homevalue: true` as the headline number.

**JavaScript Example:**
```javascript
async function getValueRangeData(address) {
  const response = await fetch('http://localhost:5001/property/raw/avm', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ address: address })
  });

  const result = await response.json();
  const estimates = result.estimates || [];
  const values = estimates.map(e => e.estimate).filter(Boolean);
  const best = estimates.find(e => e.isbest_homevalue) || estimates[0];

  return {
    avmValue: best?.estimate,
    lowValue: Math.min(...values),
    highValue: Math.max(...values),
    sourceCount: estimates.length
  };
}

// Usage:
getValueRangeData('4 Fiorenza Drive, Wilmington, MA 01887')
  .then(data => {
    console.log('AVM Value:', data.avmValue);
    console.log('Range:', data.lowValue, '-', data.highValue);
    console.log('Sources:', data.sourceCount);
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

#### 9. Similar Properties (Estimated Value + Listing Data)
```
POST /property/similar
Body: {
  "street": "4 Fiorenza Drive",
  "city": "Wilmington",
  "county": "",
  "state": "MA",
  "zip_code": "01887",
  "sqft_tolerance": 10.0,
  "radius_miles": 5.0
}
```
Note: this endpoint takes address **components**, not a single `address` string (unlike
most other endpoints). Returns up to 15 nearby properties matching bedrooms/bathrooms
exactly and square footage within `±sqft_tolerance`, sourced from RealtyAPI.io.

**Response Example:**
```json
{
  "subject_property": {
    "address": "4 Fiorenza Drive, Wilmington, MA 01887",
    "bedrooms": 3,
    "bathrooms": 2.5,
    "sqft": 3054
  },
  "filters_applied": {
    "bedrooms": 3,
    "bathrooms": 2.5,
    "sqft_range": "2,748 - 3,359",
    "sqft_tolerance": "±10.0%",
    "radius_miles": 5.0
  },
  "total_comparables": 1,
  "comparables": [
    {
      "address": "32 River Rd, Andover, MA 01810",
      "distance_miles": 6.4,
      "bedrooms": 3,
      "bathrooms": "2.5",
      "building_size_sqft": 2395,
      "listing_status": "for_sale",
      "estimated_value": "$727,900",
      "raw_estimated_value": 727900,
      "estimated_value_per_sqft": "$303.92",
      "list_price": "$539,900",
      "last_sale_price": "N/A",
      "last_sale_date": null,
      "property_id": "4166998128"
    }
  ]
}
```

Note there's no `assessed_value` or `confidence_score` per property anymore, and the
array key is `comparables` (not `similar_properties`) with `total_comparables`
(not `total_properties`) — update any UI code that reads the old field names.

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

### Raw Data Endpoints (Unformatted RentCast / RealtyAPI.io Responses)

#### Raw AVM Data
```
POST /property/raw/avm
Body: {"address": "123 Main St, Boston, MA 02101"}
```
Returns raw RealtyAPI.io listing/valuation response (use this for value range slider).

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
    const response = await fetch('http://localhost:5001/property/raw/avm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address: address })
    });

    const result = await response.json();
    const estimates = result.estimates || [];
    const values = estimates.map(e => e.estimate).filter(Boolean);
    const best = estimates.find(e => e.isbest_homevalue) || estimates[0];
    const low = Math.min(...values);
    const high = Math.max(...values);

    // Update your UI elements
    document.getElementById('mostLikelyValue').textContent =
      `$${best.estimate.toLocaleString()}`;
    document.getElementById('lowValue').textContent =
      `$${low.toLocaleString()}`;
    document.getElementById('highValue').textContent =
      `$${high.toLocaleString()}`;

    // Calculate marker position (0-100%)
    const range = high - low;
    const position = ((best.estimate - low) / range) * 100;
    document.getElementById('rangeMarker').style.left = position + '%';

    // Update metrics (no FSD from this provider - show source count instead)
    document.getElementById('sourceCount').textContent = `${estimates.length} sources`;
    document.getElementById('valueRange').textContent =
      `$${range.toLocaleString()}`;

  } catch (error) {
    console.error('Error fetching AVM data:', error);
  }
}

// Usage
updateValueRangeSlider('4 Fiorenza Drive, Wilmington, MA 01887');
```

### Example 2: Fetch Similar Properties for Comparison

```javascript
async function getSimilarProperties(street, city, state, zip_code) {
  const response = await fetch('http://localhost:5001/property/similar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ street, city, county: '', state, zip_code })
  });

  const data = await response.json();

  // Display similar properties in your UI
  (data.comparables || []).forEach(property => {
    console.log(`${property.address}: ${property.estimated_value}`);
    console.log(`  Status: ${property.listing_status}`);
    console.log(`  Distance: ${property.distance_miles} miles`);
  });

  return data;
}
```

### Example 3: Load Assessment History for Charts

```javascript
async function loadAssessmentCharts(address) {
  const response = await fetch('http://localhost:5001/property/assessmenthistory', {
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
# http://localhost:5001
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
- Returns: a list of valuation `estimates` (source name + value) - derive low/high/best yourself
- Perfect for the gradient slider visualization

### For Property Comparison:
✅ **`POST /property/similar`**
- Returns: up to 15 similar properties with estimated value + listing status
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
curl -X POST http://localhost:5001/property/raw/avm \
  -H "Content-Type: application/json" \
  -d '{"address": "4 Fiorenza Drive, Wilmington, MA 01887"}'

# Test similar properties
curl -X POST http://localhost:5001/property/similar \
  -H "Content-Type: application/json" \
  -d '{"address": "4 Fiorenza Drive, Wilmington, MA 01887"}'
```

### Using Postman:
1. Create new POST request
2. URL: `http://localhost:5001/property/raw/avm`
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
http://localhost:5001/health
http://localhost:5001/charts
http://localhost:5001/static/value-range-slider.html
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
- Check if `~/.vendi-ave/.env` exists with `RENTCAST_API_KEY` and `REALTYAPI_KEY`
- Verify Python dependencies: `pip install -r requirements.txt`

**CORS errors?**
- CORS is enabled by default
- Check browser console for specific error messages

**No data returned?**
- Verify address format is correct
- Check both API keys are valid
- Property may not exist in RentCast/RealtyAPI.io's coverage

**Server running on different port?**
- Default is 5001
- Check console output when starting server
- Update base URL accordingly

---

**✅ All endpoints are live and ready for your designer to use!**

**Server Status:** Run `python property_rest_api.py` to start
**Base URL:** `http://localhost:5001`
**CORS:** Enabled for all origins
**Response Format:** JSON
