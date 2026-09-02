document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('marketChart').getContext('2d');

    fetch('/api/get-user-registration')
        .then(res => {
            if (!res) return null;
            if (!res.ok) {
                throw new Error(`HTTP error, status: ${res.status}`);
            }
            return res.json();
        })
        .then(chartData => {
            if (!chartData) return;
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        label: 'Students Registrations',
                        data: chartData.data,
                        borderColor: '#4c4b9e',
                        backgroundColor: 'rgba(76, 75, 158, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3
                    }]
                },
                options: {
                    responsive: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        })
        .catch(err => {
            console.error('Error loading chart data:', err);
        });
});

function extractRows(response) {
    if (Array.isArray(response)) return response;
    if (!response || typeof response !== 'object') return [];
    if (Array.isArray(response.data)) return response.data;
    if (Array.isArray(response.events)) return response.events;
    if (Array.isArray(response.result)) return response.result;
    if (Array.isArray(response.rows)) return response.rows;
    return [];
}

function pick(obj, ...keys) {
    for (const k of keys) {
        if (obj[k] !== undefined && obj[k] !== null) return obj[k];
    }
    return null;
}

function buildRow(item) {
    const startRaw = pick(item, 'start_time', 'start', 'startTime');
    const endRaw = pick(item, 'end_time', 'end', 'endTime');

    const start = startRaw ? new Date(startRaw).toLocaleString() : 'N/A';
    const end = endRaw ? new Date(endRaw).toLocaleString() : 'N/A';

    const title = pick(item, 'title', 'name') || 'N/A';
    const teacherName = pick(item, 'teacherName', 'teacher_name', 'teacher') || 'N/A';
    const roomName = pick(item, 'roomName', 'room_name', 'room') || 'N/A';
    const type = pick(item, 'type', 'eventType') || 'N/A';
    const color = pick(item, 'color') || '#999';

    return `
        <tr>
            <td><span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:${color};"></span></td>
            <td>${title}</td>
            <td>${teacherName}</td>
            <td>${roomName}</td>
            <td>${start}</td>
            <td>${end}</td>
            <td>${type}</td>
        </tr>
    `;
}

function loadCalanderModerateur(sessionId, accountId) {
    console.log('loadCalanderModerateur called with', sessionId, accountId);

    fetch(`/api/get-calender-moderateur/${sessionId}/${accountId}`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error, status: ${res.status}`);
            }
            return res.json();
        })
        .then(response => {
            console.log('Calendar response (raw):', response);

            const tbody = document.querySelector('#example-calendar-events tbody');
            if (!tbody) {
                console.error('tbody not found for #example-calendar-events');
                return;
            }

            const rows = extractRows(response);
            console.log('Extracted rows:', rows);

            tbody.innerHTML = '';

            if (!rows || rows.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">No data</td></tr>';
                return;
            }

            rows.forEach(item => {
                tbody.insertAdjacentHTML('beforeend', buildRow(item));
            });

            console.log('Rows inserted:', tbody.children.length);

            if (typeof $ !== 'undefined' && $.fn && $.fn.DataTable) {
                if ($.fn.DataTable.isDataTable('#example-calendar-events')) {
                    $('#example-calendar-events').DataTable().destroy();
                }
                $('#example-calendar-events').DataTable({
                    language: {
                        paginate: {
                            previous: '&lsaquo;',
                            next: '&rsaquo;'
                        }
                    }
                });
            } else {
                console.warn('jQuery/DataTable not loaded — skipping DataTable init');
            }
        })
        .catch(err => console.error('Error loading calendar data:', err));
}

function loadCalendarSessions(accountId) {
    console.log('loadCalendarSessions called with accountId =', accountId);

    if (accountId === undefined || accountId === null || accountId === 'undefined') {
        console.error('Invalid accountId, aborting session load:', accountId);
        return;
    }

    fetch(`/api/get-sessions/${accountId}`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error, status: ${res.status}`);
            }
            return res.json();
        })
        .then(result => {
            console.log('Sessions response:', result);

            const select = document.getElementById('calendar-session-filter');
            select.innerHTML = '<option value="">Select a session</option>';

            const sessions = extractRows(result);
            sessions.forEach(sess => {
                const option = document.createElement('option');
                option.value = sess.id;
                option.textContent = sess.name;
                select.appendChild(option);
            });

            if (typeof $ !== 'undefined' && $.fn && $.fn.selectpicker) {
                $(select).selectpicker('refresh');
            }

            if (sessions.length > 0) {
                if (typeof $ !== 'undefined' && $.fn && $.fn.selectpicker) {
                    $(select).selectpicker('val', String(sessions[0].id));
                } else {
                    select.value = sessions[0].id;
                }
                loadCalanderModerateur(sessions[0].id, accountId);
            } else {
                console.warn('No sessions returned for this account');
            }
        })
        .catch(error => {
            console.error('Error loading sessions:', error);
        });
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('window.ACCOUNT_ID =', window.ACCOUNT_ID);

    loadCalendarSessions(window.ACCOUNT_ID);

    const filterEl = document.getElementById('calendar-session-filter');
    if (typeof $ !== 'undefined') {
        $(filterEl).on('change', function () {
            const sessionId = this.value;
            if (sessionId) {
                loadCalanderModerateur(sessionId, window.ACCOUNT_ID);
            } else {
                document.querySelector('#example-calendar-events tbody').innerHTML =
                    '<tr><td colspan="7" class="text-center">No session selected</td></tr>';
            }
        });
    } else {
        filterEl.addEventListener('change', function () {
            const sessionId = this.value;
            if (sessionId) {
                loadCalanderModerateur(sessionId, window.ACCOUNT_ID);
            } else {
                document.querySelector('#example-calendar-events tbody').innerHTML =
                    '<tr><td colspan="7" class="text-center">No session selected</td></tr>';
            }
        });
    }
});