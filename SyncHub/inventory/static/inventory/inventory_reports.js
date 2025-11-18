/* eslint-disable */
// Chart.js for items added visualization (by date)
const itemsCanvas = document.getElementById('itemsChart');
const dates = JSON.parse(itemsCanvas.dataset.dates);
const itemsCount = JSON.parse(itemsCanvas.dataset.items);
const totalQuantitiesList = JSON.parse(itemsCanvas.dataset.quantities);

if (dates && dates.length > 0) {
    const ctx = itemsCanvas.getContext('2d');
    const itemsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'Items Added',
                data: itemsCount,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                yAxisID: 'y'
            }, {
                label: 'Total Quantity',
                data: totalQuantitiesList,
                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.datasetIndex === 0) {
                                label += context.parsed.y + ' items';
                            } else {
                                label += context.parsed.y + ' quantity';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Number of Items'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Total Quantity'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

// Second chart: Total quantity per item
const itemQuantitiesCanvas = document.getElementById('itemQuantitiesChart');
const itemNames = JSON.parse(itemQuantitiesCanvas.dataset.names);
const itemTotalQuantities = JSON.parse(itemQuantitiesCanvas.dataset.quantities);

if (itemNames && itemNames.length > 0) {
    const ctx2 = itemQuantitiesCanvas.getContext('2d');
    const itemQuantitiesChart = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: itemNames,
            datasets: [{
                label: 'Total Quantity',
                data: itemTotalQuantities,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y + ' quantity';
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Total Quantity'
                    }
                }
            }
        }
    });
}
/* eslint-enable */
