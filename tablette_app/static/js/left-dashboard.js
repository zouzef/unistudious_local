// =============================
// GLOBAL VARIABLES
// =============================
let socket;
let attendanceData = [];
let filteredData = [];
let sessionId = document.body.dataset.sessionId;
let tabletId = document.body.dataset.tabletId;
let absent_students = 0;
let present_students = 0;
let entriesPerPage = 8;
let totalPages = 1;
let groupId = null;
let currentCalendarId = null;
let currentNoteStudentId = null;
let currentNoteAttendanceId = null;
let paymentStatusMap = {};

// =============================
// SOCKET.IO FUNCTIONS
// =============================
function initializeSocket() {
    socket = io();

    socket.on('status', function (data) {
        showNotification(data.message, 'warning');
    });

    socket.on('connect', function () {
        console.log('Connected to server');
        updateConnectionStatus(true);
        socket.emit('join_session', {
            session_id: sessionId,
            tablet_id: tabletId
        });
    });

    socket.on('disconnect', function () {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });

    socket.on('attendance_update', function (data) {
        if (data.session_id === sessionId) {
            attendanceData = data.attendance;
            renderAttendanceTable();
            showNotification('Attendance data updated!', 'success');
        }
    });

    socket.on('status_update', function (data) {
        updateStudentStatusInTable(data.attendance_id, data.new_status);
        showNotification('Student status updated!', 'info');
    });

    socket.on('note_update', function (data) {
        updateStudentNoteInTable(data.user_id, data.note);
        showNotification('Note added!', 'info');
    });
}

function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connectionStatus');
    const statusText = statusElement.querySelector('.status-text');

    if (connected) {
        statusElement.classList.remove('disconnected');
        statusElement.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusElement.classList.remove('connected');
        statusElement.classList.add('disconnected');
        statusText.textContent = 'Disconnected';
    }
}


// =============================
// NOTIFICATION FUNCTIONS
// =============================
function showNotification(message, type = 'info') {
    const toastElement = document.getElementById('updateNotification');
    const messageElement = document.getElementById('toastMessage');

    messageElement.textContent = message;
    toastElement.classList.remove('bg-success', 'bg-info', 'bg-warning');

    switch (type) {
        case 'success':
            toastElement.classList.add('bg-success', 'text-white');
            break;
        case 'info':
            toastElement.classList.add('bg-info', 'text-white');
            break;
        case 'warning':
            toastElement.classList.add('bg-warning');
            break;
    }

    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}


// =============================
// DATA LOADING FUNCTIONS
// =============================
function loadcalender(sessionId) {
    fetch(`/attendance/${sessionId}`)
        .then(res => {
            if (!res.ok) {
                throw new Error("Failed to load session data");
            }
            return res.json();
        })
        .then(data => {
            document.getElementById('name_group_label').innerHTML = data.name || 'N/A';
            document.getElementById('teacher_name').innerHTML = data.teacherFullName || 'N/A';
            document.getElementById('room_name').innerHTML = data.roomName || 'N/A';
            document.getElementById('subject_name').innerHTML = data.subjectName || 'N/A';
        })
        .catch(err => {
            console.error("Error loading session data:", err);
            showNotification('Error loading session data', 'warning');
        });
}

function loadAttendance(sessionId) {
    showLoadingIndicator(true);

    fetch(`/calender/${sessionId}`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            console.log(data);
            attendanceData = data || [];
            renderAttendanceTable();
            showLoadingIndicator(false);
        })
        .catch(err => {
            console.error("Error loading attendance:", err);
            showLoadingIndicator(false);
            showNotification('Error loading attendance data', 'warning');
            const tbody = document.getElementById('attendanceBody');
            tbody.innerHTML = "<tr><td colspan='5'>Error loading attendance data</td></tr>";
        });
}

function loadPaymentStatuses(sessionId) {
    fetch(`/api/get_payment_calander_session/${sessionId}`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            paymentStatusMap = {};
            (data || []).forEach(entry => {
                paymentStatusMap[entry.user_id] = entry.status;
            });
            renderAttendanceTable();
        })
        .catch(err => {
            console.error("Error loading payment statuses:", err);
        });
}

