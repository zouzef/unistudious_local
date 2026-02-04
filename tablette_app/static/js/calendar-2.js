document.addEventListener('DOMContentLoaded', function() {
    var Calendar = FullCalendar.Calendar;

    // Get data attributes from the 'calendare' div
    var dataEl = document.getElementById('calendare');
    const sessionId = dataEl.dataset.sessionId;
    const roomId = dataEl.dataset.roomId;

    console.log('Session ID:', sessionId);
    console.log('Room ID:', roomId);

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
                title: item.title, // This is "Groub FFF" in your data
                start: item.start_time, // Note: underscore, not camelCase
                end: item.end_time,     // Note: underscore, not camelCase
                backgroundColor: item.color, // Use the color from your data
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

      // Display event details on click
      eventClick: function(info) {
        alert('Event: ' + info.event.title + '\n' +
              'Description: ' + info.event.extendedProps.description + '\n' +
              'Reference: ' + info.event.extendedProps.ref + '\n' +
              'Type: ' + info.event.extendedProps.type + '\n' +
              'Start: ' + info.event.start.toLocaleString() + '\n' +
              'End: ' + info.event.end.toLocaleString());
      }
    });

    calendar.render();
    console.log('Calendar rendered');
});