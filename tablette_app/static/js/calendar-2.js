document.addEventListener('DOMContentLoaded', function() {
    var Calendar = FullCalendar.Calendar;

    // Get data attributes from the 'calendare' div
    var dataEl = document.getElementById('calendare');
    const sessionId = dataEl.dataset.sessionId;
    const roomId = dataEl.dataset.roomId;

    console.log('Session ID:', sessionId); // For debugging
    console.log('Room ID:', roomId); // For debugging

    // Initialize calendar on the 'calendar' div
    var calendarEl = document.getElementById('calendar');

    var calendar = new Calendar(calendarEl, {
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      initialDate: new Date(), // Use current date instead of hardcoded
      navLinks: true,
      editable: true,
      droppable: true,
      dayMaxEvents: true,

      // Fetch events from your endpoint
      events: function(info, successCallback, failureCallback) {
        console.log('Fetching calendar events...'); // For debugging
        fetch(`/get-all-calander/${roomId}`)
          .then(response => {
            console.log('Response status:', response.status); // For debugging
            return response.json();
          })
          .then(data => {
            console.log('Calendar data received:', data); // For debugging
            if (data.Message === "Success") {
              // Transform your data to FullCalendar format
              const events = data.data.map(item => ({
                id: item.id,
                title: item.name || item.subjectName, // Use group name or subject
                start: item.start,
                end: item.end,
                extendedProps: {
                  description: item.description,
                  teacherName: item.teacherFullName,
                  subjectName: item.subjectName,
                  roomName: item.roomName,
                  sessionName: item.sessionName,
                  localName: item.localName
                }
              }));
              console.log('Transformed events:', events); // For debugging
              successCallback(events);
            } else {
              console.error('Failed to fetch events - Message not Success');
              failureCallback(new Error('Failed to fetch events'));
            }
          })
          .catch(error => {
            console.error('Error fetching calendar events:', error);
            failureCallback(error);
          });
      },

      // Optional: Display event details on click
      eventClick: function(info) {
        alert('Event: ' + info.event.title + '\n' +
              'Teacher: ' + info.event.extendedProps.teacherName + '\n' +
              'Subject: ' + info.event.extendedProps.subjectName + '\n' +
              'Room: ' + info.event.extendedProps.roomName);
      }
    });

    calendar.render();
    console.log('Calendar rendered'); // For debugging
});