// =============================
// TABLE RENDERING FUNCTIONS
// =============================
function renderAttendanceTable() {
    const tbody = document.getElementById('attendanceBody');
    tbody.innerHTML = "";

    const dataToRender = filteredData.length > 0 ? filteredData : attendanceData;

    if (!dataToRender || dataToRender.length === 0) {
        tbody.innerHTML = "<tr><td colspan='6'>No attendance data found</td></tr>";
        document.getElementById('paginationNav').style.display = 'none';
        return;
    }

    totalPages = Math.ceil(dataToRender.length / entriesPerPage);
    if (currentPage > totalPages) {
        currentPage = Math.max(1, totalPages);
    }

    const startIndex = (currentPage - 1) * entriesPerPage;
    const endIndex = Math.min(startIndex + entriesPerPage, dataToRender.length);
    const pageData = dataToRender.slice(startIndex, endIndex);

    pageData.forEach(item => {
        const statusClass = item.isPresent ? "status-present" : "status-absent";
        const statusText = item.isPresent ? "Present" : "Absent";
        const note = item.note ? item.note : "N/A";

        if (item.isPresent) {
            present_students++;
        } else {
            absent_students++;
        }

        const row = document.createElement('tr');
        row.setAttribute('data-attendance-id', item.id);
        if (paymentStatusMap[item.userId] === 'Unpaid') {
            row.classList.add('payment-row-unpaid');
        }
        row.innerHTML = `
            <td>
                <i class="fa-solid fa-trash" style="font-size:20px;color:red;cursor:pointer" onclick="deleteStudent(${item.userId})"></i>
            </td>
            <td>${item.userId}</td>
            <td>${item.userName}</td>
            <td><div class="status ${statusClass}">${statusText}</div></td>
            <td><div class="note-content">${note}</div></td>
            <td class="buttonss">
                <button class="btn attendance-toggle-btn ${item.isPresent ? 'btn-danger' : 'btn-success'}"
                        data-attendance-id="${item.id}"
                        data-is-present="${item.isPresent}">
                    ${item.isPresent ? 'Mark Absent' : 'Mark Present'}
                </button>
                <button class="btn btn-note"
                    onclick="addNote(${item.userId}, ${item.id})"
                    data-bs-toggle="modal"
                    data-bs-target="#model-add-note"
                    style="
                        display: inline-flex;
                        align-items: center;
                        gap: 6px;
                        background: #EEEDFE;
                        color: #3C3489;
                        border: 1.5px solid #AFA9EC;
                        border-radius: 8px;
                    "
                    onmouseover="this.style.background='#CECBF6'"
                    onmouseout="this.style.background='#EEEDFE'"
                    onmousedown="this.style.transform='scale(0.97)'"
                    onmouseup="this.style.transform='scale(1)'">
                Add Note
            </button>
            <button class="btn btn-payment"
                onclick="showPayment(${item.userId})"
                data-bs-toggle="modal"
                data-bs-target="#model-payment-status"
                    style="
                        display: inline-flex;
                        align-items: center;
                        gap: 6px;
                        background: white;
                        color: rgb(252, 196, 62);
                        border: 1.5px solid rgb(252, 196, 62);
                        padding: 7px 16px;
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: background 0.15s, color 0.15s, transform 0.1s;
                    "
                    onmouseover="this.style.background='rgb(252, 196, 62)'; this.style.color='white'"
                    onmouseout="this.style.background='white'; this.style.color='rgb(252, 196, 62)'"
                    onmousedown="this.style.transform='scale(0.97)'"
                    onmouseup="this.style.transform='scale(1)'">

                Payment
            </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    renderPaginationControls();
}


// =============================
// REAL-TIME UPDATE FUNCTIONS
// =============================
function updateStudentStatusInTable(attendanceId, newStatus) {
    const studentIndex = attendanceData.findIndex(s => s.id === attendanceId);
    if (studentIndex !== -1) {
        attendanceData[studentIndex].isPresent = newStatus;
    }

    const row = document.querySelector(`tr[data-attendance-id="${attendanceId}"]`);
    if (row) {
        const statusCell = row.querySelector('.status');
        const button = row.querySelector('.attendance-toggle-btn');

        if (button) {
            button.setAttribute('data-is-present', newStatus);
            button.textContent = newStatus ? 'Mark Absent' : 'Mark Present';
            button.className = `btn attendance-toggle-btn ${newStatus ? 'btn-danger' : 'btn-success'}`;
        }

        if (statusCell) {
            statusCell.className = `status ${newStatus ? 'status-present' : 'status-absent'}`;
            statusCell.textContent = newStatus ? 'Present' : 'Absent';
        }
    }
}

function updateStudentNoteInTable(userId, note) {
    const studentIndex = attendanceData.findIndex(s => s.userId === userId);
    if (studentIndex !== -1) {
        attendanceData[studentIndex].note = note;
    }

    const rows = document.querySelectorAll('#attendanceBody tr');
    rows.forEach(row => {
        const idCell = row.querySelector('td:first-child');
        if (idCell && idCell.textContent == userId) {
            const noteCell = row.querySelector('.note-content');
            if (noteCell) {
                noteCell.textContent = note || 'N/A';
            }
        }
    });
}


// =============================
// ATTENDANCE STATUS FUNCTIONS
// =============================
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('attendance-toggle-btn')) {
        const button = e.target;
        const id = parseInt(button.getAttribute('data-attendance-id'));
        const currentStatus = button.getAttribute('data-is-present') === 'true';
        markPresent(id, currentStatus);
    }
});

function markPresent(id, currentStatus) {
    showLoadingIndicator(true);
    const newStatus = !currentStatus;

    console.log('Toggling attendance:', {
        id: id,
        currentStatus: currentStatus,
        newStatus: newStatus
    });

    fetch(`/change-stutatus/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            is_present: newStatus
        })
    })
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            showLoadingIndicator(false);
            if (data.status === "success") {
                const button = document.querySelector(`button[data-attendance-id="${id}"]`);
                if (button) {
                    button.setAttribute('data-is-present', newStatus);
                    button.textContent = newStatus ? 'Mark Absent' : 'Mark Present';
                    button.className = `btn attendance-toggle-btn ${newStatus ? 'btn-danger' : 'btn-success'}`;
                }
                showNotification(`Student marked as ${newStatus ? 'present' : 'absent'} successfully!`, 'success');
            } else {
                showNotification(`Failed to update status: ${data.message || 'Unknown error'}`, 'warning');
            }
        })
        .catch(err => {
            console.error("Error updating status:", err);
            showLoadingIndicator(false);
            showNotification("An error occurred while updating status.", 'warning');
        });
}


