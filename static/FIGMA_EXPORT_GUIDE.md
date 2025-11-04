# Figma Export Guide - Value Range Slider Visualization

## 📊 Overview

This guide explains how to get the **Value Range Slider** visualization into Figma for your UI designer to edit and customize.

## 🎯 File Location

**Standalone Component:** [static/value-range-slider.html](static/value-range-slider.html)

## 🚀 Method 1: Screenshot + Import (Quickest)

### Steps:
1. **Open the HTML file** in your browser:
   - Navigate to `static/value-range-slider.html`
   - Or visit: `http://localhost:5000/static/value-range-slider.html` (if Flask server running)

2. **Take a high-quality screenshot:**
   - **Mac**: `Cmd + Shift + 4` (drag to select area)
   - **Windows**: `Win + Shift + S` or use Snipping Tool
   - **Browser Extension**: Use "Full Page Screen Capture" for entire page

3. **Import to Figma:**
   - Drag and drop the screenshot into Figma
   - Use as reference for building components
   - Trace over elements to create editable vectors

### Pros:
- ✅ Fastest method
- ✅ Shows exact rendered result
- ✅ No technical setup required

### Cons:
- ❌ Not editable (just an image)
- ❌ Designer must recreate components manually
- ❌ Not responsive

---

## 🎨 Method 2: HTML to Figma Plugin (Recommended)

### Option A: "html.to.design" Plugin

1. **Install the plugin in Figma:**
   - Go to Figma → Plugins → Browse plugins
   - Search for **"html.to.design"**
   - Click "Install"

2. **Prepare the HTML:**
   - Open [value-range-slider.html](static/value-range-slider.html)
   - Copy the entire HTML source code

3. **Import to Figma:**
   - In Figma, right-click → Plugins → html.to.design
   - Paste the HTML code
   - Click "Import"
   - The plugin converts HTML/CSS to Figma layers

### Option B: "Figma to Code" (Reverse Process)

1. **Install "Figma to Code"** plugin
2. Use the "Import from URL" feature
3. Point to your local server: `http://localhost:5000/static/value-range-slider.html`

### Pros:
- ✅ Converts to editable Figma layers
- ✅ Preserves structure and styling
- ✅ Designer can modify directly

### Cons:
- ❌ May need adjustments after import
- ❌ Some CSS effects might not convert perfectly
- ❌ Requires plugin installation

---

## 🔧 Method 3: Manual Recreation in Figma (Best Quality)

### Use this guide for your designer to recreate the component:

### **Component Breakdown:**

