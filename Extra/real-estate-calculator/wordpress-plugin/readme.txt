=== Real Estate Commission Calculator ===
Contributors: yourusername
Tags: real estate, calculator, commission, mortgage, home selling
Requires at least: 5.0
Tested up to: 6.4
Stable tag: 1.0.0
Requires PHP: 7.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

A beautiful, interactive calculator showing home sellers what they'll actually take home after selling - with emphasis on agent commissions.

== Description ==

The Real Estate Commission Calculator helps home sellers understand the true costs of selling their property. It provides a clear, visual breakdown showing exactly where their money goes - with special emphasis on real estate agent commissions.

**Features:**

* **Comprehensive Breakdown** - Shows gross sale price, agent commission, mortgage payoff, closing costs, and net proceeds
* **Visual Analytics** - Interactive bar chart showing percentage breakdown
* **Real-Time Calculations** - Updates instantly as values change
* **Prominent Commission Display** - Highlights agent fees in red with clear warning message
* **Mobile Responsive** - Works perfectly on all devices
* **Easy to Use** - Simple shortcode integration
* **No Dependencies** - Pure HTML, CSS, and JavaScript

**Perfect For:**

* Real estate agent websites
* Property listing pages
* Seller resource sections
* Educational blog posts
* Client communication tools

**How It Works:**

Users enter:
1. Home sale price
2. Agent commission percentage (adjustable slider)
3. Remaining mortgage balance
4. Estimated closing costs
5. Optional other fees

The calculator instantly shows:
* Total deductions
* Agent commission amount (prominently highlighted)
* Net proceeds (what the seller keeps)
* Visual percentage breakdown

**Why This Calculator?**

This calculator emphasizes **transparency**. It helps sellers understand that a $500,000 home sale with a 6% commission and $300,000 mortgage means:
* $30,000 goes to agents (6%)
* $300,000 pays off mortgage (60%)
* $5,000 for closing costs (1%)
* **Only $165,000 actually goes to the seller (33%)**

== Installation ==

**Automatic Installation:**

1. Log in to your WordPress admin panel
2. Go to Plugins → Add New
3. Search for "Real Estate Commission Calculator"
4. Click "Install Now" and then "Activate"

**Manual Installation:**

1. Download the plugin zip file
2. Go to Plugins → Add New → Upload Plugin
3. Choose the zip file and click "Install Now"
4. Click "Activate Plugin"

**Using the Calculator:**

After activation, add the calculator to any page or post using the shortcode:

`[re_calculator]`

**With Custom Defaults:**

`[re_calculator default_price="750000" default_commission="5.5" default_mortgage="400000" default_closing="7000"]`

== Frequently Asked Questions ==

= How do I add the calculator to my page? =

Simply add the shortcode `[re_calculator]` to any page or post using the Shortcode block or in a Classic Editor.

= Can I customize the default values? =

Yes! Use shortcode attributes:

`[re_calculator default_price="600000" default_commission="5" default_mortgage="350000" default_closing="6000"]`

= Does it work with page builders? =

Yes! Works with Gutenberg, Classic Editor, Elementor, Divi, and other page builders. Just add a Shortcode element and paste `[re_calculator]`.

= Is it mobile-friendly? =

Absolutely! The calculator is fully responsive and works beautifully on phones, tablets, and desktops.

= Does it send data to any servers? =

No! All calculations happen in the user's browser. No data is collected or transmitted.

= Can I use it on multiple pages? =

Yes! Use the shortcode on as many pages as you want.

= Will it slow down my site? =

No. The calculator is lightweight and has zero external dependencies.

= Can I change the colors? =

Yes, but it requires custom CSS. Contact a developer or check the plugin documentation.

= Does it work with my theme? =

Yes! The calculator uses unique CSS classes to avoid conflicts with themes.

== Screenshots ==

1. Full calculator interface showing all input fields and visual breakdown
2. Mobile responsive design
3. Visual bar chart showing where money goes
4. Agent commission prominently highlighted in red
5. Net proceeds highlighted in green

== Changelog ==

= 1.0.0 =
* Initial release
* Real-time calculation functionality
* Visual breakdown bar chart
* Responsive design
* Shortcode support with custom attributes
* WordPress 6.4 compatibility

== Upgrade Notice ==

= 1.0.0 =
Initial release of Real Estate Commission Calculator plugin.

== Shortcode Attributes ==

**Available Attributes:**

* `default_price` - Default sale price (default: 500000)
* `default_commission` - Default commission percentage (default: 6)
* `default_mortgage` - Default mortgage balance (default: 300000)
* `default_closing` - Default closing costs (default: 5000)

**Example Usage:**

`[re_calculator default_price="850000" default_commission="5.5"]`

== Support ==

For support, documentation, and customization help, visit the plugin's GitHub repository or contact the developer.

== Credits ==

Built with modern web standards:
* HTML5
* CSS3 (Flexbox & Grid)
* Vanilla JavaScript (ES6+)

No external dependencies required!

== Privacy Policy ==

This plugin does not:
* Collect any user data
* Use cookies
* Make external API calls
* Track analytics
* Store any information

All calculations are performed client-side in the user's browser.