// =============================
// NOTE MANAGEMENT FUNCTIONS
// =============================
function addNote(userId, attendanceId) {
    currentNoteStudentId = userId;
    currentNoteAttendanceId = attendanceId;
    document.getElementById('noteTextArea').value = '';
}

document.getElementById('add-note').addEventListener('click', function () {
    const note = document.getElementById('noteTextArea').value.trim();

    if (!note) {
        showNotification('Please enter a note before saving.', 'warning');
        return;
    }

    if (!currentNoteStudentId || !currentNoteAttendanceId) {
        showNotification('Error: Student information not found.', 'warning');
        return;
    }

    showLoadingIndicator(true);

    const requestBody = {
        note: note,
        session_id: sessionId
    };

    fetch(`/add-note/${currentNoteAttendanceId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
        .then(res => {
            if (!res.ok) {
                return res.text().then(text => {
                    throw new Error(`HTTP error! status: ${res.status}, response: ${text}`);
                });
            }
            return res.json();
        })
        .then(data => {
            showLoadingIndicator(false);
            if (data.status === "success") {
                showNotification("Note added successfully!", 'success');
                $('#model-add-note').modal('hide');
                currentNoteStudentId = null;
                currentNoteAttendanceId = null;
            } else {
                showNotification(`Failed to add note: ${data.message || 'Unknown error'}`, 'warning');
            }
        })
        .catch(err => {
            console.error("Error adding note:", err);
            showLoadingIndicator(false);
            showNotification("An error occurred while adding the note.", 'warning');
        });
});

document.getElementById('model-add-note').addEventListener('hidden.bs.modal', function () {
    currentNoteStudentId = null;
    currentNoteAttendanceId = null;
    document.getElementById('noteTextArea').value = '';
});


// =============================
// SEARCH/FILTER FUNCTIONS
// =============================
function filterStudents() {
    const searchTerm = document.getElementById('studentSearch').value.toLowerCase().trim();

    if (!searchTerm) {
        filteredData = [];
        currentPage = 1;
        renderAttendanceTable();
        return;
    }

    filteredData = attendanceData.filter(student => {
        const userName = student.userName.toLowerCase();
        const userId = student.userId.toString().toLowerCase();
        return userName.includes(searchTerm) || userId.includes(searchTerm);
    });

    currentPage = 1;

    if (filteredData.length === 0) {
        const tbody = document.getElementById('attendanceBody');
        tbody.innerHTML = "<tr><td colspan='6' style='text-align:center; color:#9490c9; padding:20px; font-style:italic;'>No students found matching your search.</td></tr>";
        document.getElementById('paginationNav').style.display = 'none';
        return;
    }

    renderAttendanceTable();
}


// =============================
// PAGINATION FUNCTIONS
// =============================
function renderPaginationControls() {
    const paginationNav = document.getElementById('paginationNav');

    if (totalPages <= 1) {
        paginationNav.style.display = 'none';
        return;
    }

    paginationNav.style.display = 'flex';

    const prevItem = document.getElementById('prevPageItem');
    if (currentPage === 1) {
        prevItem.classList.add('disabled');
        prevItem.querySelector('a').setAttribute('tabindex', '-1');
    } else {
        prevItem.classList.remove('disabled');
        prevItem.querySelector('a').removeAttribute('tabindex');
    }

    const nextItem = document.getElementById('nextPageItem');
    if (currentPage === totalPages) {
        nextItem.classList.add('disabled');
        nextItem.querySelector('a').setAttribute('tabindex', '-1');
    } else {
        nextItem.classList.remove('disabled');
        nextItem.querySelector('a').removeAttribute('tabindex');
    }

    const existingPages = paginationNav.querySelectorAll('.page-number');
    existingPages.forEach(page => page.remove());

    for (let i = 1; i <= totalPages; i++) {
        const pageItem = document.createElement('li');
        pageItem.className = `page-item page-number ${i === currentPage ? 'active' : ''}`;
        pageItem.innerHTML = `<a class="page-link pagination-link" href="#" onclick="changePage(${i})">${i}</a>`;
        nextItem.parentNode.insertBefore(pageItem, nextItem);
    }
}

function changePage(page) {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
        currentPage = page;
        renderAttendanceTable();
    }
}


// =============================
// STUDENT MANAGEMENT FUNCTIONS
// =============================
function deleteStudent(userId) {
    fetch(`/delete_attendance_api/${sessionId}/${userId}`)
        .then(res => {
            if (!res.ok) {
                throw new Error("Failed to delete user");
            }
            return res.json();
        })
        .then(data => {
            showNotification('success deleting user', 'warning');
        })
        .catch(err => {
            console.error("Error deleting user :", err);
            showNotification('Error deleting user', 'warning');
        });
}

function loadStudentList() {
    currentCalendarId = sessionId;

    fetch(`/slc/list-add-student-attendance/${sessionId}`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            const students = data.users || [];
            const select = document.querySelector("#student-select");
            select.innerHTML = "";

            const defaultOption = document.createElement("option");
            defaultOption.value = "";
            defaultOption.textContent = "Select a student";
            defaultOption.selected = true;
            select.appendChild(defaultOption);

            if (students.length === 0) {
                const option = document.createElement("option");
                option.textContent = "No students found";
                option.disabled = true;
                select.appendChild(option);
                return;
            }

            students.forEach(student => {
                const option = document.createElement("option");
                option.dataset.relationId = student.relationId || student.id;
                option.dataset.id = student.id || student.userId;
                option.dataset.groupId = student.groupId || "default";
                option.value = student.id || student.userId;
                option.textContent = student.fullName || student.name || "Unknown Student";
                select.appendChild(option);
            });

            $('#student-select').select2({
                dropdownParent: $('#model-add-student'),
                placeholder: "Select a student",
                allowClear: false,
                width: '100%'
            });
        })
        .catch(err => {
            console.error("Error loading student list:", err);
            const select = document.querySelector("#student-select");
            select.innerHTML = "";
            const errorOption = document.createElement("option");
            errorOption.textContent = "Error loading students";
            errorOption.disabled = true;
            select.appendChild(errorOption);
        });
}

function load_current_group(calendarId, userId) {
    fetch(`/slc/attendance-get-group-student-select/${calendarId}/${userId}`)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (!data.groups || !Array.isArray(data.groups)) {
                console.error("Expected groups array but got:", data);
                return;
            }

            const select = document.getElementById('change-group');
            select.innerHTML = '';

            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select a group';
            defaultOption.selected = true;
            select.appendChild(defaultOption);

            const uniqueGroups = new Map();
            data.groups.forEach(group => {
                if (!uniqueGroups.has(group.id)) {
                    uniqueGroups.set(group.id, group.name);
                }
            });

            uniqueGroups.forEach((name, id) => {
                const option = document.createElement('option');
                option.value = id;
                option.textContent = name;
                select.appendChild(option);
            });

            document.getElementById('current-group').style.display = 'block';
        })
        .catch(err => {
            console.error("Error loading current group:", err);
            document.getElementById('current-group').style.display = 'none';
        });
}

function get_group_from_calender(calender_id) {
    return fetch(`/api/get-new-group/${calender_id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            if (data.group_session_id) {
                return data.group_session_id;
            } else {
                console.error("Group ID not found in response:", data);
                return null;
            }
        })
        .catch(error => {
            console.error("Error fetching group from calendar:", error);
            return null;
        });
}


// =============================
// UTILITY FUNCTIONS
// =============================
function showLoadingIndicator(show) {
    const loadingElement = document.getElementById('loadingIndicator');
    loadingElement.style.display = show ? 'block' : 'none';
}


// =============================
// INITIALIZATION
// =============================
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('studentSearch');
    searchInput.addEventListener('input', filterStudents);

    if (sessionId) {
        initializeSocket();
        loadAttendance(sessionId);
        loadcalender(sessionId);
        loadPaymentStatuses(sessionId);

        setInterval(() => {
            if (!socket || !socket.connected) {
                loadAttendance(sessionId);
            }
        }, 120000);
    } else {
        console.error("No session ID found");
        showNotification('No session ID found', 'warning');
    }

    const checkbox1 = document.getElementById("checkbox1");
    const checkbox2 = document.getElementById("checkbox2");
    const currentGroup = document.getElementById("current-group");

    checkbox1.addEventListener("change", function () {
        if (this.checked) {
            currentGroup.style.display = "block";
            checkbox2.checked = false;
            checkbox2.disabled = true;
        } else {
            currentGroup.style.display = "none";
            checkbox2.disabled = false;
        }
    });
});

