# Property Assessment Charts Integration Guide

## 📊 Overview

Your AVM API now includes powerful D3.js-based visualization capabilities for property assessment history data. You can integrate interactive line charts showing:

1. **Total Assessed Value Over Time** - Property valuation trends
2. **Annual Property Tax Over Time** - Tax burden evolution  
3. **Assessed Value Per Square Foot** - Per-unit value trends

## 🚀 Quick Start

### Option 1: Full-Featured Web Interface

Visit the complete chart interface at:
```
http://localhost:5000/charts
```

This provides a ready-to-use web interface where users can:
- Enter any property address
- View all three interactive charts
- Hover for detailed tooltips
- See property information summary

### Option 2: JavaScript Library Integration

For developers who want to embed charts in their own applications:

#### Step 1: Include Dependencies

```html
<!-- Include D3.js -->
<script src="https://d3js.org/d3.v7.min.js"></script>

<!-- Include the Assessment Charts library -->
<script src="http://localhost:5000/static/assessment-charts.js"></script>
```

#### Step 2: Create Container

```html
<div id="my-charts-container"></div>
```

#### Step 3: Initialize and Load Charts

```javascript
// Initialize the charts library
const charts = new AssessmentCharts({
    apiBaseUrl: 'http://localhost:5000',  // Your API base URL
    containerId: 'my-charts-container',   // Container element ID
    width: 800,                          // Chart width (optional, default: 800)
    height: 400,                         // Chart height (optional, default: 400)
    colors: {                           // Custom colors (optional)
        assessment: '#2E8B57',          // Green for assessed value
        tax: '#DC143C',                 // Red for tax amount
        sqft: '#4169E1'                 // Blue for per sq ft
    }
});

// Load charts for a specific property
charts.loadCharts('4 Fiorenza Drive, Wilmington, MA 01887');
```

## 🔧 API Endpoints

Your Flask server now includes these new endpoints:

### Visualization Endpoints
- **`GET /charts`** - Complete web interface with charts
- **`GET /static/assessment-charts.js`** - JavaScript library for developers
- **`GET /static/demo.html`** - Interactive demo of the library

### Data Endpoints (Already Available)
- **`POST /property/assessmenthistory`** - Processed assessment history data
- **`POST /property/raw/assessmenthistory`** - Raw assessment data from Attom

## 📋 Complete API Endpoint List

```
GET  /health                           - Health check
GET  /                                 - API documentation  
GET  /charts                           - Interactive D3.js charts interface
GET  /static/<filename>                - Static files (JS library, demo)

POST /property/complete                - Complete report (AVM + Basic Profile)
POST /property/combined                - Combined report with fallback
POST /property/avm                     - AVM report only
POST /property/basic                   - Basic profile only
POST /property/allevents               - All events snapshot
POST /property/assessmenthistory       - Assessment history charts data
POST /property/batch                   - Batch processing (up to 10 addresses)

POST /property/raw/avm                 - Raw AVM data
POST /property/raw/basic               - Raw basic profile data  
POST /property/raw/allevents           - Raw all events data
POST /property/raw/assessmenthistory   - Raw assessment history data
```

## 🎨 Customization Options

### Library Configuration

```javascript
const charts = new AssessmentCharts({
    apiBaseUrl: 'http://your-api-server.com',
    containerId: 'charts-container',
    width: 1000,           // Custom width
    height: 500,           // Custom height
    margin: {              // Custom margins
        top: 30,
        right: 60,
        bottom: 80, 
        left: 100
    },
    colors: {              // Custom color scheme
        assessment: '#1f77b4',
        tax: '#ff7f0e', 
        sqft: '#2ca02c'
    }
});
```

### Styling

The charts automatically include responsive design and can be styled with CSS:

```css
.assessment-charts-wrapper {
    font-family: 'Your-Font', Arial, sans-serif;
}

.chart-container {
    border: 2px solid #your-color;
    border-radius: 10px;
}

.chart-title {
    color: #your-brand-color;
    font-size: 20px;
}
```

## 📊 Data Structure

The charts consume data from the `/property/assessmenthistory` endpoint:

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
      "raw_assessed_per_sqft": 370.60,
      "land_value": "$344,700",
      "improvement_value": "$787,100"
    }
  ]
}
```

## 🔄 Integration Examples

### React Component Example

```javascript
import React, { useEffect, useRef } from 'react';

