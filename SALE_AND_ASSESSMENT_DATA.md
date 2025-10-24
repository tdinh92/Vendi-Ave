# Sale Snapshot vs Assessment Snapshot Data

## 📊 Assessment Snapshot Data (`/assessment/snapshot`)

### What We Extract and Display:
- **Total Assessed Value**: `assessment.assessed.assdttlvalue` = **$1,131,800**
- **Tax Amount**: `assessment.tax.taxamt` = **$12,959.0**
- **Tax Year**: `assessment.tax.taxyear` = **2025**

### Additional Available Data (Not Currently Used):

#### Assessed Values:
- `assdimprvalue`: **$787,100** (Improvement/Building value)
- `assdlandvalue`: **$344,700** (Land value)
- `assdimprpersizeunit`: **$257.73** (Improvement value per sq ft)
- `assdlandpersizeunit`: **$13.88** (Land value per sq ft)
- `assdttlpersizeunit`: **$370.60** (Total assessed per sq ft)

#### Tax Information:
- `taxpersizeunit`: **$4.24** (Tax per sq ft)

#### Calculations:
- `calcimprvalue`: $787,100 (Calculated improvement value)
- `calclandvalue`: $344,700 (Calculated land value)
- `calcttlvalue`: $1,131,800 (Calculated total value)
- `calcvaluepersizeunit`: $370.60 (Calculated value per sq ft)

#### Property Details (Also in Assessment):
- Address, lot size, location, property type, year built, beds, baths, sqft

---

## 💰 Sale Snapshot Data (`/sale/snapshot`)

### What We Extract and Display:
- **Sale Amount**: `sale.amount.saleamt` = **$370,000**
- **Sale Date**: `sale.amount.salerecdate` = **"2000-04-28"** (April 28, 2000)
- **Price Per Sq Ft**: `sale.calculation.pricepersizeunit` = **$121.15**

### Additional Available Data (Not Currently Used):

#### Sale Details:
- `saledoctype`: **"DEED"** (Type of sale document)
- `saledocnum`: **"10791-127"** (Document number)
- `saletranstype`: **"Resale"** (Transaction type: Resale, New Construction, etc.)
- `saledisclosuretype`: **0** (Disclosure type code)
- `salesearchdate`: "2000-04-28" (Sale search date)

#### Calculations:
- `priceperbed`: **$123,333** (Sale price per bedroom)
- `pricepersizeunit`: **$121.15** (Sale price per sq ft)

#### Vintage:
- `lastModified`: "2018-12-01" (Last time sale data was updated)

#### Property Details (Also in Sale):
- Address, lot size, location, property type, year built, beds, baths, sqft

---

## 🔍 What We're Currently Using in Option 8

### From Assessment Snapshot (15 calls):
✅ **Total Assessed Value** - The current assessed value from the tax assessor
✅ **Tax Amount** - Annual property tax
✅ **Tax Year** - Which year the assessment is for (2024 or 2025)

### From Sale Snapshot (15 calls):
✅ **Sale Price** - Last recorded sale price
✅ **Sale Date** - When the property last sold
✅ **Price Per Sq Ft** - Calculated sale price per square foot

### From Property Detail Search (1 call):
✅ Property characteristics (beds, baths, sqft, year built, distance)

---

## 💡 Potential Enhancements

### Data We Could Add:
1. **Land vs Improvement Values** - Show breakdown of assessed value
2. **Document Details** - Show deed type and document number
3. **Transaction Type** - Show if it's a resale, new construction, etc.
4. **Tax Per Sq Ft** - Show tax burden per square foot
5. **Assessed Per Sq Ft** - Compare to sale price per sq ft

### Example Enhanced Display:
```
Property #1
  Address: 4 FIORENZA DR, WILMINGTON, MA 01887
  Distance: 0.0 miles

  ASSESSMENT DATA (2025):
    Total Assessed: $1,131,800
    - Land: $344,700 ($13.88/sqft)
    - Building: $787,100 ($257.73/sqft)
    Tax Amount: $12,959.0 ($4.24/sqft)

  SALE DATA:
    Last Sale: $370,000 (April 28, 2000)
    Price/SqFt: $121.15
    Transaction: Resale via DEED #10791-127
```

---

## 📈 Key Insights

### Assessment vs Sale Price:
For the subject property (4 Fiorenza Drive):
- **Current Assessed Value (2025)**: $1,131,800
- **Last Sale (2000)**: $370,000
- **Appreciation**: +206% over 25 years

### Value Per Square Foot:
- **Assessed (2025)**: $370.60/sqft
- **Sale (2000)**: $121.15/sqft
- **Increase**: +206%

### Tax Burden:
- **Annual Tax**: $12,959
- **Tax per Sq Ft**: $4.24/sqft
- **Effective Tax Rate**: 1.14% (tax/assessed value)

---

## 🎯 Summary

**Assessment Snapshot** = Current government valuation and tax data (what you owe)
**Sale Snapshot** = Historical transaction data (what it actually sold for)

Together, they provide:
- **Current value** (assessment) vs **historical value** (sale)
- **Tax implications** (assessment) vs **market value** (sale)
- **Appreciation trends** by comparing assessment growth to sale price
