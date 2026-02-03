document.addEventListener('DOMContentLoaded', function() {
    // Check if calendar-info element exists on this page
    var calendarInfoEl = document.getElementById('calendar-info');
    if (!calendarInfoEl) {
        console.log('Calendar info element not found - skipping calendar initialization');
        return; // Exit early if not on a calendar page
    }

    var Calendar = FullCalendar.Calendar;
    var Draggable = FullCalendar.Draggable;

    var containerEl = document.getElementById('external-events');

    // Get data from calendar-info div
    var sessionId = parseInt(calendarInfoEl.dataset.sessionId);
    var accountId = parseInt(calendarInfoEl.dataset.accountId);

    console.log('Session ID:', sessionId);
    console.log('Account ID:', accountId);

    // Get the actual calendar element to render on
    var calendarEl = document.getElementById('calendar');

    // Check if calendar element exists
    if (!calendarEl) {
        console.error('Calendar element not found');
        return;
    }

    // Initialize the external events
    if (containerEl) {
        new Draggable(containerEl, {
          itemSelector: '.external-event',
          eventData: function(eventEl) {
            return {
              title: eventEl.innerText,
              groupId: eventEl.getAttribute('data-group-id'),
              groupCapacity: eventEl.getAttribute('data-group-capacity')
            };
          }
        });
    }

    // Function to adjust timezone - SUBTRACT 1 hour
    function adjustTimezone(dateString) {
        var date = new Date(dateString);
        date.setHours(date.getHours() - 1);
        return date;
    }

    // Initialize the calendar
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

      events: function(info, successCallback, failureCallback) {
        var url = `/dashboard/get_calander_per_session/${accountId}/${sessionId}`;
        console.log('Fetching from URL:', url);

        fetch(url)
          .then(response => {
            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
          })
          .then(data => {
            console.log('Data received:', data);

            if (data.success && data.data) {
              var events = data.data.map(function(item) {
                var startDate = adjustTimezone(item.start_time);
                var endDate = adjustTimezone(item.end_time);

                return {
                  id: item.id,
                  title: item.title,
                  start: startDate,
                  end: endDate,
                  backgroundColor: item.color,
                  borderColor: item.color,
                  extendedProps: {
                    description: item.description,
                    teacher_id: item.teacher_id,
                    subject_id: item.subject_id,
                    room_id: item.room_id,
                    group_session_id: item.group_session_id,
                    ref: item.ref
                  }
                };
              });
              console.log('Transformed events:', events);
              successCallback(events);
            } else {
              console.error('No data or success flag false:', data);
              successCallback([]);
            }
          })
          .catch(error => {
            console.error('Fetch error:', error);
            console.error('Error message:', error.message);
            failureCallback(error);
          });
      },

      // OPEN MODAL WHEN GROUP IS DROPPED
      drop: function(info) {
    console.log('=== GROUP DROPPED ===');
    console.log('Dropped event:', info);

    const droppedDate = info.date;
    const groupName = info.draggedEl.innerText.trim();
    const groupId = info.draggedEl.getAttribute('data-group-id');
    const groupCapacity = info.draggedEl.getAttribute('data-group-capacity');

    console.log('Group Name:', groupName);
    console.log('Group ID:', groupId);
    console.log('Group Capacity:', groupCapacity);
    console.log('Dropped Date:', droppedDate);

    // Open the modal first - NEW ID
    const modalElement = document.getElementById('createEventModal');
    if (!modalElement) {
        console.error('Modal element not found: createEventModal');
        return;
    }

    const eventModal = new bootstrap.Modal(modalElement);
    eventModal.show();

    // Wait for modal to be shown, then populate the form
    modalElement.addEventListener('shown.bs.modal', function() {
        // Safely populate the form with dropped group info - NEW IDs
        const eventTitle = document.getElementById('createEventTitle');
        const eventDate = document.getElementById('createEventDate');
        const eventGroupId = document.getElementById('createEventGroupId');
        const eventGroupCapacity = document.getElementById('createEventGroupCapacity');
        const eventSessionId = document.getElementById('createEventSessionId');
        const eventAccountId = document.getElementById('createEventAccountId');

        if (eventTitle) eventTitle.value = groupName;
        if (eventDate) eventDate.value = droppedDate.toISOString().split('T')[0];
        if (eventGroupId) eventGroupId.value = groupId;
        if (eventGroupCapacity) eventGroupCapacity.value = groupCapacity;
        if (eventSessionId) eventSessionId.value = sessionId;
        if (eventAccountId) eventAccountId.value = accountId;

        // Log which elements were found/not found
        console.log('createEventTitle found:', !!eventTitle);
        console.log('createEventDate found:', !!eventDate);
        console.log('createEventGroupId found:', !!eventGroupId);
        console.log('createEventGroupCapacity found:', !!eventGroupCapacity);
        console.log('createEventSessionId found:', !!eventSessionId);
        console.log('createEventAccountId found:', !!eventAccountId);
        }, { once: true });
    },

      // Redirect to attendance page when event is clicked
      eventClick: function(info) {
        // Get the event ID
        var eventId = info.event.id;

        // Redirect to the attendance page
        window.location.href = '/dashboard/show-attendance-presence/' + eventId;

        // Prevent default action
        info.jsEvent.preventDefault();
      }
    });

    calendar.render();
});