window.sessionId = '{{ session_info.id }}';
window.sessionInfo = {
    id: '{{ session_info.id }}',
    roomId: '{{ session_info.roomId }}',
    start: "{{ session_info.start }}",
    end: "{{ session_info.end }}",
    subject: "{{ session_info.subject if session_info.subject else '' }}"
};


// =============================
// JQUERY READY FUNCTIONS
// =============================
$(document).ready(function () {
    $('#student-select').select2({
        dropdownParent: $('#model-add-student'),
        placeholder: "Select a student",
        allowClear: false,
        width: '100%'
    });

    get_group_from_calender(sessionId).then(id => {
        groupId = id;
        console.log("Group ID loaded:", groupId);
    }).catch(err => {
        console.error("Failed to load group ID:", err);
    });

    async function checkConditionsForAddUser() {
        const checkbox1 = $('#checkbox1').is(':checked');
        const checkbox2 = $('#checkbox2').is(':checked');
        const selectedOption = $('#student-select').find("option:selected");
        const studentId = selectedOption.data("id");
        const relationId = selectedOption.data("relationId");
        const studentName = selectedOption.text();
        const studentSelected = !!studentId;

        if (checkbox2 && studentSelected) {
            const requestData = {
                userId: studentId,
                calendarId: sessionId,
                groupId: groupId,
                relationId: relationId,
                checkbox1: checkbox1,
                checkbox2: checkbox2,
                selectedGroupId: $('#change-group').val()
            };
            console.log(requestData);

            $.ajax({
                url: '/api/add-student-attendance',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(requestData),
                success: function (response) {
                    $('#model-add-student').modal('hide');
                },
            });
        }

        if ((checkbox1 == false) && (checkbox2 == false) && (studentSelected)) {
            const requestData = {
                userId: studentId,
                calendarId: sessionId,
                groupId: groupId,
                relationId: relationId,
                checkbox1: checkbox1,
                checkbox2: checkbox2,
                selectedGroupId: $('#change-group').val()
            };

            $.ajax({
                url: '/api/add-student-attendance',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(requestData),
                success: function (response) {
                    $('#model-add-student').modal('hide');
                },
            });
        }

        if (checkbox1 && studentSelected) {
            const selectedGroupId = $('#change-group').val();
            const requestData = {
                userId: studentId,
                calendarId: sessionId,
                groupId: groupId,
                relationId: relationId,
                checkbox1: checkbox1,
                checkbox2: checkbox2,
                selectedGroupId: $('#change-group').val()
            }
            console.log(requestData);

            $.ajax({
                url: '/api/add-student-attendance',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(requestData),
                success: function (response) {
                    $('#model-add-student').modal('hide');
                },
            });
        }
    }

    $('#add-new-user').on('click', function () {
        checkConditionsForAddUser();
    });

    function checkStudentAndCheckbox() {
        const checkbox1 = $('#checkbox1').is(':checked');
        const selectedOption = $('#student-select').find("option:selected");
        const studentId = selectedOption.data("id");
        const studentSelected = !!studentId;

        if (checkbox1 && studentSelected) {
            load_current_group(sessionId, studentId);
        }
    }

    $('#model-add-student').on('hidden.bs.modal', function () {
        $('#checkbox1').prop('checked', false);
        $('#checkbox2').prop('checked', false);
        $('#student-select').val('').trigger('change');
        $('#current-group').hide();
        $('#checkbox2').prop('disabled', false);
        $('#change-group').empty();
    });

    $('#student-select').on('change', function () {
        const selectedValue = $(this).val();
        const selectedText = $(this).find("option:selected").text();
        const studentId = $(this).find("option:selected").data("id");
        checkStudentAndCheckbox();
    });

    $('#checkbox1').on('change', function () {
        if (this.checked) {
            $('#current-group').show();
        } else {
            $('#current-group').hide();
        }
        checkStudentAndCheckbox();
    });
});


