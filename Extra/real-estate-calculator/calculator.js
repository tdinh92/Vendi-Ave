// Real Estate Commission Calculator - JavaScript Logic

// Format number as currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Format number with commas
function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

// Parse currency input (remove $ and commas)
function parseCurrency(value) {
    if (typeof value === 'number') return value;
    const cleaned = String(value).replace(/[$,]/g, '').trim();
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? 0 : parsed;
}

// Calculate and update all results
function calculate() {
    // Get input values
    const salePrice = parseCurrency(document.getElementById('salePrice').value);
    const commissionRate = parseFloat(document.getElementById('commissionRate').value);
    const mortgageBalance = parseCurrency(document.getElementById('mortgageBalance').value);
    const closingCosts = parseCurrency(document.getElementById('closingCosts').value);
    const otherFees = parseCurrency(document.getElementById('otherFees').value);

    // Validate sale price
    if (salePrice <= 0) {
        console.warn('Sale price must be greater than 0');
        return;
    }

    // Calculate deductions
    const agentCommission = salePrice * (commissionRate / 100);
    const totalDeductions = agentCommission + mortgageBalance + closingCosts + otherFees;
    const netProceeds = salePrice - totalDeductions;

    // Update results display
    document.getElementById('grossSale').textContent = formatCurrency(salePrice);
    document.getElementById('agentCommission').textContent = '-' + formatCurrency(agentCommission);
    document.getElementById('commissionPercentage').textContent = `(${commissionRate.toFixed(1)}%)`;
    document.getElementById('mortgagePayoff').textContent = '-' + formatCurrency(mortgageBalance);
    document.getElementById('closingCostsDisplay').textContent = '-' + formatCurrency(closingCosts);
    document.getElementById('otherFeesDisplay').textContent = otherFees > 0 ? '-' + formatCurrency(otherFees) : '$0';
    document.getElementById('netProceeds').textContent = formatCurrency(Math.max(0, netProceeds));

    // Show/hide other fees row
    const otherFeesRow = document.getElementById('otherFeesRow');
    if (otherFees > 0) {
        otherFeesRow.classList.remove('hidden');
    } else {
        otherFeesRow.classList.add('hidden');
    }

    // Update visual breakdown
    updateVisualBreakdown(salePrice, agentCommission, mortgageBalance, closingCosts, otherFees, netProceeds);
}

// Update the visual breakdown bar chart
function updateVisualBreakdown(salePrice, agentCommission, mortgageBalance, closingCosts, otherFees, netProceeds) {
    // Calculate percentages
    const agentPercent = (agentCommission / salePrice) * 100;
    const mortgagePercent = (mortgageBalance / salePrice) * 100;
    const totalCosts = closingCosts + otherFees;
    const costsPercent = (totalCosts / salePrice) * 100;
    const proceedsPercent = Math.max(0, (netProceeds / salePrice) * 100);

    // Update bar widths
    document.getElementById('agentBar').style.width = agentPercent + '%';
    document.getElementById('mortgageBar').style.width = mortgagePercent + '%';
    document.getElementById('costsBar').style.width = costsPercent + '%';
    document.getElementById('proceedsBar').style.width = proceedsPercent + '%';

    // Update percentage labels
    document.getElementById('agentPercent').textContent = agentPercent.toFixed(1) + '%';
    document.getElementById('mortgagePercent').textContent = mortgagePercent.toFixed(1) + '%';
    document.getElementById('costsPercent').textContent = costsPercent.toFixed(1) + '%';
    document.getElementById('proceedsPercent').textContent = proceedsPercent.toFixed(1) + '%';

    // Hide segments that are too small to display
    const minPercent = 3; // Minimum percentage to show label

    if (agentPercent < minPercent) {
        document.getElementById('agentBar').querySelector('.bar-label').style.display = 'none';
        document.getElementById('agentBar').querySelector('.bar-percentage').style.display = 'none';
    } else {
        document.getElementById('agentBar').querySelector('.bar-label').style.display = 'block';
        document.getElementById('agentBar').querySelector('.bar-percentage').style.display = 'block';
    }

    if (mortgagePercent < minPercent) {
        document.getElementById('mortgageBar').querySelector('.bar-label').style.display = 'none';
        document.getElementById('mortgageBar').querySelector('.bar-percentage').style.display = 'none';
    } else {
        document.getElementById('mortgageBar').querySelector('.bar-label').style.display = 'block';
        document.getElementById('mortgageBar').querySelector('.bar-percentage').style.display = 'block';
    }

    if (costsPercent < minPercent) {
        document.getElementById('costsBar').querySelector('.bar-label').style.display = 'none';
        document.getElementById('costsBar').querySelector('.bar-percentage').style.display = 'none';
    } else {
        document.getElementById('costsBar').querySelector('.bar-label').style.display = 'block';
        document.getElementById('costsBar').querySelector('.bar-percentage').style.display = 'block';
    }

    if (proceedsPercent < minPercent) {
        document.getElementById('proceedsBar').querySelector('.bar-label').style.display = 'none';
        document.getElementById('proceedsBar').querySelector('.bar-percentage').style.display = 'none';
    } else {
        document.getElementById('proceedsBar').querySelector('.bar-label').style.display = 'block';
        document.getElementById('proceedsBar').querySelector('.bar-percentage').style.display = 'block';
    }
}

// Format input fields with commas on blur
function formatInputOnBlur(inputElement) {
    const value = parseCurrency(inputElement.value);
    if (value > 0) {
        inputElement.value = formatNumber(value);
    }
}

// Remove formatting when focusing (for easier editing)
function removeFormatOnFocus(inputElement) {
    const value = parseCurrency(inputElement.value);
    if (value > 0) {
        inputElement.value = value;
    }
}

// Update commission rate display
function updateCommissionDisplay() {
    const rate = document.getElementById('commissionRate').value;
    document.getElementById('commissionDisplay').textContent = parseFloat(rate).toFixed(1);
    calculate();
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get all input elements
    const salePriceInput = document.getElementById('salePrice');
    const commissionRateInput = document.getElementById('commissionRate');
    const mortgageBalanceInput = document.getElementById('mortgageBalance');
    const closingCostsInput = document.getElementById('closingCosts');
    const otherFeesInput = document.getElementById('otherFees');

    // Add event listeners for real-time calculation
    salePriceInput.addEventListener('input', calculate);
    commissionRateInput.addEventListener('input', updateCommissionDisplay);
    mortgageBalanceInput.addEventListener('input', calculate);
    closingCostsInput.addEventListener('input', calculate);
    otherFeesInput.addEventListener('input', calculate);

    // Add formatting event listeners
    [salePriceInput, mortgageBalanceInput, closingCostsInput, otherFeesInput].forEach(input => {
        input.addEventListener('focus', function() {
            removeFormatOnFocus(this);
        });

        input.addEventListener('blur', function() {
            formatInputOnBlur(this);
            calculate();
        });

        // Handle enter key
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                this.blur();
            }
        });
    });

    // Initial calculation with default values
    calculate();

    // Format initial values
    [salePriceInput, mortgageBalanceInput, closingCostsInput, otherFeesInput].forEach(input => {
        formatInputOnBlur(input);
    });
});

// Export functions for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatCurrency,
        formatNumber,
        parseCurrency,
        calculate
    };
}
