// Dashboard Charts and Visualizations

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts if their containers exist
    if (document.getElementById('consultasChart')) {
        initConsultasChart();
    }
    
    if (document.getElementById('pacientesChart')) {
        initPacientesChart();
    }
});

// Initialize appointments chart
function initConsultasChart() {
    const ctx = document.getElementById('consultasChart').getContext('2d');
    
    // Use Chart.js to create a bar chart for appointments
    const consultasChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho'],
            datasets: [{
                label: 'Consultas Realizadas',
                data: [12, 19, 15, 17, 20, 25],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }, {
                label: 'Consultas Canceladas',
                data: [2, 3, 1, 4, 2, 3],
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Número de Consultas'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Mês'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Consultas por Mês'
                }
            }
        }
    });
}

// Initialize patients chart
function initPacientesChart() {
    const ctx = document.getElementById('pacientesChart').getContext('2d');
    
    // Use Chart.js to create a pie chart for patient demographics
    const pacientesChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['0-18 anos', '19-30 anos', '31-50 anos', '51-65 anos', '65+ anos'],
            datasets: [{
                data: [15, 25, 30, 20, 10],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'Distribuição de Pacientes por Idade'
                }
            }
        }
    });
}

// Function to update charts with server data
function updateChartsWithData(consultasData, pacientesData) {
    if (window.consultasChart && consultasData) {
        window.consultasChart.data.datasets[0].data = consultasData.realizadas;
        window.consultasChart.data.datasets[1].data = consultasData.canceladas;
        window.consultasChart.update();
    }
    
    if (window.pacientesChart && pacientesData) {
        window.pacientesChart.data.datasets[0].data = pacientesData.valores;
        window.pacientesChart.update();
    }
}

// Load chart data from API if available
function loadChartData() {
    // This would typically fetch data from an API endpoint
    // For now, we're using static demo data
    console.log('Loading chart data...');
    
    // Simulating API response with static data
    const consultasData = {
        realizadas: [12, 19, 15, 17, 20, 25],
        canceladas: [2, 3, 1, 4, 2, 3]
    };
    
    const pacientesData = {
        valores: [15, 25, 30, 20, 10]
    };
    
    updateChartsWithData(consultasData, pacientesData);
}
