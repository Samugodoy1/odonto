// Dashboard charts and statistics
document.addEventListener('DOMContentLoaded', function() {
    // If the charts container exists, initialize charts
    if (document.getElementById('appointmentsChart')) {
        initializeAppointmentsChart();
    }
    
    if (document.getElementById('patientsChart')) {
        initializePatientsChart();
    }
});

// Appointments by Status chart
function initializeAppointmentsChart() {
    const ctx = document.getElementById('appointmentsChart').getContext('2d');
    
    // We'll use dummy data here - in a real app, this would come from an API
    const appointmentsChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Agendadas', 'Concluídas', 'Canceladas', 'Faltas'],
            datasets: [{
                data: [40, 35, 15, 10],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(255, 206, 86, 0.7)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#eee'
                    }
                },
                title: {
                    display: true,
                    text: 'Distribuição de Status das Consultas',
                    color: '#eee'
                }
            }
        }
    });
}

// Patients by age group chart
function initializePatientsChart() {
    const ctx = document.getElementById('patientsChart').getContext('2d');
    
    // We'll use dummy data here - in a real app, this would come from an API
    const patientsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-18', '19-30', '31-45', '46-60', '61+'],
            datasets: [{
                label: 'Pacientes por Faixa Etária',
                data: [15, 30, 25, 20, 10],
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Pacientes por Faixa Etária',
                    color: '#eee'
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#eee'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#eee'
                    }
                }
            }
        }
    });
}