// =============================
// PAYMENT MODAL FUNCTIONS
// =============================
function showPayment(userId) {
    const tbody = document.getElementById('paymentBody');
    const loading = document.getElementById('payment-loading');
    const empty = document.getElementById('payment-empty');
    const sessionNameEl = document.getElementById('payment-session-name');
    const studentNameEl = document.getElementById('payment-student-name');

    // Reset state
    tbody.innerHTML = '';
    empty.style.display = 'none';
    empty.querySelector('p').textContent = 'No orders found for this student.';
    sessionNameEl.textContent = '—';
    studentNameEl.textContent = '—';
    loading.style.display = 'flex';

    fetch(`/api/get_payment_calander_user/${sessionId}/${userId}`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            loading.style.display = 'none';

            if (!data || data.length === 0) {
                empty.style.display = 'block';
                return;
            }

            // Fill info pills using the first record
            sessionNameEl.textContent = data[0].name || 'N/A';
            studentNameEl.textContent = data[0].username || 'N/A';

            data.forEach(payment => {
                let statusClass = 'payment-status-not-registered';
                let rowClass = '';

                if (payment.status === 'Paid') {
                    statusClass = 'payment-status-paid';
                } else if (payment.status === 'Cancelled') {
                    statusClass = 'payment-status-cancelled';
                } else if (payment.status === 'Not Registered') {
                    statusClass = 'payment-status-not-registered';
                } else if (payment.status === 'Unpaid') {
                    statusClass = 'payment-status-unpaid';
                    rowClass = 'payment-row-unpaid';
                }

                const row = document.createElement('tr');
                if (rowClass) {
                    row.className = rowClass;
                }

                const description = payment.description ? payment.description : 'N/A';
                const amount = payment.amount && payment.amount !== '0'
                    ? `${payment.amount} DT`
                    : '—';
                const datePayment = payment.date_payment
                    ? new Date(payment.date_payment).toLocaleDateString('en-GB', {
                        day: '2-digit', month: 'short', year: 'numeric'
                    })
                    : 'N/A';

                row.innerHTML = `
                    <td>#${payment.id}</td>
                    <td>${payment.type_date || 'N/A'}</td>
                    <td>${description}</td>
                    <td><span class="payment-status-badge ${statusClass}">${payment.status}</span></td>
                    <td>${amount}</td>
                    <td>${datePayment}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(err => {
            console.error("Error loading payment data:", err);
            loading.style.display = 'none';
            empty.style.display = 'block';
            empty.querySelector('p').textContent = 'Error loading payment data.';
            showNotification('Error loading payment data', 'warning');
        });
}