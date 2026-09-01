document.addEventListener('DOMContentLoaded', function () {
    loadUserInfo(window.USER_ID);
    loadProfileImage(window.USER_ID);
});

function loadUserInfo(userId) {
    fetch(`/api/get-user-info/${userId}`)
        .then(response => response.json())
        .then(result => {
            if (!result.Data || result.Data.length === 0) {
                console.error('No user data found');
                return;
            }
            const user = result.Data[0];
            renderUserInfo(user);
        })
        .catch(error => {
            console.error('Error fetching user info:', error);
        });
}

function renderUserInfo(user) {
    document.querySelector('.user h2.mb-0').textContent = user.full_name || '—';

    let role = 'Student';
    try {
        const roles = JSON.parse(user.roles);
        if (roles && roles.length > 0) {
            role = roles[0].replace('ROLE_', '');
        }
    } catch (e) {
        console.error('Error parsing roles:', e);
    }
    document.querySelector('.user p.text-primary').textContent = role;

    document.querySelector('.student-details:nth-of-type(1) h5').textContent = user.grand || '—';
    document.querySelectorAll('.student-details')[1].querySelector('h5').textContent = user.address || '—';
    document.querySelectorAll('.student-details')[2].querySelector('h5').textContent = user.phone || '—';
    document.querySelectorAll('.student-details')[3].querySelector('h5').textContent = user.email || '—';
}

function loadProfileImage(userId) {
    const img = document.querySelector('.user-media img.avatar');
    if (img) {
        img.src = `/api/get_profile_img/${userId}?t=${Date.now()}`;
    }
}



document.addEventListener('DOMContentLoaded', function () {
    loadUserSessions(window.USER_ID);

    $('#session-filter').on('change', function () {
        const sessionId = this.value;
        if (sessionId) {
            loadPaymentHistory(sessionId, window.USER_ID);
        } else {
            renderPaymentTable([]);
        }
    });

    $('#schedule-session-filter').on('change', function () {
        const sessionId = this.value;
        if (sessionId) {
            loadAttendanceHistory(sessionId, window.USER_ID);
        } else {
            renderScheduleTable([]);
        }
    });
});

