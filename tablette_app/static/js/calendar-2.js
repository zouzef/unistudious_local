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
                'P': 'Presence',
                'O': 'Online',
                'H': 'Hybrid',
                'A': 'Absence',
            };
            return typeMap[type] || type;
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
            info.jsEvent.preventDefault();

            // Close the "more" popover if open
            const popover = document.querySelector('.fc-popover');
            if (popover) popover.remove();

            const event = info.event;
            const startDate = event.start;
            const endDate = event.end;

            const formatDate = (date) => {
                if (!date) return '';
                return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
            };

            const formatTime = (date) => {
                if (!date) return '';
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                return `${hours}:${minutes}`;
            };

            // Type badge colors
            const typeColors = {
                'P': '#27ae60',
                'O': '#2980b9',
                'H': '#8e44ad',
                'A': '#e74c3c'
            };
            const type = event.extendedProps.type || '';
            const typeLabel = getTypeLabel(type);
            const typeColor = typeColors[type] || '#667eea';

            // Fill modal data
            document.getElementById('modal-title').textContent = event.title || 'No Title';
            document.getElementById('modal-ref').textContent = event.extendedProps.ref || '-';
            document.getElementById('modal-date').textContent = `${formatDate(startDate)} → ${formatDate(endDate)}`;
            document.getElementById('modal-time').textContent = `${formatTime(startDate)} - ${formatTime(endDate)}`;

            // Type badge with dynamic color
            const typeBadge = document.getElementById('modal-type-badge');
            typeBadge.textContent = typeLabel;
            typeBadge.style.background = typeColor;

            // Extract teacher name from description
            const desc = event.extendedProps.description || '';
            const teacherMatch = desc.match(/Teacher\s+"(.+?)"/i);
            document.getElementById('modal-teacher').textContent = teacherMatch ? teacherMatch[1] : '-';

            // Description
            if (desc) {
                document.getElementById('modal-description').textContent = desc;
                document.getElementById('modal-description-container').style.display = 'block';
            } else {
                document.getElementById('modal-description-container').style.display = 'none';
            }

            // Teacher image
            const teacherId = event.extendedProps.teacherId;
            const img = document.getElementById('modal-teacher-img');
            if (teacherId) {
                img.src = `/api/get-profile-image/${teacherId}`;
                img.onerror = () => img.src = '/static/assets/images/profile.svg';
            } else {
                img.src = '/static/assets/images/profile.svg';
            }

            // Dynamic header gradient based on type
            const gradients = {
                'P': 'linear-gradient(135deg, #27ae60, #2ecc71)',
                'O': 'linear-gradient(135deg, #2980b9, #3498db)',
                'H': 'linear-gradient(135deg, #8e44ad, #9b59b6)',
                'A': 'linear-gradient(135deg, #c0392b, #e74c3c)'
            };
            document.getElementById('modal-header-banner').style.background = '#4D44B5';

            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('eventDetailModal'));
            modal.show();
        },

          // Handle date click (when clicking on empty day)
        // Handle date click (when clicking on empty day)
          dateClick: function(info) {
            const clickedDate = info.dateStr; // format: "2026-03-12"

            const eventsOnDay = calendar.getEvents().filter(event => {
                if (!event.start) return false;
                // Extract just the date part regardless of time/timezone
                const eventDate = event.start.toISOString().substring(0, 10);
                return eventDate === clickedDate;
            });

            console.log('Clicked date:', clickedDate);
            console.log('Events found:', eventsOnDay.length);

            if (eventsOnDay.length > 0) {
                Swal.fire({
                    icon: 'success',
                    title: '📅 Classes Today!',
                    html: `There ${eventsOnDay.length === 1 ? 'is' : 'are'} <b>${eventsOnDay.length}</b> class${eventsOnDay.length > 1 ? 'es' : ''} scheduled on <b>${clickedDate}</b>`,
                    confirmButtonColor: '#28a745',
                    confirmButtonText: 'OK'
                });
            } else {
                Swal.fire({
                    icon: 'info',
                    title: 'No Class Today',
                    text: `There is no class scheduled on ${clickedDate}`,
                    confirmButtonColor: '#3085d6',
                    confirmButtonText: 'OK'
                });
            }
        }

        });

        calendar.render();
        console.log('Calendar rendered');

    });