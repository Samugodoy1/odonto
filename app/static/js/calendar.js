// Calendar functionality for appointment management
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('calendar')) {
        initializeCalendar();
    }
});

function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    
    // Get current date from URL or use today
    const urlParams = new URLSearchParams(window.location.search);
    const currentDateStr = urlParams.get('data');
    
    let currentDate;
    if (currentDateStr) {
        // Parse YYYY-MM-DD from URL
        const parts = currentDateStr.split('-');
        currentDate = new Date(parts[0], parts[1] - 1, parts[2]); // Month is 0-based in JS
    } else {
        currentDate = new Date();
    }
    
    // Ensure the date is valid
    if (isNaN(currentDate.getTime())) {
        currentDate = new Date();
    }
    
    // Build a simple monthly calendar
    buildMonthlyCalendar(calendarEl, currentDate);
}

function buildMonthlyCalendar(container, date) {
    // Clear the container
    container.innerHTML = '';
    
    // Get the year and month
    const year = date.getFullYear();
    const month = date.getMonth(); // 0-based month
    
    // Get the first day of the month
    const firstDay = new Date(year, month, 1).getDay(); // 0 (Sunday) to 6 (Saturday)
    
    // Get the number of days in the month
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    // Month names
    const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    
    // Create month header
    const header = document.createElement('div');
    header.className = 'd-flex justify-content-between align-items-center mb-3';
    
    const prevMonthBtn = document.createElement('button');
    prevMonthBtn.className = 'btn btn-sm btn-outline-secondary';
    prevMonthBtn.innerHTML = '<i class="bi bi-chevron-left"></i> Mês Anterior';
    prevMonthBtn.addEventListener('click', function() {
        const prevMonth = new Date(year, month - 1, 1);
        buildMonthlyCalendar(container, prevMonth);
    });
    
    const monthTitle = document.createElement('h5');
    monthTitle.className = 'mb-0';
    monthTitle.textContent = `${monthNames[month]} ${year}`;
    
    const nextMonthBtn = document.createElement('button');
    nextMonthBtn.className = 'btn btn-sm btn-outline-secondary';
    nextMonthBtn.innerHTML = 'Próximo Mês <i class="bi bi-chevron-right"></i>';
    nextMonthBtn.addEventListener('click', function() {
        const nextMonth = new Date(year, month + 1, 1);
        buildMonthlyCalendar(container, nextMonth);
    });
    
    header.appendChild(prevMonthBtn);
    header.appendChild(monthTitle);
    header.appendChild(nextMonthBtn);
    
    container.appendChild(header);
    
    // Create the table for the calendar
    const table = document.createElement('table');
    table.className = 'table table-bordered';
    
    // Create table header with day names
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    const dayNames = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    
    dayNames.forEach(day => {
        const th = document.createElement('th');
        th.className = 'text-center';
        th.textContent = day;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body with dates
    const tbody = document.createElement('tbody');
    
    let day = 1;
    const today = new Date();
    
    // Create weeks until all days of the month are rendered
    for (let i = 0; i < 6; i++) {
        if (day > daysInMonth) break;
        
        const row = document.createElement('tr');
        
        // Create days of the week
        for (let j = 0; j < 7; j++) {
            const cell = document.createElement('td');
            cell.style.height = '80px';
            cell.style.width = '14.28%';
            cell.className = 'position-relative';
            
            if ((i === 0 && j < firstDay) || day > daysInMonth) {
                // Empty cell before the first day or after the last day
                cell.className += ' text-muted bg-light bg-opacity-10';
            } else {
                // Valid date cell
                const currentDate = new Date(year, month, day);
                const dateLink = document.createElement('a');
                dateLink.href = `/agendamentos?data=${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                dateLink.className = 'position-absolute top-0 end-0 p-2';
                
                // Highlight current date
                if (currentDate.toDateString() === today.toDateString()) {
                    dateLink.className += ' fw-bold text-primary';
                }
                
                dateLink.textContent = day;
                cell.appendChild(dateLink);
                
                // Add event indicators (these would come from real data in production)
                if (Math.random() > 0.7) { // Just random data for visual representation
                    const eventCount = Math.floor(Math.random() * 5) + 1;
                    const eventIndicator = document.createElement('div');
                    eventIndicator.className = 'position-absolute bottom-0 start-0 end-0 p-1';
                    eventIndicator.innerHTML = `<span class="badge bg-primary">${eventCount} consultas</span>`;
                    cell.appendChild(eventIndicator);
                }
                
                day++;
            }
            
            row.appendChild(cell);
        }
        
        tbody.appendChild(row);
    }
    
    table.appendChild(tbody);
    container.appendChild(table);
}
