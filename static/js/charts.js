// Chart initializations for NearShop Dashboard using Chart.js

// Global Chart configurations
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'Inter', system-ui, -apple-system, sans-serif";
    Chart.defaults.color = '#64748b';
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(30, 41, 59, 0.9)';
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
}

/**
 * Initialize a line chart showing stock trends over time
 */
window.initStockTrendChart = function(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (!data || !data.labels || data.labels.length === 0) {
        showNoDataMessage(ctx);
        return;
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Stock Level',
                data: data.values,
                borderColor: '#1a56db',
                backgroundColor: 'rgba(26, 86, 219, 0.1)',
                borderWidth: 2,
                tension: 0.4, // Smooth curve
                fill: true,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: '#1a56db',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Stock: ${context.parsed.y} units`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#e2e8f0', drawBorder: false }
                },
                x: {
                    grid: { display: false, drawBorder: false }
                }
            },
            animation: { duration: 1000, easing: 'easeOutQuart' }
        }
    });
};

/**
 * Initialize a horizontal bar chart for top products
 */
window.initTopProductsChart = function(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (!data || !data.labels || data.labels.length === 0) {
        showNoDataMessage(ctx);
        return;
    }

    // Create gradient
    const chartCtx = ctx.getContext('2d');
    const gradient = chartCtx.createLinearGradient(0, 0, 400, 0);
    gradient.addColorStop(0, '#1a56db');
    gradient.addColorStop(1, '#4f46e5');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Searches',
                data: data.values,
                backgroundColor: gradient,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            indexAxis: 'y', // Horizontal bar
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Searches: ${context.parsed.x}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: '#e2e8f0', drawBorder: false }
                },
                y: {
                    grid: { display: false, drawBorder: false }
                }
            },
            animation: { duration: 1000, easing: 'easeOutQuart' }
        }
    });
};

/**
 * Initialize a doughnut chart for category distribution
 */
window.initCategoryPieChart = function(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (!data || !data.labels || data.labels.length === 0) {
        showNoDataMessage(ctx);
        return;
    }

    const colors = [
        '#1a56db', '#16a34a', '#f59e0b', '#ef4444', 
        '#8b5cf6', '#ec4899', '#06b6d4', '#14b8a6', '#6366f1'
    ];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: colors.slice(0, data.labels.length),
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 20, usePointStyle: true }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100) + '%';
                            return `${label}: ${value} (${percentage})`;
                        }
                    }
                }
            },
            cutout: '70%',
            animation: { animateScale: true, animateRotate: true }
        }
    });
};

/**
 * Initialize a line chart showing price trends
 */
window.initPriceTrendChart = function(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (!data || !data.labels || data.labels.length === 0) {
        showNoDataMessage(ctx);
        return;
    }

    // Calculate average for average line
    const avg = data.values.reduce((a, b) => a + b, 0) / data.values.length;
    const avgData = Array(data.labels.length).fill(avg);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Actual Price',
                    data: data.values,
                    borderColor: '#1a56db',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    tension: 0.1,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#1a56db',
                    pointRadius: 4
                },
                {
                    label: 'Average Price',
                    data: avgData,
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false,
                    tension: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ₹${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) { return '₹' + value; }
                    },
                    grid: { color: '#e2e8f0', drawBorder: false }
                },
                x: {
                    grid: { display: false, drawBorder: false }
                }
            }
        }
    });
};

/**
 * Initialize a bar chart showing search trends over time
 */
window.initSearchTrendChart = function(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (!data || !data.labels || data.labels.length === 0) {
        showNoDataMessage(ctx);
        return;
    }

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Searches',
                data: data.values,
                backgroundColor: '#16a34a',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#e2e8f0', drawBorder: false }
                },
                x: {
                    grid: { display: false, drawBorder: false }
                }
            }
        }
    });
};

/**
 * Helper to display a 'No data available' message on the canvas
 */
function showNoDataMessage(canvasElement) {
    const ctx = canvasElement.getContext('2d');
    ctx.font = '14px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#64748b';
    ctx.fillText('No data available', canvasElement.width / 2, canvasElement.height / 2);
}
