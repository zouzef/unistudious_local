document.addEventListener('DOMContentLoaded', function() {
    var Calendar = FullCalendar.Calendar;

    // Get data attributes from the 'calendare' div
    var dataEl = document.getElementById('calendare');
    const sessionId = dataEl.dataset.sessionId;
    const roomId = dataEl.dataset.roomId;

    console.log('Session ID:', sessionId);
    console.log('Room ID:', roomId);

    // Add type mapping function
    function getTypeLabel(type) {
        const typeMap = {
            'p': 'Presence',
            'o': 'Online',
            'h': 'Hybrid',
            'a': 'Absence',
            // Add more mappings as needed
        };
        return typeMap[type] || type; // Return original if not found in map
    }

    // Initialize calendar on the 'calendar' div
    var calendarEl = document.getElementById('calendar');

    var calendar = new Calendar(calendarEl, {
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      initialDate: new Date(),
      navLinks: true,
      editable: true,
      droppable: true,
      dayMaxEvents: true,

      // Fetch events from your endpoint
      events: function(info, successCallback, failureCallback) {
        console.log('Fetching calendar events...');
        fetch(`/get-calendar-room/${roomId}`)
          .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
          })
          .then(data => {
            console.log('Calendar data received:', data);

            // Check for "Successfully got calendar room" message
            if (data.Message === "Successfully got calendar room" && data.Data) {
              // Transform your data to FullCalendar format
              const events = data.Data.map(item => ({
                id: item.id,
                title: item.title,
                start: item.start_time,
                end: item.end_time,
                backgroundColor: item.color,
                borderColor: item.color,
                extendedProps: {
                  description: item.description,
                  ref: item.ref,
                  sessionId: item.session_id,
                  groupSessionId: item.group_session_id,
                  teacherId: item.teacher_id,
                  subjectId: item.subject_id,
                  roomId: item.room_id,
                  status: item.status,
                  enabled: item.enabled,
                  type: item.type
                }
              }));
              console.log('Transformed events:', events);
              successCallback(events);
            } else {
              console.error('Failed to fetch events - unexpected response format');
              failureCallback(new Error('Failed to fetch events'));
            }
          })
          .catch(error => {
            console.error('Error fetching calendar events:', error);
            failureCallback(error);
          });
      },

      // Display event details in modal on click
      eventClick: function(info) {
        // Prevent the browser from navigating
        info.jsEvent.preventDefault();

        // Get event data
        const event = info.event;
        const startDate = event.start;
        const endDate = event.end;

        // Format dates and times
        const formatDate = (date) => {
          if (!date) return '';
          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');
          return `${year}-${month}-${day}`;
        };

        const formatTime = (date) => {
          if (!date) return '';
          const hours = String(date.getHours()).padStart(2, '0');
          const minutes = String(date.getMinutes()).padStart(2, '0');
          return `${hours}:${minutes}`;
        };

        // Populate modal fields
        document.getElementById('groupRef').value = event.extendedProps.ref || '';
        document.getElementById('groupName').value = event.title || '';
        document.getElementById('eventDate').value = formatDate(startDate);
        document.getElementById('eventEndDate').value = formatDate(endDate);
        document.getElementById('eventStartTime').value = formatTime(startDate);
        document.getElementById('eventEndTime').value = formatTime(endDate);

        // Use the mapping function for type
        document.getElementById('typeSessionEdit').value = getTypeLabel(event.extendedProps.type) || '';

        document.getElementById('description').value = event.extendedProps.description || '';
        document.getElementById('groupId').value = event.id || '';

        // Show the modal using Bootstrap
        const eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
        eventModal.show();
      },

      // Handle date click (when clicking on empty day)
      dateClick: function(info) {
        alert('Clicked on: ' + info.dateStr);
      }
    });

    calendar.render();
    console.log('Calendar rendered');
});