function loadUserSessions(userId) {
    fetch(`/api/get_assigned_session_user/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            account_id: window.ACCOUNT_ID,
            is_virtual: false
        })
    })
    .then(response => response.json())
    .then(result => {
        const select = document.getElementById('session-filter');
        const scheduleSelect = document.getElementById('schedule-session-filter');
        select.innerHTML = '<option value="">Select a session</option>';
        scheduleSelect.innerHTML = '<option value="">Select a session</option>';

        const sessions = result.data || [];
        sessions.forEach(sess => {
            const option = document.createElement('option');
            option.value = sess.id;
            option.textContent = sess.name;
            select.appendChild(option);

            const option2 = document.createElement('option');
            option2.value = sess.id;
            option2.textContent = sess.name;
            scheduleSelect.appendChild(option2);
        });

        $(select).selectpicker('refresh');
        $(scheduleSelect).selectpicker('refresh');

        if (sessions.length > 0) {
            $(select).selectpicker('val', String(sessions[0].id));
            $(scheduleSelect).selectpicker('val', String(sessions[0].id));
            loadPaymentHistory(sessions[0].id, window.USER_ID);
            loadAttendanceHistory(sessions[0].id, window.USER_ID);
        }
    })
    .catch(error => {
        console.error('Error loading sessions:', error);
    });
}

function loadPaymentHistory(sessionId, userId) {
    fetch(`/api/get_payment_user_info_service/${sessionId}/${userId}`)
        .then(response => response.json())
        .then(result => {
            const payments = Array.isArray(result) ? result : (result.data || []);
            renderPaymentTable(payments);
        })
        .catch(error => {
            console.error('Error loading payment history:', error);
            renderPaymentTable([]);
        });
}

function renderPaymentTable(payments) {
    const tbody = document.querySelector('#example-payment tbody');
    tbody.innerHTML = '';

    if (payments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">No payment history found</td></tr>';
        return;
    }

    payments.forEach(p => {
        const statusClass = p.status === 'Paid' ? 'text-success' :
                             p.status === 'Unpaid' ? 'text-danger' : 'text-warning';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="sorting_1">
                <div class="d-flex align-items-center">
                    <div class="icon-box icon-box-sm bg-danger">
                        <svg width="26" height="16" viewBox="0 0 26 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M25.0004 1.33333C25.013 1.24043 25.013 1.14624 25.0004 1.05333C24.9888 0.975052 24.9664 0.898765 24.9337 0.826666C24.8985 0.761503 24.8584 0.699103 24.8137 0.64C24.763 0.555671 24.7001 0.479292 24.6271 0.413333L24.4671 0.32C24.3901 0.262609 24.3046 0.21762 24.2137 0.186666H23.9471C23.8658 0.107993 23.7709 0.0447434 23.6671 0H17.0004C16.6468 0 16.3076 0.140476 16.0576 0.390525C15.8075 0.640573 15.6671 0.979711 15.6671 1.33333C15.6671 1.68696 15.8075 2.02609 16.0576 2.27614C16.3076 2.52619 16.6468 2.66667 17.0004 2.66667H20.7737L15.4404 8.94667L9.68039 5.52C9.40757 5.35773 9.0858 5.29813 8.77296 5.3519C8.46011 5.40567 8.17671 5.56929 7.97373 5.81333L1.30706 13.8133C1.19479 13.9481 1.1102 14.1036 1.05815 14.2711C1.00609 14.4386 0.987577 14.6147 1.00368 14.7893C1.01978 14.9639 1.07017 15.1337 1.15198 15.2888C1.23378 15.4439 1.34538 15.5814 1.48039 15.6933C1.72028 15.8921 2.02219 16.0006 2.33373 16C2.52961 16.0003 2.72315 15.9575 2.9006 15.8745C3.07804 15.7915 3.23503 15.6705 3.36039 15.52L9.29373 8.4L14.9871 11.8133C15.2571 11.9735 15.575 12.0332 15.8848 11.982C16.1945 11.9308 16.4763 11.7719 16.6804 11.5333L22.3337 4.93333V8C22.3337 8.35362 22.4742 8.69276 22.7242 8.94281C22.9743 9.19286 23.3134 9.33333 23.6671 9.33333C24.0207 9.33333 24.3598 9.19286 24.6099 8.94281C24.8599 8.69276 25.0004 8.35362 25.0004 8V1.33333Z" fill="#FCFCFC"></path>
                        </svg>
                    </div>
                    <div class="ms-3">
                        <h6 class="mb-0 font-w600">${p.id}</h6>
                    </div>
                </div>
            </td>
            <td><span>${p.date_payment || '—'}</span></td>
            <td><span class="doller font-w600"> $ ${p.amount || 0}</span></td>
            <td class="pe-3"><span class="${statusClass} font-w600">${p.status || '—'}</span></td>
        `;
        tbody.appendChild(row);
    });
}

function loadAttendanceHistory(sessionId, userId) {
    fetch(`/api/get-user-history/${sessionId}/${userId}`)
        .then(response => response.json())
        .then(result => {
            const history = Array.isArray(result) ? result : (result.data || []);
            renderScheduleTable(history);
        })
        .catch(error => {
            console.error('Error loading attendance history:', error);
            renderScheduleTable([]);
        });
}

function renderScheduleTable(history) {
    const tbody = document.getElementById('example-schedule-body');
    tbody.innerHTML = '';

    if (history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No schedule found</td></tr>';
        return;
    }

    history.forEach((h, index) => {
        const badgeClass = h.is_present === 1 ? 'badge-success' : 'badge-danger';
        const statusText = h.is_present === 1 ? 'Present' : 'Absent';

        const row = document.createElement('tr');
        row.innerHTML = `
            <th>${index + 1}</th>
            <td>${h.title || '—'}</td>
            <td><span class="badge ${badgeClass}">${statusText}</span></td>
            <td>${h.start_time || '—'}</td>
            <td>${h.teacher_name || '—'}</td>
        `;
        tbody.appendChild(row);
    });
}