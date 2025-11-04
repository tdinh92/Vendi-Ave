# 🏠 Real Estate Commission Calculator

A beautiful, interactive calculator that shows home sellers **exactly** what they'll take home after selling their property - with special emphasis on real estate agent commissions.

![Calculator Preview](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![No Dependencies](https://img.shields.io/badge/Dependencies-None-blue)
![WordPress Compatible](https://img.shields.io/badge/WordPress-Compatible-blue)

---

## ✨ Features

### 💰 Comprehensive Breakdown
- **Gross Sale Price** - What the home sells for
- **Agent Commission** - Prominently highlighted in red (typically 5-6%)
- **Mortgage Payoff** - Remaining loan balance
- **Closing Costs** - Title, escrow, and other fees
- **Other Fees** - Optional repairs, staging, warranties, etc.
- **Net Proceeds** - What the seller actually keeps (highlighted in green)

### 📊 Visual Analytics
- **Interactive Bar Chart** - Shows where every dollar goes
- **Real-Time Calculations** - Updates instantly as you type
- **Percentage Breakdown** - See exactly what % goes to each category
- **Prominent Agent Fee Display** - Makes commission costs crystal clear

### 🎨 Beautiful Design
- **Modern UI** - Purple gradient header with clean, professional styling
- **Responsive** - Works perfectly on desktop, tablet, and mobile
- **Smooth Animations** - Hover effects and transitions
- **Color-Coded Results** - Red for deductions, green for proceeds

### ⚡ User-Friendly
- **Slider for Commission** - Easy adjustment from 1% to 10%
- **Auto-Formatting** - Numbers automatically format with commas
- **Smart Defaults** - Pre-filled with typical values
- **No Coding Required** - Multiple easy installation options

---

## 🚀 Quick Start

### Option 1: Standalone HTML (Easiest!)

1. Open `calculator-standalone.html` in any web browser
2. That's it! The calculator works completely offline.

**For WordPress users:**
- Copy the entire contents of `calculator-standalone.html`
- Paste into a WordPress Custom HTML block
- Publish!

### Option 2: Modular Files (For Developers)

Use the separate HTML, CSS, and JS files for easier customization:

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="calculator.css">
</head>
<body>
    <!-- Include calculator.html content -->
    <script src="calculator.js"></script>
</body>
</html>
```

### Option 3: WordPress Plugin

1. Upload the `wordpress-plugin` folder to your WordPress plugins directory
2. Activate the plugin
3. Use the shortcode: `[re_calculator]`

**Detailed instructions:** See [WORDPRESS_INTEGRATION_GUIDE.md](WORDPRESS_INTEGRATION_GUIDE.md)

---

## 📁 File Structure

```
real-estate-calculator/
├── README.md                              # This file
├── WORDPRESS_INTEGRATION_GUIDE.md         # Step-by-step WordPress setup
│
├── calculator.html                        # Modular HTML (for developers)
├── calculator.css                         # Modular CSS (for developers)
├── calculator.js                          # Modular JavaScript (for developers)
│
├── calculator-standalone.html             # All-in-one file (for easy deployment)
│
└── wordpress-plugin/                      # WordPress plugin
    ├── re-commission-calculator.php       # Main plugin file
    └── templates/
        └── calculator-template.php        # Calculator template
```

---

## 🎯 Use Cases

### For Real Estate Professionals
- **Agent Websites** - Help sellers understand costs upfront
- **Listing Pages** - Show potential proceeds for specific properties
- **Educational Resources** - Teach clients about selling expenses

### For Homeowners
- **Planning** - Estimate proceeds before listing
- **Comparison** - Compare costs at different price points
- **Negotiation** - Understand commission impact

### For Developers
- **Client Projects** - Easy to integrate into real estate websites
- **Customization** - Clean code, easy to modify
- **White-Label** - Remove branding, add your own

---

## 🛠️ Customization

### Change Default Values

Edit these values in the HTML:

```html
<input type="text" id="salePrice" value="500000">          <!-- Sale price -->
<input type="range" id="commissionRate" value="6">        <!-- Commission % -->
<input type="text" id="mortgageBalance" value="300000">    <!-- Mortgage -->
<input type="text" id="closingCosts" value="5000">         <!-- Closing costs -->
```

### Change Colors

In the CSS, modify these color variables:

```css
/* Header gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Agent commission (red) */
--agent-color: #dc2626;

/* Net proceeds (green) */
--proceeds-color: #10b981;

/* Other elements */
--mortgage-color: #f59e0b;
--costs-color: #6b7280;
```

### Modify Commission Range

Change the slider min/max:

```html
<input type="range" id="commissionRate" min="1" max="10" step="0.1" value="6">
```

### Add Your Branding

Add a logo or custom footer in the HTML:

```html
<div class="calculator-header">
    <img src="your-logo.png" alt="Your Company">
    <h1>Home Sale Proceeds Calculator</h1>
</div>
```

---

## 📱 Browser Support

- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers (iOS/Android)

**No external dependencies required!** Pure HTML, CSS, and vanilla JavaScript.

---

## 🔒 Privacy & Security

- **100% Client-Side** - All calculations happen in the browser
- **No Data Collection** - Nothing is sent to any servers
- **No Tracking** - No analytics or cookies
- **Offline Capable** - Works without an internet connection
- **Open Source** - Full transparency, inspect the code yourself

---

## 💡 Tips for Real Estate Agents

### Highlight the Value You Provide

While this calculator emphasizes commission costs, use it as a conversation starter to discuss the **value** you provide:

- **Market Expertise** - Pricing strategy, comparative market analysis
- **Marketing** - Professional photos, staging, open houses, online listings
- **Negotiation** - Getting the best price and terms
- **Paperwork** - Handling complex contracts and disclosures
- **Network** - Connections to inspectors, contractors, lenders
- **Time Savings** - Managing showings, answering questions, coordinating

### Positioning Strategies

**"Transparency First"** - Show clients exactly where their money goes, building trust

**"No Surprises"** - Help sellers plan financially with accurate estimates

**"Education Tool"** - Explain the selling process and associated costs

**"Comparison Shopping"** - Show how different commission rates affect net proceeds

---

## 🎨 Customization Examples

### Example 1: Luxury Market

```html
<!-- Higher default values for luxury properties -->
<input type="text" id="salePrice" value="2000000">
<input type="text" id="mortgageBalance" value="800000">
<input type="text" id="closingCosts" value="15000">
```

### Example 2: Lower Commission Area

```html
<!-- If your market has lower typical commissions -->
<input type="range" id="commissionRate" value="4.5">
```

### Example 3: Custom Branding Colors

```css
/* Match your company's brand colors */
.calculator-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
}

.agent-commission-highlight {
    border-color: #1e3a8a;
}
```

---

## 📊 Example Calculations

### Scenario 1: Typical Suburban Home
- **Sale Price:** $500,000
- **Commission:** 6% = $30,000
- **Mortgage:** $300,000
- **Closing Costs:** $5,000
- **Net Proceeds:** $165,000

### Scenario 2: Paid-Off Home
- **Sale Price:** $500,000
- **Commission:** 6% = $30,000
- **Mortgage:** $0
- **Closing Costs:** $5,000
- **Net Proceeds:** $465,000

### Scenario 3: Lower Commission
- **Sale Price:** $500,000
- **Commission:** 4% = $20,000
- **Mortgage:** $300,000
- **Closing Costs:** $5,000
- **Net Proceeds:** $175,000 (saves $10,000!)

---

## 🤝 Contributing

Found a bug? Have a feature request? Want to improve the design?

1. Fork the repository
2. Make your changes
3. Submit a pull request

All contributions are welcome!

---

## 📄 License

This project is open source and available under the MIT License.

**Free to use for:**
- Personal websites
- Client projects
- Commercial real estate sites
- Educational purposes

**Attribution appreciated but not required!**

---

## 🙋 FAQ

### Can I use this on my real estate website?
**Yes!** That's exactly what it's designed for. No attribution required.

### Does it work with WordPress?
**Yes!** See the [WORDPRESS_INTEGRATION_GUIDE.md](WORDPRESS_INTEGRATION_GUIDE.md) for step-by-step instructions.

### Can I change the colors and branding?
**Absolutely!** All CSS is customizable. See the Customization section above.

### Does it require any external libraries?
**No!** It's pure HTML, CSS, and vanilla JavaScript. No jQuery, React, or other dependencies.

### Will it work on mobile devices?
**Yes!** Fully responsive design works great on phones and tablets.

### Is the data secure?
**Yes!** All calculations happen in the browser. No data is transmitted anywhere.

### Can I add more input fields?
**Yes!** The code is well-structured and easy to extend. Just add new inputs and update the calculation function.

### Does it calculate property taxes?
**No**, but you can easily add this feature by adding another input field and including it in the deductions.

---

## 📞 Support

Need help? Have questions?

- 📖 Check the [WORDPRESS_INTEGRATION_GUIDE.md](WORDPRESS_INTEGRATION_GUIDE.md)
- 💬 Open an issue on GitHub
- 📧 Contact your web developer

---

## 🎉 Acknowledgments

Built with modern web standards and best practices:
- Clean, semantic HTML5
- Modern CSS3 with flexbox and grid
- Vanilla ES6+ JavaScript
- Mobile-first responsive design

---

**Made with ❤️ for real estate professionals who believe in transparency and helping clients make informed decisions.**

---

## 📈 Version History

### v1.0.0 (Current)
- ✅ Complete calculator functionality
- ✅ Visual breakdown bar chart
- ✅ Responsive design
- ✅ WordPress plugin support
- ✅ Standalone HTML version
- ✅ Comprehensive documentation

---

**Ready to help your clients understand the true costs of selling a home?**

[Get Started →](#-quick-start)
