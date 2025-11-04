<?php
/**
 * Calculator Template for WordPress
 * This template is loaded by the shortcode
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Get default values from shortcode attributes
$default_price = isset($atts['default_price']) ? esc_attr($atts['default_price']) : '500000';
$default_commission = isset($atts['default_commission']) ? esc_attr($atts['default_commission']) : '6';
$default_mortgage = isset($atts['default_mortgage']) ? esc_attr($atts['default_mortgage']) : '300000';
$default_closing = isset($atts['default_closing']) ? esc_attr($atts['default_closing']) : '5000';
?>

<style>
    .re-calc-container * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .re-calc-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        max-width: 1200px;
        margin: 0 auto 40px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        overflow: hidden;
        line-height: 1.6;
    }

    .re-calc-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px 30px;
        text-align: center;
    }

    .re-calc-header h2 {
        font-size: 2.5rem;
        margin-bottom: 10px;
        font-weight: 700;
    }

    .re-calc-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
    }

    .re-calc-content {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 40px;
        padding: 40px;
    }

    .re-calc-input-section {
        display: flex;
        flex-direction: column;
        gap: 25px;
    }

    .re-calc-input-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .re-calc-input-group label {
        font-weight: 600;
        color: #2d3748;
        font-size: 0.95rem;
    }

    .re-calc-input-wrapper {
        position: relative;
        display: flex;
        align-items: center;
    }

    .re-calc-currency-symbol {
        position: absolute;
        left: 15px;
        font-size: 1.2rem;
        color: #718096;
        font-weight: 600;
    }

    .re-calc-input-wrapper input[type="text"] {
        width: 100%;
        padding: 15px 15px 15px 35px;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        font-weight: 500;
    }

    .re-calc-input-wrapper input[type="text"]:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    .re-calc-slider-wrapper {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .re-calc-slider-wrapper input[type="range"] {
        flex: 1;
        height: 8px;
        border-radius: 5px;
        background: #e2e8f0;
        outline: none;
        -webkit-appearance: none;
    }

    .re-calc-slider-wrapper input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #dc2626;
        cursor: pointer;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }

    .re-calc-slider-wrapper input[type="range"]::-moz-range-thumb {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #dc2626;
        cursor: pointer;
        border: none;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }

    .re-calc-slider-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #dc2626;
        min-width: 60px;
        text-align: right;
    }

    .re-calc-helper-text {
        font-size: 0.85rem;
        color: #718096;
        font-style: italic;
    }

    .re-calc-results-section {
        background: #f7fafc;
        padding: 30px;
        border-radius: 15px;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .re-calc-results-section h3 {
        color: #2d3748;
        font-size: 1.8rem;
        margin-bottom: 10px;
    }

    .re-calc-results-section h4 {
        color: #4a5568;
        font-size: 1.2rem;
        margin-bottom: 10px;
    }

    .re-calc-result-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        background: white;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
    }

    .re-calc-result-item .label {
        font-weight: 500;
        color: #4a5568;
        font-size: 1rem;
    }

    .re-calc-result-item .value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2d3748;
    }

    .re-calc-result-item .value.negative {
        color: #dc2626;
    }

    .re-calc-gross-sale {
        border-color: #3b82f6;
        background: #eff6ff;
    }

    .re-calc-gross-sale .value {
        color: #3b82f6;
        font-size: 1.5rem;
    }

    .re-calc-agent-commission {
        border: 3px solid #dc2626;
        background: #fef2f2;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15);
        position: relative;
    }

    .re-calc-agent-commission::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #dc2626, #b91c1c);
    }

    .re-calc-commission-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }

    .re-calc-commission-header .label {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }

    .re-calc-commission-header .label strong {
        font-size: 1.1rem;
        color: #991b1b;
    }

    .re-calc-commission-percentage {
        font-size: 0.9rem;
        color: #dc2626;
        font-weight: 600;
    }

    .re-calc-commission-header .value {
        font-size: 1.8rem;
        color: #dc2626;
        font-weight: 800;
    }

    .re-calc-commission-warning {
        margin-top: 10px;
        padding: 10px 15px;
        background: #fee2e2;
        border-left: 4px solid #dc2626;
        border-radius: 5px;
        font-size: 0.95rem;
        color: #991b1b;
        font-weight: 500;
    }

    .re-calc-deductions {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .re-calc-net-proceeds {
        border: 3px solid #10b981;
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        padding: 20px;
        margin-top: 10px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
    }

    .re-calc-net-proceeds .label {
        font-size: 1.2rem;
        font-weight: 700;
        color: #047857;
    }

    .re-calc-net-proceeds .value {
        font-size: 2rem;
        font-weight: 800;
        color: #10b981;
    }

    .re-calc-visual-breakdown {
        margin-top: 20px;
        padding: 20px;
        background: white;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
    }

    .re-calc-breakdown-bar {
        width: 100%;
        height: 60px;
        display: flex;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }

    .re-calc-bar-segment {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        color: white;
    }

    .re-calc-bar-segment:hover {
        transform: scaleY(1.05);
        filter: brightness(1.1);
    }

    .re-calc-agent-segment {
        background: linear-gradient(135deg, #dc2626, #b91c1c);
    }

    .re-calc-mortgage-segment {
        background: linear-gradient(135deg, #f59e0b, #d97706);
    }

    .re-calc-costs-segment {
        background: linear-gradient(135deg, #6b7280, #4b5563);
    }

    .re-calc-proceeds-segment {
        background: linear-gradient(135deg, #10b981, #059669);
    }

    .re-calc-bar-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }

    .re-calc-bar-percentage {
        font-size: 1.1rem;
        font-weight: 700;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }

    .re-calc-breakdown-legend {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 15px;
    }

    .re-calc-legend-item {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.9rem;
        color: #4a5568;
    }

    .re-calc-legend-color {
        width: 20px;
        height: 20px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .re-calc-agent-color {
        background: linear-gradient(135deg, #dc2626, #b91c1c);
    }

    .re-calc-mortgage-color {
        background: linear-gradient(135deg, #f59e0b, #d97706);
    }

    .re-calc-costs-color {
        background: linear-gradient(135deg, #6b7280, #4b5563);
    }

    .re-calc-proceeds-color {
        background: linear-gradient(135deg, #10b981, #059669);
    }

    #reCalcOtherFeesRow.hidden {
        display: none;
    }

    @media (max-width: 968px) {
        .re-calc-content {
            grid-template-columns: 1fr;
            gap: 30px;
        }
        .re-calc-breakdown-legend {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 640px) {
        .re-calc-header h2 {
            font-size: 1.8rem;
        }
        .re-calc-content {
            padding: 20px;
        }
        .re-calc-bar-label {
            font-size: 0.65rem;
        }
        .re-calc-bar-percentage {
            font-size: 0.85rem;
        }
    }
</style>

<div class="re-calc-container">
    <div class="re-calc-header">
        <h2>Home Sale Proceeds Calculator</h2>
        <p class="re-calc-subtitle">See what you'll actually take home after selling your property</p>
    </div>

    <div class="re-calc-content">
        <div class="re-calc-input-section">
            <div class="re-calc-input-group">
                <label for="reCalcSalePrice">Home Sale Price</label>
                <div class="re-calc-input-wrapper">
                    <span class="re-calc-currency-symbol">$</span>
                    <input type="text" id="reCalcSalePrice" placeholder="500,000" value="<?php echo $default_price; ?>">
                </div>
            </div>

            <div class="re-calc-input-group">
                <label for="reCalcCommissionRate">Real Estate Agent Commission</label>
                <div class="re-calc-slider-wrapper">
                    <input type="range" id="reCalcCommissionRate" min="1" max="10" step="0.1" value="<?php echo $default_commission; ?>">
                    <span class="re-calc-slider-value"><span id="reCalcCommissionDisplay"><?php echo $default_commission; ?></span>%</span>
                </div>
                <p class="re-calc-helper-text">Typical agent commission is 5-6% of sale price</p>
            </div>

            <div class="re-calc-input-group">
                <label for="reCalcMortgageBalance">Remaining Mortgage Balance</label>
                <div class="re-calc-input-wrapper">
                    <span class="re-calc-currency-symbol">$</span>
                    <input type="text" id="reCalcMortgageBalance" placeholder="300,000" value="<?php echo $default_mortgage; ?>">
                </div>
            </div>

            <div class="re-calc-input-group">
                <label for="reCalcClosingCosts">Estimated Closing Costs</label>
                <div class="re-calc-input-wrapper">
                    <span class="re-calc-currency-symbol">$</span>
                    <input type="text" id="reCalcClosingCosts" placeholder="5,000" value="<?php echo $default_closing; ?>">
                </div>
                <p class="re-calc-helper-text">Typical closing costs: $3,000 - $8,000</p>
            </div>

            <div class="re-calc-input-group">
                <label for="reCalcOtherFees">Other Fees (Optional)</label>
                <div class="re-calc-input-wrapper">
                    <span class="re-calc-currency-symbol">$</span>
                    <input type="text" id="reCalcOtherFees" placeholder="0" value="0">
                </div>
                <p class="re-calc-helper-text">Home warranty, repairs, staging, etc.</p>
            </div>
        </div>

        <div class="re-calc-results-section">
            <h3>Your Net Proceeds Breakdown</h3>

            <div class="re-calc-result-item re-calc-gross-sale">
                <span class="label">Gross Sale Price</span>
                <span class="value" id="reCalcGrossSale">$500,000</span>
            </div>

            <div class="re-calc-deductions">
                <h4>Deductions:</h4>

                <div class="re-calc-result-item re-calc-agent-commission">
                    <div class="re-calc-commission-header">
                        <span class="label">
                            <strong>Real Estate Agent Commission</strong>
                            <span class="re-calc-commission-percentage" id="reCalcCommissionPercentage">(6.0%)</span>
                        </span>
                        <span class="value negative" id="reCalcAgentCommission">-$30,000</span>
                    </div>
                    <div class="re-calc-commission-warning">
                        💡 This is what goes to your agent(s) - not to you!
                    </div>
                </div>

                <div class="re-calc-result-item">
                    <span class="label">Mortgage Payoff</span>
                    <span class="value negative" id="reCalcMortgagePayoff">-$300,000</span>
                </div>

                <div class="re-calc-result-item">
                    <span class="label">Closing Costs</span>
                    <span class="value negative" id="reCalcClosingCostsDisplay">-$5,000</span>
                </div>

                <div class="re-calc-result-item" id="reCalcOtherFeesRow">
                    <span class="label">Other Fees</span>
                    <span class="value negative" id="reCalcOtherFeesDisplay">$0</span>
                </div>
            </div>

            <div class="re-calc-result-item re-calc-net-proceeds">
                <span class="label">Your Net Proceeds</span>
                <span class="value" id="reCalcNetProceeds">$165,000</span>
            </div>

            <div class="re-calc-visual-breakdown">
                <h4>Where Your Money Goes:</h4>
                <div class="re-calc-breakdown-bar">
                    <div class="re-calc-bar-segment re-calc-agent-segment" id="reCalcAgentBar">
                        <span class="re-calc-bar-label">Agent</span>
                        <span class="re-calc-bar-percentage" id="reCalcAgentPercent">6%</span>
                    </div>
                    <div class="re-calc-bar-segment re-calc-mortgage-segment" id="reCalcMortgageBar">
                        <span class="re-calc-bar-label">Mortgage</span>
                        <span class="re-calc-bar-percentage" id="reCalcMortgagePercent">60%</span>
                    </div>
                    <div class="re-calc-bar-segment re-calc-costs-segment" id="reCalcCostsBar">
                        <span class="re-calc-bar-label">Costs</span>
                        <span class="re-calc-bar-percentage" id="reCalcCostsPercent">1%</span>
                    </div>
                    <div class="re-calc-bar-segment re-calc-proceeds-segment" id="reCalcProceedsBar">
                        <span class="re-calc-bar-label">You Keep</span>
                        <span class="re-calc-bar-percentage" id="reCalcProceedsPercent">33%</span>
                    </div>
                </div>
                <div class="re-calc-breakdown-legend">
                    <div class="re-calc-legend-item">
                        <span class="re-calc-legend-color re-calc-agent-color"></span>
                        <span>Agent Commission</span>
                    </div>
                    <div class="re-calc-legend-item">
                        <span class="re-calc-legend-color re-calc-mortgage-color"></span>
                        <span>Mortgage Payoff</span>
                    </div>
                    <div class="re-calc-legend-item">
                        <span class="re-calc-legend-color re-calc-costs-color"></span>
                        <span>Fees & Costs</span>
                    </div>
                    <div class="re-calc-legend-item">
                        <span class="re-calc-legend-color re-calc-proceeds-color"></span>
                        <span>Your Net Proceeds</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
(function() {
    function formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }

    function formatNumber(value) {
        return new Intl.NumberFormat('en-US').format(value);
    }

    function parseCurrency(value) {
        if (typeof value === 'number') return value;
        const cleaned = String(value).replace(/[$,]/g, '').trim();
        const parsed = parseFloat(cleaned);
        return isNaN(parsed) ? 0 : parsed;
    }

    function calculate() {
        const salePrice = parseCurrency(document.getElementById('reCalcSalePrice').value);
        const commissionRate = parseFloat(document.getElementById('reCalcCommissionRate').value);
        const mortgageBalance = parseCurrency(document.getElementById('reCalcMortgageBalance').value);
        const closingCosts = parseCurrency(document.getElementById('reCalcClosingCosts').value);
        const otherFees = parseCurrency(document.getElementById('reCalcOtherFees').value);

        if (salePrice <= 0) return;

        const agentCommission = salePrice * (commissionRate / 100);
        const totalDeductions = agentCommission + mortgageBalance + closingCosts + otherFees;
        const netProceeds = salePrice - totalDeductions;

        document.getElementById('reCalcGrossSale').textContent = formatCurrency(salePrice);
        document.getElementById('reCalcAgentCommission').textContent = '-' + formatCurrency(agentCommission);
        document.getElementById('reCalcCommissionPercentage').textContent = `(${commissionRate.toFixed(1)}%)`;
        document.getElementById('reCalcMortgagePayoff').textContent = '-' + formatCurrency(mortgageBalance);
        document.getElementById('reCalcClosingCostsDisplay').textContent = '-' + formatCurrency(closingCosts);
        document.getElementById('reCalcOtherFeesDisplay').textContent = otherFees > 0 ? '-' + formatCurrency(otherFees) : '$0';
        document.getElementById('reCalcNetProceeds').textContent = formatCurrency(Math.max(0, netProceeds));

        const otherFeesRow = document.getElementById('reCalcOtherFeesRow');
        if (otherFees > 0) {
            otherFeesRow.classList.remove('hidden');
        } else {
            otherFeesRow.classList.add('hidden');
        }

        updateVisualBreakdown(salePrice, agentCommission, mortgageBalance, closingCosts, otherFees, netProceeds);
    }

    function updateVisualBreakdown(salePrice, agentCommission, mortgageBalance, closingCosts, otherFees, netProceeds) {
        const agentPercent = (agentCommission / salePrice) * 100;
        const mortgagePercent = (mortgageBalance / salePrice) * 100;
        const totalCosts = closingCosts + otherFees;
        const costsPercent = (totalCosts / salePrice) * 100;
        const proceedsPercent = Math.max(0, (netProceeds / salePrice) * 100);

        document.getElementById('reCalcAgentBar').style.width = agentPercent + '%';
        document.getElementById('reCalcMortgageBar').style.width = mortgagePercent + '%';
        document.getElementById('reCalcCostsBar').style.width = costsPercent + '%';
        document.getElementById('reCalcProceedsBar').style.width = proceedsPercent + '%';

        document.getElementById('reCalcAgentPercent').textContent = agentPercent.toFixed(1) + '%';
        document.getElementById('reCalcMortgagePercent').textContent = mortgagePercent.toFixed(1) + '%';
        document.getElementById('reCalcCostsPercent').textContent = costsPercent.toFixed(1) + '%';
        document.getElementById('reCalcProceedsPercent').textContent = proceedsPercent.toFixed(1) + '%';

        const minPercent = 3;
        [
            ['reCalcAgentBar', agentPercent],
            ['reCalcMortgageBar', mortgagePercent],
            ['reCalcCostsBar', costsPercent],
            ['reCalcProceedsBar', proceedsPercent]
        ].forEach(function(item) {
            const bar = document.getElementById(item[0]);
            const display = item[1] >= minPercent ? 'block' : 'none';
            bar.querySelector('.re-calc-bar-label').style.display = display;
            bar.querySelector('.re-calc-bar-percentage').style.display = display;
        });
    }

    function formatInputOnBlur(inputElement) {
        const value = parseCurrency(inputElement.value);
        if (value > 0) {
            inputElement.value = formatNumber(value);
        }
    }

    function removeFormatOnFocus(inputElement) {
        const value = parseCurrency(inputElement.value);
        if (value > 0) {
            inputElement.value = value;
        }
    }

    function updateCommissionDisplay() {
        const rate = document.getElementById('reCalcCommissionRate').value;
        document.getElementById('reCalcCommissionDisplay').textContent = parseFloat(rate).toFixed(1);
        calculate();
    }

    function init() {
        const salePriceInput = document.getElementById('reCalcSalePrice');
        const commissionRateInput = document.getElementById('reCalcCommissionRate');
        const mortgageBalanceInput = document.getElementById('reCalcMortgageBalance');
        const closingCostsInput = document.getElementById('reCalcClosingCosts');
        const otherFeesInput = document.getElementById('reCalcOtherFees');

        salePriceInput.addEventListener('input', calculate);
        commissionRateInput.addEventListener('input', updateCommissionDisplay);
        mortgageBalanceInput.addEventListener('input', calculate);
        closingCostsInput.addEventListener('input', calculate);
        otherFeesInput.addEventListener('input', calculate);

        [salePriceInput, mortgageBalanceInput, closingCostsInput, otherFeesInput].forEach(function(input) {
            input.addEventListener('focus', function() {
                removeFormatOnFocus(this);
            });

            input.addEventListener('blur', function() {
                formatInputOnBlur(this);
                calculate();
            });

            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    this.blur();
                }
            });
        });

        calculate();

        [salePriceInput, mortgageBalanceInput, closingCostsInput, otherFeesInput].forEach(function(input) {
            formatInputOnBlur(input);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
</script>
