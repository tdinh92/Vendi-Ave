# 📘 WordPress Integration Guide - Real Estate Commission Calculator

## 🎯 Overview

This guide will show you **3 easy ways** to add the Real Estate Commission Calculator to your WordPress website. No coding experience required!

---

## 🚀 Method 1: Copy & Paste (Easiest - 2 Steps!)

**Best for**: Beginners who just want to get it working quickly

### Step 1: Copy the Code

1. Open the file `calculator-standalone.html` in a text editor (Notepad, TextEdit, etc.)
2. Select all the code (`Ctrl+A` or `Cmd+A`)
3. Copy it (`Ctrl+C` or `Cmd+C`)

### Step 2: Paste into WordPress

1. Log in to your WordPress admin dashboard
2. Go to **Pages** → **Add New** (or edit an existing page)
3. Click the **+** button to add a new block
4. Search for "**Custom HTML**" and click it
5. Paste the code (`Ctrl+V` or `Cmd+V`)
6. Click **Publish** or **Update**

**That's it!** Your calculator is now live! 🎉

---

## 🔌 Method 2: WordPress Plugin (Easy - 3 Steps!)

**Best for**: If you want to use the calculator on multiple pages with a simple shortcode

### Step 1: Upload the Plugin

1. Download the `wordpress-plugin` folder from this repository
2. Zip the `wordpress-plugin` folder (right-click → Compress/Send to → Compressed folder)
3. Rename the zip file to `re-commission-calculator.zip`

### Step 2: Install in WordPress

1. Log in to WordPress admin
2. Go to **Plugins** → **Add New**
3. Click **Upload Plugin** (top of page)
4. Click **Choose File** and select `re-commission-calculator.zip`
5. Click **Install Now**
6. Click **Activate**

### Step 3: Add to Your Pages

Now you can add the calculator to any page/post using the shortcode:

```
[re_calculator]
```

**How to add the shortcode:**
1. Edit any page or post
2. Add a **Shortcode** block (click +, search "Shortcode")
3. Type: `[re_calculator]`
4. Publish!

**Customize default values (optional):**
```
[re_calculator default_price="750000" default_commission="5.5" default_mortgage="400000" default_closing="7000"]
```

---

## 📁 Method 3: Upload as Media File (Medium - 4 Steps!)

**Best for**: If you want to host it separately and embed it

### Step 1: Upload to WordPress

1. Log in to WordPress admin
2. Go to **Media** → **Add New**
3. Click **Select Files**
4. Upload `calculator-standalone.html`
5. After upload, click the file and copy the **File URL** (something like `https://yoursite.com/wp-content/uploads/2024/01/calculator-standalone.html`)

### Step 2: Create an Embed Code

Replace `YOUR-FILE-URL-HERE` with the URL you copied:

```html
<iframe src="YOUR-FILE-URL-HERE" width="100%" height="1200px" frameborder="0" style="border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);"></iframe>
```

### Step 3: Add to Your Page

1. Edit a page or post
2. Add a **Custom HTML** block
3. Paste your iframe code
4. Publish!

---

## 🎨 Customization Tips

### Change Default Values

**Method 1 (Custom HTML):**
Find these lines in the HTML and change the values:
```html
<input type="text" id="salePrice" value="500000">           <!-- Default sale price -->
<input type="range" id="commissionRate" value="6">         <!-- Default commission -->
<input type="text" id="mortgageBalance" value="300000">     <!-- Default mortgage -->
<input type="text" id="closingCosts" value="5000">          <!-- Default closing costs -->
```

**Method 2 (Plugin):**
Use shortcode attributes:
```
[re_calculator default_price="600000" default_commission="5.5"]
```

### Change Colors

Find the CSS section (in `<style>` tags) and modify these colors:

**Header Background:**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**Agent Commission (Red):**
```css
background: #dc2626;  /* Change to your color */
color: #dc2626;       /* Change to your color */
```

**Net Proceeds (Green):**
```css
background: #10b981;  /* Change to your color */
color: #10b981;       /* Change to your color */
```

---

## ❓ Troubleshooting

### Calculator Not Showing Up?

**If using Custom HTML:**
- Make sure you're using the **Custom HTML** block, not the regular HTML/Code block
- Check that you copied ALL the code from the file
- Try switching to "Code Editor" mode in WordPress (top right, three dots menu)

**If using Plugin:**
- Make sure the plugin is activated (Plugins → Installed Plugins)
- Check that you spelled the shortcode correctly: `[re_calculator]` (with underscores, not spaces)
- Try clearing your browser cache (Ctrl+Shift+Delete)

### Calculator Looks Weird/Broken?

- Your WordPress theme might have conflicting CSS
- Try adding `!important` to the CSS rules (this makes them override theme styles)
- Contact your theme support if issues persist

### Calculator Not Calculating?

- Make sure JavaScript is enabled in your browser
- Check browser console for errors (F12 → Console tab)
- Some WordPress security plugins block inline JavaScript - try whitelisting the calculator

---

## 📱 Mobile Optimization

The calculator is **fully responsive** and works great on mobile devices! No extra configuration needed.

---

## 🔒 Security Notes

- The calculator runs **100% in the browser** (client-side)
- No data is sent to any servers
- No personal information is collected
- Safe to use with any WordPress setup

---

## 🆘 Need Help?

### Quick Checks:
1. ✅ Is the code fully copied/pasted?
2. ✅ Are you using the Custom HTML block?
3. ✅ Is the plugin activated (if using Method 2)?
4. ✅ Did you save/publish the page?

### Still Having Issues?

1. **Check WordPress version**: Make sure you're on WordPress 5.0+ (supports Gutenberg blocks)
2. **Test on a different page**: Create a fresh page with just the calculator
3. **Disable other plugins temporarily**: Check if another plugin is conflicting
4. **Try a different browser**: Rule out browser-specific issues

---

## 📊 Usage Examples

### Real Estate Agent Website
Add to your "Seller Resources" page:
```
[re_calculator default_price="650000" default_commission="5.5"]
```

### Home Listing Page
Embed next to property details:
```html
<iframe src="https://yoursite.com/calculator.html" width="100%" height="1200px"></iframe>
```

### Blog Post About Selling
Add inline with your content using the shortcode in a Shortcode block.

---

## 🎉 You're Done!

Congratulations! Your Real Estate Commission Calculator is now live on your WordPress site.

**Want to make changes?** Just edit the page and modify the Custom HTML block or shortcode attributes.

**Want to use on another page?** Just add the same Custom HTML code or shortcode - it's reusable!

---

## 📝 Summary Table

| Method | Difficulty | Steps | Best For |
|--------|-----------|-------|----------|
| **Copy & Paste** | ⭐ Easy | 2 | Quick setup, single page |
| **Plugin** | ⭐⭐ Easy | 3 | Multiple pages, shortcode use |
| **Media Upload** | ⭐⭐⭐ Medium | 4 | Separate hosting, iframe embed |

**Recommended**: Try **Method 1** first. If you like it and want to use it on multiple pages, upgrade to **Method 2** (Plugin).

---

*Made with ❤️ for real estate professionals who want to help their clients understand the true costs of selling a home.*