#### 1. **Container**
- **Size**: 800px wide (responsive)
- **Background**: White (#FFFFFF)
- **Padding**: 40px all sides
- **Border Radius**: 16px
- **Shadow**: 0px 4px 20px rgba(0, 0, 0, 0.08)

#### 2. **Title**
- **Text**: "Estimated Property Value Range"
- **Font**: SF Pro / Inter / System UI
- **Size**: 24px (1.5rem)
- **Weight**: Bold (700)
- **Color**: #1e293b
- **Alignment**: Center

#### 3. **Most Likely Value**
- **Label**:
  - Text: "MOST LIKELY VALUE (AVM)"
  - Size: 15px (0.95rem)
  - Weight: 600
  - Color: #64748b
  - Transform: Uppercase
  - Letter Spacing: 0.5px

- **Value**:
  - Text: "$1,327,564"
  - Size: 48px (3rem)
  - Weight: Extra Bold (800)
  - Color: #1e3a8a
  - Alignment: Center

#### 4. **Range Slider** (The Gradient Bar)
- **Size**: 100% width × 12px height
- **Border Radius**: 6px
- **Gradient**: Linear (left to right)
  - 0%: #ef4444 (Red)
  - 25%: #f59e0b (Orange)
  - 50%: #10b981 (Green)
  - 75%: #f59e0b (Orange)
  - 100%: #ef4444 (Red)
- **Shadow**: 0px 2px 8px rgba(0, 0, 0, 0.1)

#### 5. **Range Marker** (The Dot)
- **Size**: 24px × 24px circle
- **Fill**: White (#FFFFFF)
- **Border**: 4px solid #1e3a8a
- **Shadow**: 0px 4px 12px rgba(0, 0, 0, 0.2)
- **Position**: Centered vertically on slider, horizontally positioned based on value

- **Arrow (Marker Indicator)**:
  - Triangle pointing down
  - Color: #1e3a8a
  - Size: 12px wide × 8px tall
  - Position: 30px above marker

#### 6. **Range Labels** (Low & High)
- **Layout**: Flex row, space-between
- **Gap**: 20px

- **Each Label**:
  - Title: "LOW ESTIMATE" / "HIGH ESTIMATE"
    - Size: 14px (0.85rem)
    - Weight: 600
    - Color: #64748b
    - Transform: Uppercase
    - Letter Spacing: 0.5px

  - Value: "$1,261,185" / "$1,393,942"
    - Size: 21px (1.3rem)
    - Weight: Bold (700)
    - Color: #1e293b

#### 7. **Metric Cards** (FSD & Value Range)
- **Layout**: 2-column grid, 20px gap

- **Each Card**:
  - Background: #f8fafc
  - Padding: 25px
  - Border: 2px solid #e2e8f0
  - Border Radius: 12px
  - Alignment: Center

  - **Value**: "5.0%" / "$132,757"
    - Size: 32px (2rem)
    - Weight: Extra Bold (800)
    - Color: #1e3a8a

  - **Label**: "FSD" / "Value Range"
    - Size: 15px (0.95rem)
    - Weight: 600
    - Color: #64748b

  - **Description**: "Forecast Standard Deviation" / "High - Low Difference"
    - Size: 13px (0.8rem)
    - Weight: Regular (400)
    - Color: #94a3b8
    - Style: Italic

### **Color Palette for Figma:**

```
Primary Blue Dark: #1e3a8a
Primary Blue: #3b82f6
Slate 900: #1e293b
Slate 600: #64748b
Slate 400: #94a3b8
Slate 200: #e2e8f0
Slate 50: #f8fafc

Gradient Colors:
- Red: #ef4444
- Orange: #f59e0b
- Green: #10b981
```

---

## 📐 Method 4: SVG Export (For Vector Graphics)

### For Individual Elements:

1. **Extract specific components** as SVG:
   - Open browser DevTools (F12)
   - Right-click on the gradient bar → Copy → Copy element
   - Paste into an SVG editor (like Figsvg.com or SVGOMG)
   - Export as .svg file

2. **Import SVG to Figma:**
   - Drag and drop .svg files into Figma
   - Fully editable as vectors
   - Perfect for the gradient slider bar

### Create SVG from scratch for Figma:

```svg
<!-- Gradient Slider Bar SVG -->
<svg width="760" height="12" viewBox="0 0 760 12" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="valueGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#ef4444;stop-opacity:1" />
      <stop offset="25%" style="stop-color:#f59e0b;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#10b981;stop-opacity:1" />
      <stop offset="75%" style="stop-color:#f59e0b;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#ef4444;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="760" height="12" rx="6" fill="url(#valueGradient)" />
</svg>
```

---

## 🔄 Method 5: Figma API + Code Components (Advanced)

### For developers with Figma API access:

1. **Use Figma REST API** to programmatically create components
2. **Code Connect** feature in Figma can link your HTML/CSS to Figma designs
3. **Component Libraries** can be synced between code and design

---

## 🎓 Recommended Workflow for Your UI Designer:

### **Step-by-Step:**

1. **Use Method 1 (Screenshot)** initially for reference
2. **Manually recreate in Figma** using the component breakdown above
3. **Create Figma components** for:
   - Value Range Slider (with variants for different positions)
   - Metric Cards (reusable component)
   - Value Display (component with text properties)

4. **Set up Auto Layout**:
   - Main container: Vertical auto layout, 40px padding
   - Range labels: Horizontal auto layout, space-between
   - Metrics: Horizontal auto layout, 20px gap

5. **Add Constraints**:
   - Slider bar: Left & Right constraints (responsive width)
   - Marker: Top constraint, horizontal position variable
   - Text: Center-aligned with fill container width

6. **Create Interactive Prototype**:
   - Add variants for different value positions
   - Use Figma variables for AVM value, low, high
   - Prototype marker movement (optional)

---

## 🚀 Quick Start for Your Designer:

### **Send them this:**

> "Hey! I need you to recreate this value range slider visualization in Figma.
>
> **Files:**
> - View the component: Open `static/value-range-slider.html` in a browser
> - Design specs: See `FIGMA_EXPORT_GUIDE.md` → "Component Breakdown" section
>
> **What I need:**
> - Recreate the gradient slider bar with marker
> - Make it a reusable Figma component
> - Use variables for the values (low, AVM, high)
> - Ensure it's responsive (scales to different widths)
>
> **Colors and measurements are all documented in the guide!**"

---

## 📊 Example Values (For Demo):

- **Low Estimate**: $1,261,185
- **AVM Value**: $1,327,564 (Most Likely)
- **High Estimate**: $1,393,942
- **FSD**: 5.0%
- **Value Range**: $132,757

---

## 💡 Pro Tips:

1. **Use Figma Variants** to show different marker positions (e.g., Low, Medium, High confidence scenarios)
2. **Create Figma Variables** for all numeric values so they can be easily updated
3. **Set up Component Properties** to make the slider reusable with different data
4. **Use Auto Layout** for responsive behavior
5. **Add Hover States** to the marker for interactivity mockups
6. **Create a Figma Plugin** (if doing this often) to auto-generate slider from data

---

## 🆘 Troubleshooting:

**Q: HTML plugins not working?**
- Try a different browser
- Check if the HTML is well-formed (validate at validator.w3.org)
- Simplify the HTML first (remove JavaScript)

**Q: Colors look different in Figma?**
- Ensure Figma color space is set to sRGB
- Convert hex colors manually if needed
- Check display calibration

**Q: Gradient not smooth?**
- Use Figma's native gradient tool
- Add more gradient stops for smoother transitions
- Use "Linear" gradient type, 0° angle

---

## 📚 Additional Resources:

- **Figma Gradient Tutorial**: https://help.figma.com/hc/en-us/articles/360041068494
- **HTML to Figma Plugin**: https://www.figma.com/community/plugin/1159123024924461424
- **Figma Auto Layout Guide**: https://help.figma.com/hc/en-us/articles/360040451373

---

**✅ You're all set! Your UI designer should be able to recreate this visualization in Figma with these resources.**
