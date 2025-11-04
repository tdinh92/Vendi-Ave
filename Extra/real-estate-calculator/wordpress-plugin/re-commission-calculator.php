<?php
/**
 * Plugin Name: Real Estate Commission Calculator
 * Plugin URI: https://github.com/yourusername/re-calculator
 * Description: A beautiful commission calculator showing home sellers what they'll actually take home after fees. Use shortcode [re_calculator] to display.
 * Version: 1.0.0
 * Author: Your Name
 * Author URI: https://yourwebsite.com
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Main plugin class
 */
class RE_Commission_Calculator {

    /**
     * Constructor
     */
    public function __construct() {
        // Register shortcode
        add_shortcode('re_calculator', array($this, 'render_calculator'));

        // Register Gutenberg block (optional, for block editor)
        add_action('init', array($this, 'register_block'));
    }

    /**
     * Render the calculator
     */
    public function render_calculator($atts = array()) {
        // Parse attributes (for future customization)
        $atts = shortcode_atts(array(
            'default_price' => '500000',
            'default_commission' => '6',
            'default_mortgage' => '300000',
            'default_closing' => '5000'
        ), $atts);

        // Start output buffering
        ob_start();

        // Include the calculator HTML with inline CSS and JS
        include plugin_dir_path(__FILE__) . 'templates/calculator-template.php';

        // Return the buffered content
        return ob_get_clean();
    }

    /**
     * Register Gutenberg block (optional)
     */
    public function register_block() {
        // Register block only if Gutenberg is available
        if (!function_exists('register_block_type')) {
            return;
        }

        register_block_type('re-calculator/commission-calculator', array(
            'render_callback' => array($this, 'render_calculator'),
        ));
    }
}

// Initialize the plugin
new RE_Commission_Calculator();