const PropertyCharts = ({ address }) => {
    const chartRef = useRef();
    
    useEffect(() => {
        if (window.AssessmentCharts && address) {
            const charts = new window.AssessmentCharts({
                apiBaseUrl: 'http://localhost:5000',
                containerId: chartRef.current.id
            });
            charts.loadCharts(address);
        }
    }, [address]);
    
    return <div id="property-charts" ref={chartRef}></div>;
};
```

### Vue Component Example

```javascript
<template>
  <div id="property-charts" ref="chartsContainer"></div>
</template>

<script>
export default {
  props: ['address'],
  mounted() {
    this.initCharts();
  },
  methods: {
    initCharts() {
      const charts = new AssessmentCharts({
        apiBaseUrl: 'http://localhost:5000',
        containerId: 'property-charts'
      });
      if (this.address) {
        charts.loadCharts(this.address);
      }
    }
  },
  watch: {
    address(newAddress) {
      if (newAddress && this.charts) {
        this.charts.loadCharts(newAddress);
      }
    }
  }
}
</script>
```

### jQuery Example

```javascript
$(document).ready(function() {
    // Initialize charts
    const charts = new AssessmentCharts({
        apiBaseUrl: 'http://localhost:5000',
        containerId: 'charts-container'
    });
    
    // Load charts when address is entered
    $('#address-input').on('change', function() {
        const address = $(this).val();
        if (address) {
            charts.loadCharts(address);
        }
    });
});
```

## 🎯 Use Cases

### Real Estate Applications
- **Property listing pages** - Show historical value trends
- **Investment analysis** - Track ROI and tax implications
- **Market research** - Compare property appreciation rates

### Financial Applications  
- **Mortgage applications** - Display property value stability
- **Tax planning** - Visualize tax burden trends
- **Portfolio management** - Track real estate investments

### Government/Municipal
- **Assessment appeals** - Show historical assessment patterns
- **Tax policy analysis** - Understand tax revenue trends
- **Property database systems** - Enhanced data visualization

## 🛠️ Development Tips

1. **Error Handling**: The library includes comprehensive error handling for API failures, missing data, and network issues.

2. **Responsive Design**: Charts automatically resize and are mobile-friendly.

3. **Performance**: The library efficiently handles large datasets and includes loading states.

4. **Accessibility**: Charts include proper labeling and can be enhanced with ARIA attributes.

5. **Caching**: Consider implementing client-side caching for frequently accessed properties.

## 📱 Mobile Considerations

The charts are responsive but for mobile applications, consider:

```javascript
const isMobile = window.innerWidth < 768;
const charts = new AssessmentCharts({
    apiBaseUrl: 'http://localhost:5000',
    containerId: 'charts-container',
    width: isMobile ? 350 : 800,
    height: isMobile ? 300 : 400,
    margin: isMobile ? 
        { top: 20, right: 30, bottom: 60, left: 60 } :
        { top: 20, right: 50, bottom: 70, left: 80 }
});
```

## 🔒 Security Considerations

- **CORS**: Server includes CORS headers for cross-origin requests
- **Input Validation**: Address inputs are validated and sanitized
- **Rate Limiting**: Consider implementing rate limiting for production use
- **API Keys**: Attom API keys are server-side only, not exposed to clients

## 🚀 Getting Started Checklist

- [ ] Start your Flask server: `python3 property_rest_api.py`
- [ ] Test the charts interface: Visit `http://localhost:5000/charts`
- [ ] Try the demo: Visit `http://localhost:5000/static/demo.html`
- [ ] Include D3.js and the library in your application
- [ ] Create a container element
- [ ] Initialize AssessmentCharts with your configuration
- [ ] Call `loadCharts()` with a property address

## 🆘 Troubleshooting

**Charts not loading?**
- Check that D3.js is loaded before the assessment-charts.js library
- Verify the API server is running on the correct port
- Check browser console for JavaScript errors

**Data not displaying?**
- Ensure the property address exists in the Attom database
- Check that your API key is valid and active
- Verify the address format is correct

**Styling issues?**
- The library uses inline styles that can be overridden with CSS
- Check for CSS conflicts with existing styles
- Use browser developer tools to inspect chart elements

---

🎉 **You now have a complete, production-ready property assessment visualization system!**

Your developers can easily embed these interactive charts in any web application, providing users with valuable insights into property value trends, tax implications, and market performance over time.