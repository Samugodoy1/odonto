// Calendar and Appointment Management Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize calendar if container exists
    if (document.getElementById('calendar')) {
        initCalendar();
    }
    
    // Initialize appointment selectors
    initAppointmentTimeSelectors();
});

// Initialize calendar view
function initCalendar() {
    const calendarEl = document.getElementById('calendar');
    const currentDate = new Date();
    
    // Get the month and year for display
    const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    const monthYear = monthNames[currentDate.getMonth()] + ' ' + currentDate.getFullYear();
    
    // Set the calendar header
    const calendarHeader = document.getElementById('calendarMonthYear');
    if (calendarHeader) {
        calendarHeader.textContent = monthYear;
    }
    
    // Generate calendar days
    generateCalendarDays(calendarEl, currentDate);
    
    // Add event listeners for previous/next month buttons
    const prevMonthBtn = document.getElementById('prevMonth');
    const nextMonthBtn = document.getElementById('nextMonth');
    
    if (prevMonthBtn) {
        prevMonthBtn.addEventListener('click', function() {
            currentDate.setMonth(currentDate.getMonth() - 1);
            updateCalendar(calendarEl, currentDate);
        });
    }
    
    if (nextMonthBtn) {
        nextMonthBtn.addEventListener('click', function() {
            currentDate.setMonth(currentDate.getMonth() + 1);
            updateCalendar(calendarEl, currentDate);
        });
    }
}

// Generate calendar days for the given month
function generateCalendarDays(calendarEl, date) {
    // Clear existing calendar
    calendarEl.innerHTML = '';
    
    // Get the first day of the month
    const firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
    
    // Get the last day of the month
    const lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
    
    // Get the day of the week for the first day (0 = Sunday, 1 = Monday, etc.)
    let firstDayOfWeek = firstDay.getDay();
    
    // Adjust for Monday as the first day of the week
    if (firstDayOfWeek === 0) firstDayOfWeek = 7;
    
    // Create header row with day names
    const headerRow = document.createElement('div');
    headerRow.className = 'row mb-2';
    
    const dayNames = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
    
    for (let i = 0; i < 7; i++) {
        const dayHeader = document.createElement('div');
        dayHeader.className = 'col text-center calendar-day-header';
        dayHeader.textContent = dayNames[i];
        headerRow.appendChild(dayHeader);
    }
    
    calendarEl.appendChild(headerRow);
    
    // Create calendar grid
    let day = 1;
    const totalDays = lastDay.getDate();
    
    // Create weeks (rows)
    for (let i = 0; i < 6; i++) {
        const weekRow = document.createElement('div');
        weekRow.className = 'row mb-2';
        
        // Create days (columns)
        for (let j = 0; j < 7; j++) {
            const dayCol = document.createElement('div');
            dayCol.className = 'col calendar-day';
            
            // Add day number for valid days
            if ((i === 0 && j < firstDayOfWeek - 1) || day > totalDays) {
                // Empty cell
                dayCol.classList.add('bg-dark', 'opacity-25');
            } else {
                // Valid day
                const dayNumber = document.createElement('div');
                dayNumber.className = 'calendar-day-number';
                dayNumber.textContent = day;
                
                // Check if it's today
                const currentDate = new Date();
                if (day === currentDate.getDate() && 
                    date.getMonth() === currentDate.getMonth() && 
                    date.getFullYear() === currentDate.getFullYear()) {
                    dayNumber.classList.add('badge', 'bg-primary');
                }
                
                dayCol.appendChild(dayNumber);
                
                // Add day content container
                const dayContent = document.createElement('div');
                dayContent.className = 'calendar-day-content';
                
                // Here you would add appointments for this day
                // This is a placeholder for demonstration
                if (Math.random() > 0.7) {
                    const event = document.createElement('div');
                    event.className = 'calendar-event bg-primary text-white';
                    event.textContent = '09:00 - Consulta';
                    dayContent.appendChild(event);
                }
                
                if (Math.random() > 0.8) {
                    const event = document.createElement('div');
                    event.className = 'calendar-event bg-success text-white';
                    event.textContent = '15:30 - Retorno';
                    dayContent.appendChild(event);
                }
                
                dayCol.appendChild(dayContent);
                
                // Add click event to navigate to that day's appointments
                dayCol.style.cursor = 'pointer';
                dayCol.addEventListener('click', function() {
                    const selectedDate = new Date(date.getFullYear(), date.getMonth(), day);
                    const formattedDate = selectedDate.toISOString().split('T')[0]; // YYYY-MM-DD
                    window.location.href = '/agendamentos?data=' + formattedDate;
                });
                
                day++;
            }
            
            weekRow.appendChild(dayCol);
        }
        
        calendarEl.appendChild(weekRow);
        
        // Stop if we've displayed all days
        if (day > totalDays) break;
    }
}

// Update calendar for a new month
function updateCalendar(calendarEl, date) {
    // Update month/year display
    const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    const monthYear = monthNames[date.getMonth()] + ' ' + date.getFullYear();
    
    const calendarHeader = document.getElementById('calendarMonthYear');
    if (calendarHeader) {
        calendarHeader.textContent = monthYear;
    }
    
    // Regenerate calendar days
    generateCalendarDays(calendarEl, date);
}

// Initialize time selectors for appointment booking
function initAppointmentTimeSelectors() {
    const timeButtons = document.querySelectorAll('.time-slot-btn');
    
    timeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the time from the button's data attribute
            const time = this.getAttribute('data-time');
            
            // Update the time input field
            const timeInput = document.getElementById('hora_consulta');
            if (timeInput) {
                timeInput.value = time;
            }
            
            // Remove 'active' class from all buttons
            timeButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add 'active' class to this button
            this.classList.add('active');
        });
    });
}

// Function to check for schedule conflicts
function checkAppointmentConflicts(date, time) {
    // This would typically call an API endpoint to check for conflicts
    console.log(`Checking conflicts for: ${date} at ${time}`);
    
    // For demonstration purposes, simulate an API call with a promise
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            // Randomly determine if there's a conflict
            const hasConflict = Math.random() > 0.8;
            
            if (hasConflict) {
                reject({
                    conflict: true,
                    message: 'Já existe um agendamento para este horário.'
                });
            } else {
                resolve({
                    conflict: false,
                    message: 'Horário disponível.'
                });
            }
        }, 500);
    });
}
