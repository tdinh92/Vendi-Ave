/**
 * Property Assessment Charts Library
 * Easy-to-use JavaScript library for embedding property assessment history charts
 * 
 * Dependencies: D3.js v7
 * 
 * Usage:
 * const charts = new AssessmentCharts({
 *   apiBaseUrl: 'http://localhost:5000',
 *   containerId: 'charts-container'
 * });
 * charts.loadCharts('4 Fiorenza Drive, Wilmington, MA 01887');
 */

class AssessmentCharts {
    constructor(config = {}) {
        this.config = {
            apiBaseUrl: config.apiBaseUrl || 'http://localhost:5000',
            containerId: config.containerId || 'assessment-charts',
            width: config.width || 800,
            height: config.height || 400,
            margin: config.margin || { top: 20, right: 50, bottom: 70, left: 80 },
            colors: config.colors || {
                assessment: '#2E8B57',
                tax: '#DC143C',
                sqft: '#4169E1'
            }
        };

        this.container = document.getElementById(this.config.containerId);
        if (!this.container) {
            throw new Error(`Container element with ID '${this.config.containerId}' not found`);
        }

        this.initializeContainer();
        this.initializeTooltip();
    }

    initializeContainer() {
        this.container.innerHTML = `
            <div class="assessment-charts-wrapper" style="font-family: Arial, sans-serif;">
                <div class="loading" style="display: none; text-align: center; padding: 50px; color: #666;">
                    Loading assessment data...
                </div>
                
                <div class="error" style="display: none; color: #dc3545; background: #f8d7da; padding: 15px; border-radius: 4px; margin: 20px 0;">
                </div>
                
                <div class="property-info" style="display: none; background: #e7f3ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 class="property-address" style="margin: 0 0 10px 0;"></h3>
                    <p class="property-details" style="margin: 0; color: #666;"></p>
                </div>
                
                <div class="chart-container assessment-chart" style="display: none; margin: 30px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                    <div class="chart-title" style="font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #333;">
                        Total Assessed Value Over Time
                    </div>
                    <svg class="chart" id="assessment-svg"></svg>
                    <div class="legend" style="display: flex; justify-content: center; gap: 30px; margin-top: 15px; font-size: 14px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 20px; height: 3px; background: ${this.config.colors.assessment};"></div>
                            <span>Assessed Value</span>
                        </div>
                    </div>
                </div>
                
                <div class="chart-container tax-chart" style="display: none; margin: 30px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                    <div class="chart-title" style="font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #333;">
                        Annual Property Tax Over Time
                    </div>
                    <svg class="chart" id="tax-svg"></svg>
                    <div class="legend" style="display: flex; justify-content: center; gap: 30px; margin-top: 15px; font-size: 14px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 20px; height: 3px; background: ${this.config.colors.tax};"></div>
                            <span>Annual Tax</span>
                        </div>
                    </div>
                </div>
                
                <div class="chart-container sqft-chart" style="display: none; margin: 30px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                    <div class="chart-title" style="font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #333;">
                        Assessed Value Per Square Foot Over Time
                    </div>
                    <svg class="chart" id="sqft-svg"></svg>
                    <div class="legend" style="display: flex; justify-content: center; gap: 30px; margin-top: 15px; font-size: 14px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 20px; height: 3px; background: ${this.config.colors.sqft};"></div>
                            <span>Value per Sq Ft</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Get element references
        this.elements = {
            loading: this.container.querySelector('.loading'),
            error: this.container.querySelector('.error'),
            propertyInfo: this.container.querySelector('.property-info'),
            propertyAddress: this.container.querySelector('.property-address'),
            propertyDetails: this.container.querySelector('.property-details'),
            assessmentChart: this.container.querySelector('.assessment-chart'),
            taxChart: this.container.querySelector('.tax-chart'),
            sqftChart: this.container.querySelector('.sqft-chart')
        };
    }

    initializeTooltip() {
        if (!document.querySelector('.assessment-charts-tooltip')) {
            const tooltip = document.createElement('div');
            tooltip.className = 'assessment-charts-tooltip';
            tooltip.style.cssText = `
                position: absolute;
                padding: 8px 12px;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                border-radius: 4px;
                font-size: 12px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s;
                z-index: 1000;
            `;
            document.body.appendChild(tooltip);
        }
        this.tooltip = document.querySelector('.assessment-charts-tooltip');
    }

    async loadCharts(address) {
        if (!address) {
            this.showError('Please provide a property address');
            return;
        }

        this.showLoading(true);
        this.hideError();
        this.hideCharts();

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/property/assessmenthistory`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ address: address })
            });

            const data = await response.json();
            
            if (!response.ok || data.error) {
                throw new Error(data.error || 'Failed to fetch data');
            }

            if (!data.assessments || data.assessments.length === 0) {
                throw new Error('No assessment history found for this address');
            }

            // Show property info
            this.showPropertyInfo(data);

            // Process data for charts
            const chartData = this.processAssessmentData(data.assessments);
            
            // Create all three charts
            this.createAssessmentChart(chartData);
            this.createTaxChart(chartData);
            this.createSqftChart(chartData);
            
            this.showCharts();
            
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.showLoading(false);
        }
    }

    processAssessmentData(assessments) {
        return assessments.map(d => ({
            year: +d.tax_year,
            assessedValue: d.raw_total_assessed,
            taxAmount: d.raw_tax_amount,
            valuePerSqft: d.raw_assessed_per_sqft,
            assessedValueFormatted: d.total_assessed_value,
            taxAmountFormatted: d.tax_amount,
            valuePerSqftFormatted: d.assessed_per_sqft
        })).sort((a, b) => a.year - b.year);
    }

    createAssessmentChart(data) {
        this.createLineChart({
            data: data,
            svgSelector: '#assessment-svg',
            yAccessor: d => d.assessedValue,
            color: this.config.colors.assessment,
            yLabel: 'Assessed Value ($)',
            formatValue: d3.format('$,.0f'),
            tooltipLabel: 'Assessed Value'
        });
    }

    createTaxChart(data) {
        this.createLineChart({
            data: data,
            svgSelector: '#tax-svg',
            yAccessor: d => d.taxAmount,
            color: this.config.colors.tax,
            yLabel: 'Annual Tax ($)',
            formatValue: d3.format('$,.0f'),
            tooltipLabel: 'Annual Tax'
        });
    }

    createSqftChart(data) {
        this.createLineChart({
            data: data,
            svgSelector: '#sqft-svg',
            yAccessor: d => d.valuePerSqft,
            color: this.config.colors.sqft,
            yLabel: 'Value per Sq Ft ($)',
            formatValue: d3.format('$,.2f'),
            tooltipLabel: 'Value per Sq Ft'
        });
    }

    createLineChart({ data, svgSelector, yAccessor, color, yLabel, formatValue, tooltipLabel }) {
        const margin = this.config.margin;
        const width = this.config.width - margin.left - margin.right;
        const height = this.config.height - margin.top - margin.bottom;

        const svg = d3.select(svgSelector);
        svg.selectAll("*").remove();
        svg.attr('width', this.config.width).attr('height', this.config.height);
        
        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Scales
        const xScale = d3.scaleLinear()
            .domain(d3.extent(data, d => d.year))
            .range([0, width]);

        const yScale = d3.scaleLinear()
            .domain([0, d3.max(data, yAccessor) * 1.1])
            .range([height, 0]);

        // Line generator
        const line = d3.line()
            .x(d => xScale(d.year))
            .y(d => yScale(yAccessor(d)))
            .curve(d3.curveMonotoneX);

        // Add axes
        g.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale).tickFormat(d3.format('d')))
            .style('font-size', '12px');

        g.append('g')
            .call(d3.axisLeft(yScale).tickFormat(formatValue))
            .style('font-size', '12px');

        // Add axis labels
        g.append('text')
            .attr('x', width / 2)
            .attr('y', height + 50)
            .style('text-anchor', 'middle')
            .style('font-size', '14px')
            .text('Year');

        g.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('y', -60)
            .attr('x', -height / 2)
            .style('text-anchor', 'middle')
            .style('font-size', '14px')
            .text(yLabel);

        // Add line
        g.append('path')
            .datum(data)
            .attr('fill', 'none')
            .attr('stroke', color)
            .attr('stroke-width', 3)
            .attr('d', line);

        // Add dots
        const tooltip = this.tooltip;
        g.selectAll('.dot')
            .data(data)
            .enter().append('circle')
            .attr('r', 4)
            .attr('fill', color)
            .attr('stroke', 'white')
            .attr('stroke-width', 2)
            .attr('cx', d => xScale(d.year))
            .attr('cy', d => yScale(yAccessor(d)))
            .on('mouseover', function(event, d) {
                tooltip.style.opacity = '1';
                tooltip.innerHTML = `Year: ${d.year}<br/>${tooltipLabel}: ${formatValue(yAccessor(d))}`;
                tooltip.style.left = (event.pageX + 10) + 'px';
                tooltip.style.top = (event.pageY - 10) + 'px';
            })
            .on('mouseout', function() {
                tooltip.style.opacity = '0';
            });
    }

    showLoading(show) {
        this.elements.loading.style.display = show ? 'block' : 'none';
    }

    showError(message) {
        this.elements.error.textContent = message;
        this.elements.error.style.display = 'block';
    }

    hideError() {
        this.elements.error.style.display = 'none';
    }

    showPropertyInfo(data) {
        this.elements.propertyAddress.textContent = data.address;
        this.elements.propertyDetails.textContent = 
            `${data.total_assessments} assessment records spanning ${data.assessment_years[data.assessment_years.length-1]} - ${data.assessment_years[0]}`;
        this.elements.propertyInfo.style.display = 'block';
    }

    showCharts() {
        this.elements.assessmentChart.style.display = 'block';
        this.elements.taxChart.style.display = 'block';
        this.elements.sqftChart.style.display = 'block';
    }

    hideCharts() {
        this.elements.assessmentChart.style.display = 'none';
        this.elements.taxChart.style.display = 'none';
        this.elements.sqftChart.style.display = 'none';
        this.elements.propertyInfo.style.display = 'none';
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AssessmentCharts;
}

// Make available globally
if (typeof window !== 'undefined') {
    window.AssessmentCharts = AssessmentCharts;
}