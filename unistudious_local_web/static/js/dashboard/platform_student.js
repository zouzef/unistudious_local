/* ===============================================
   USER MANAGEMENT - TABLE PAGE
   =============================================== */

// ==================== DATATABLE INIT ====================
let dataTableInstance = null;

function initDataTable() {
    if ($.fn.DataTable.isDataTable('#example8')) {
        $('#example8').DataTable().destroy();
        dataTableInstance = null;
    }

    dataTableInstance = $('#example8').DataTable({
        order: [],
        pageLength: 10,
        lengthChange: true,
        lengthMenu: [10, 25, 50, 100],
        language: {
            lengthMenu: 'Show _MENU_ entries',
            paginate: {
                next: '<i class="fa-solid fa-angle-right"></i>',
                previous: '<i class="fa-solid fa-angle-left"></i>'
            }
        },
        drawCallback: function () {
            stylePaginationButtons();
        }
    });
}

function stylePaginationButtons() {
    const paginate = document.querySelector('#example8_wrapper .dataTables_paginate');
    if (!paginate) return;

    paginate.querySelectorAll('span > a, a.paginate_button').forEach(btn => {
        btn.style.cssText = `
            min-width: 32px; height: 32px; border-radius: 8px;
            border: 1.5px solid #e0dfef; background: #fff;
            color: #4c4b8f; font-size: 13px; font-weight: 500;
            cursor: pointer; display: inline-flex; align-items: center;
            justify-content: center; padding: 0 6px; margin: 0 2px;
            text-decoration: none; transition: background .15s;
        `;
    });

    paginate.querySelectorAll('a.paginate_button.current').forEach(btn => {
        btn.style.cssText += `background: #4c4b9e !important; color: #fff !important; border-color: #4c4b9e !important;`;
    });

    paginate.querySelectorAll('a.paginate_button.disabled').forEach(btn => {
        btn.style.opacity = '0.35';
        btn.style.cursor = 'default';
    });
}


// ==================== CONFIGURATION ====================
const CONFIG = {
  USERS_PER_PAGE: 10
};

// ==================== STATE ====================
const state = {
  accountId: window.ACCOUNT_ID,
  allUsers: [],
  currentPage: 1
};

// ==================== API ====================
const API = {
  async fetchUsers(accountId) {
    const response = await fetch(`/api/get-all-users/${accountId}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const result = await response.json();
    return result.data?.data ?? result.data ?? [];
  }
};


// ==================== TABLE ====================
async function loadTableUsers(accountId) {
  const tbody = document.querySelector('#example8 tbody');

  if (!tbody) {
    console.error("❌ #example8 tbody not found in DOM");
    return;
  }

  try {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </td>
      </tr>`;

    const users = await API.fetchUsers(accountId);
    state.allUsers = users;

    renderTable(state.allUsers);

  } catch (error) {
    console.error("❌ Error loading table users:", error);
    tbody.innerHTML = `
      <tr>
        <td colspan="5">
          <div class="alert alert-danger m-3">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            Failed to load users. Please try again.
          </div>
        </td>
      </tr>`;
  }
}

function renderTable(users) {
  const tbody = document.querySelector('#example8 tbody');

  if ($.fn.DataTable.isDataTable('#example8')) {
    $('#example8').DataTable().destroy();
    dataTableInstance = null;
  }

  if (!users.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center py-4 text-muted">No users found.</td>
      </tr>`;
    initDataTable();
    return;
  }

  tbody.innerHTML = users.map(user => {
    const isReal = user.type === 'real';
    const displayUser = (isReal && user.virtualUser) ? user.virtualUser : user;

    return `
      <tr id="student-row-${user.id}">
        <td class="student-name">
          <div class="trans-list">
            <h4>${displayUser.fullName ?? '-'}</h4>
          </div>
        </td>
        <td class="student-phone">
          <div class="trans-list">
            <h4>${displayUser.phone ?? '-'}</h4>
          </div>
        </td>
        <td class="student-email">
          <div class="trans-list">
            <h4>${displayUser.email ?? '-'}</h4>
          </div>
        </td>

        ${isReal
          ? `<td class="sorting_1 student-type">
               <span class="badge light badge-primary">
                 <i class="fa fa-circle text-primary me-1"></i>
                 Real
               </span>
             </td>`
          : `<td class="sorting_1 student-type">
               <span class="badge light badge-warning">
                 <i class="fa fa-circle text-warning me-1"></i>
                 Virtual
               </span>
             </td>`
        }

        ${isReal
          ? `<td>
               <a data-user-id="${user.id}"
                  data-id="${user.virtualUser ? user.virtualUser.id : ''}"
                  data-name="${displayUser.fullName ?? ''}"
                  data-phone="${displayUser.phone ?? ''}"
                  data-status="${displayUser.status ?? ''}"
                  data-account-id="${displayUser.account ?? ''}"
                  data-email="${displayUser.email ?? ''}"
                  class="btn btn-sm btn-outline-primary btn-edit-virtual-user">
                 <i class="fa fa-edit me-1"></i>
                 Edit
               </a>
               <a data-user-id="${user.id}"
                  class="btn btn-sm btn-outline-info btn-manage-sessions-virtual-user">
                 <i class="fa fa-calendar-alt me-1"></i>
                 Manage Sessions
               </a>
               ${user.mastodonAccessToken
                 ? `<a href="/dashboard/show-profile-admin/${user.id}" class="btn btn-sm btn-outline-warning">
                      <i class="fa fa-user me-1"></i>
                      Show Profile
                    </a>`
                 : `<button type="button" class="btn btn-sm btn-outline-dark" disabled>
                      <i class="fa fa-user me-1"></i>
                      Show Profile
                    </button>`
               }
             </td>`
          : `<td>
               <a data-user-id="${user.userId}"
                  data-id="${user.id}"
                  data-account-id="${user.account ?? ''}"
                  class="btn btn-sm btn-outline-success btn-associate-virtual-user">
                 <i class="fa fa-link me-1"></i>
                 Associate Student
               </a>
               <a data-user-id="${user.userId}"
                  class="btn btn-sm btn-outline-info btn-manage-sessions-virtual-user">
                 <i class="fa fa-calendar-alt me-1"></i>
                 Manage Sessions
               </a>
               <a data-user-id="${user.userId}"
                  data-id="${user.id}"
                  data-name="${user.fullName ?? ''}"
                  data-phone="${user.phone ?? ''}"
                  data-status="${user.status ?? ''}"
                  data-account-id="${user.account ?? ''}"
                  data-email="${user.email ?? ''}"
                  class="btn btn-sm btn-outline-primary btn-edit-virtual-user">
                 <i class="fa fa-edit me-1"></i>
                 Edit
               </a>
               <a data-user-id="${user.userId}"
                  data-id="${user.id}"
                  data-account-id="${user.account ?? ''}"
                  class="btn btn-sm btn-outline-danger btn-delete-virtual-user">
                 <i class="fa fa-trash me-1"></i>
                 Delete
               </a>
             </td>`
        }
      </tr>
    `;
  }).join('');

  initDataTable();
}

// ==================== PAGINATION ====================
function renderPagination(totalUsers, page) {
  const controls = document.getElementById("pagination-controls");
  const totalPages = Math.ceil(totalUsers / CONFIG.USERS_PER_PAGE);

  if (totalPages <= 1) {
    controls.innerHTML = '';
    return;
  }

  let pages = new Set([1, totalPages, page]);
  if (page - 1 > 0) pages.add(page - 1);
  if (page + 1 <= totalPages) pages.add(page + 1);
  pages = [...pages].sort((a, b) => a - b);

  let paginationHTML = `
    <li class="page-item ${page === 1 ? 'disabled' : ''}">
      <a class="page-link" id="prev-page" href="javascript:void(0);">
        <i class="fa-solid fa-chevron-left"></i>
      </a>
    </li>`;

  let prev = null;
  pages.forEach(p => {
    if (prev && p - prev > 1) {
      paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
    }
    paginationHTML += `
      <li class="page-item ${p === page ? 'active' : ''}">
        <a class="page-link" href="javascript:void(0);" data-page="${p}">${p}</a>
      </li>`;
    prev = p;
  });

  paginationHTML += `
    <li class="page-item ${page === totalPages ? 'disabled' : ''}">
      <a class="page-link" id="next-page" href="javascript:void(0);">
        <i class="fa-solid fa-chevron-right"></i>
      </a>
    </li>`;

  controls.innerHTML = paginationHTML;
  attachPaginationEvents(totalPages);
}

function attachPaginationEvents(totalPages) {
  const controls = document.getElementById("pagination-controls");

  controls.querySelectorAll('[data-page]').forEach(btn => {
    btn.addEventListener('click', function () {
      state.currentPage = parseInt(this.dataset.page);
      renderTable(state.allUsers, state.currentPage);
    });
  });

  const prevBtn = document.getElementById("prev-page");
  if (prevBtn) {
    prevBtn.addEventListener('click', function () {
      if (state.currentPage > 1) {
        state.currentPage--;
        renderTable(state.allUsers, state.currentPage);
      }
    });
  }

  const nextBtn = document.getElementById("next-page");
  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      if (state.currentPage < totalPages) {
        state.currentPage++;
        renderTable(state.allUsers, state.currentPage);
      }
    });
  }
}

// ==================== EDIT MODAL (virtual students only) ====================
document.addEventListener('click', function (e) {
    const btn = e.target.closest('.btn-edit-virtual-user');
    if (!btn) return;

    const userId = btn.dataset.userId;   // real user id
    const rowId  = btn.dataset.id;       // linked virtual_user id (may be empty for real users with none)

    if (!rowId) {
        Swal.fire({
            icon: 'info',
            title: 'Nothing to edit',
            text: 'This student has no linked virtual profile yet.',
            confirmButtonColor: '#4c4b9e'
        });
        return;
    }

    document.getElementById('editUserId').value    = userId;
    document.getElementById('editId').value        = rowId;
    document.getElementById('editAccountId').value = btn.dataset.accountId ?? state.accountId;
    document.getElementById('editName').value       = btn.dataset.name  ?? '';
    document.getElementById('editEmail').value      = btn.dataset.email ?? '';
    document.getElementById('editPhone').value      = btn.dataset.phone ?? '';
    document.getElementById('editStatus').value     = btn.dataset.status ?? 1;

    const modal = new bootstrap.Modal(document.getElementById('editStudentModal'));
    modal.show();
});

// ==================== SHOW PROFILE (local restriction notice) ====================
document.addEventListener('click', function (e) {
    const btn = e.target.closest('.btn-show-profile-local');
    if (!btn) return;

    Swal.fire({
        icon: 'info',
        title: 'Not available locally',
        text: 'You can only view the student profile on the website, not on the local server.',
        confirmButtonColor: '#4c4b9e'
    });
});

// ==================== DELETE VIRTUAL USER ====================
document.addEventListener('click', function (e) {
    const btn = e.target.closest('.btn-delete-virtual-user');
    if (!btn) return;

    const userId    = btn.dataset.userId;    // real user id -> goes in URL
    const virtualId = btn.dataset.id;        // virtual_user row id -> goes in body
    const accountId = btn.dataset.accountId; // account id -> goes in body
    const userName  = btn.closest('tr').querySelector('.student-name h4').textContent.trim();

    Swal.fire({
        title: 'Are you sure?',
        text: `Do you really want to delete "${userName}"? This action cannot be undone.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#4c4b9e',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (!result.isConfirmed) return;

        fetch(`/api/delete-virtuel-user/${userId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                account_id: accountId,
                id: virtualId
            })
        })
        .then(res => res.json())
        .then(data => {
            state.allUsers = state.allUsers.filter(u => u.id != virtualId);
            renderTable(state.allUsers, state.currentPage);

            Swal.fire({
                title: 'Deleted!',
                text: 'User deleted successfully.',
                icon: 'success',
                confirmButtonColor: '#4c4b9e'
            });
        })
        .catch(err => {
            console.error('❌ Error deleting user:', err);
            Swal.fire({
                title: 'Error',
                text: 'Failed to delete user. Please try again.',
                icon: 'error',
                confirmButtonColor: '#4c4b9e'
            });
        });
    });
});

// ==================== CREATE VIRTUAL STUDENT ====================
document.getElementById('createVirtualStudentForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const form = this;
    const saveBtn = document.querySelector('#addStudentModal .btn-primary[form="createVirtualStudentForm"]');

    const formData = new FormData();
    formData.append('account_id', state.accountId);
    formData.append('fullName', document.getElementById('studentFullName').value.trim());
    formData.append('email', document.getElementById('studentEmail').value.trim());
    formData.append('phone', document.getElementById('studentPhone').value.trim());
    formData.append('status', document.getElementById('studentStatus').value);

    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';

    fetch(`/api/create_virtuel_user`, {
        method: 'POST',
        body: formData
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
        if (!ok) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.Message || 'Failed to create student.',
                confirmButtonColor: '#4c4b9e'
            });
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById('addStudentModal')).hide();
        form.reset();

        Swal.fire({
            icon: 'success',
            title: 'Created!',
            text: data.Message || 'Student created successfully.',
            confirmButtonColor: '#4c4b9e'
        }).then(() => {
            window.location.reload(); // simplest way to refresh the table with the new row
        });
    })
    .catch(err => {
        console.error('❌ Error creating student:', err);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Failed to create student. Please try again.',
            confirmButtonColor: '#4c4b9e'
        });
    })
    .finally(() => {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save Student';
    });
});

// ==================== SAVE EDIT VIRTUAL STUDENT ====================
document.getElementById('editStudentForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const id     = document.getElementById('editId').value;     // virtual_user row id
    const userId = document.getElementById('editUserId').value; // linked real user id

    const payload = {
        id:        id,
        userId:    userId,
        accountId: state.accountId,
        name:   document.getElementById('editName').value.trim()  || null,
        email:  document.getElementById('editEmail').value.trim() || null,
        phone:  document.getElementById('editPhone').value.trim() || null,
        status: parseInt(document.getElementById('editStatus').value)
    };

    const saveBtn = this.querySelector('button[type="submit"]');
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';

    fetch(`/api/update-virtual-student`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        window.location.reload(); // ✅ just reload — server re-renders with fresh data
    })
    .catch(err => {
        console.error('❌ Error updating user:', err);
        alert('❌ Failed to update user. Please try again.');
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save';
    });
});

// ==================== ASSOCIATE VIRTUAL USER MODAL ====================
document.addEventListener('click', function (e) {
    const btn = e.target.closest('.btn-associate-virtual-user');
    if (!btn) return;

    const virtualUserId = btn.dataset.userId;
    const virtualId      = btn.dataset.id;
    const accountId       = btn.dataset.accountId ?? state.accountId;

    document.getElementById('virtualId').value       = virtualId;
    document.getElementById('virtualUserId').value   = virtualUserId;

    const select = document.getElementById('realUserSelect');
    select.innerHTML = `<option value="" disabled selected>Loading students...</option>`;
    $(select).selectpicker('refresh');

    const modal = new bootstrap.Modal(document.getElementById('associateVirtualUserModal'));
    modal.show();

    // Fetch real students from the API instead of using state.allUsers
    fetch('/api/get_students_with_sessions')
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            if (!ok) {
                select.innerHTML = `<option value="" disabled selected>Failed to load students</option>`;
                $(select).selectpicker('refresh');
                return;
            }

            const students = Array.isArray(data) ? data : (data.students ?? []);

            select.innerHTML = `<option value="" disabled selected>-- Select a student --</option>` +
                students.map(u =>
                    `<option value="${u.id}">${u.username ?? '-'} (${u.email ?? '-'})</option>`
                ).join('');

            $(select).selectpicker('refresh');
        })
        .catch(err => {
            console.error('❌ Error loading students:', err);
            select.innerHTML = `<option value="" disabled selected>Failed to load students</option>`;
            $(select).selectpicker('refresh');
        });
});

// ==================== SAVE ASSOCIATE VIRTUAL USER ====================
document.getElementById('associateVirtualUserForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const virtualId     = document.getElementById('virtualId').value;
    const virtualUserId = document.getElementById('virtualUserId').value;
    const realUserId    = document.getElementById('realUserSelect').value;

    if (!realUserId) {
        Swal.fire({
            icon: 'warning',
            title: 'No student selected',
            text: 'Please select a real student to associate.',
            confirmButtonColor: '#4c4b9e'
        });
        return;
    }

    // ✅ Alert showing the selected virtual id and real user id
    alert(`Virtual ID: ${virtualId}\nSelected Real User ID: ${realUserId}`);

    const payload = {
        id: virtualId,
        realUserId: realUserId
    };

    const saveBtn = document.querySelector('#associateVirtualUserModal .btn-outline-primary[form="associateVirtualUserForm"]');
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';

    fetch(`/api/associate_virtueluser/${state.accountId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
        if (!ok) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.Message || data.message || 'Failed to associate student.',
                confirmButtonColor: '#4c4b9e'
            });
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById('associateVirtualUserModal')).hide();

        Swal.fire({
            icon: 'success',
            title: 'Associated!',
            text: data.Message || data.message || 'Student associated successfully.',
            confirmButtonColor: '#4c4b9e'
        }).then(() => {
            window.location.reload();
        });
    })
    .catch(err => {
        console.error('❌ Error associating student:', err);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Failed to associate student. Please try again.',
            confirmButtonColor: '#4c4b9e'
        });
    })
    .finally(() => {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Associate';
    });
});
// ==================== SESSIONS (all sessions for dropdown) ====================
let cachedSessions = [];

async function fetchSessions() {
    if (cachedSessions.length > 0) return cachedSessions;
    try {
        const response = await fetch(`/api/get-sessions/${state.accountId}`);
        const result   = await response.json();

        if (Array.isArray(result)) {
            cachedSessions = result;
        } else if (Array.isArray(result.data)) {
            cachedSessions = result.data;
        } else if (Array.isArray(result.data?.data)) {
            cachedSessions = result.data.data;
        } else {
            cachedSessions = [];
        }

        return cachedSessions;
    } catch (err) {
        console.error('❌ Error fetching sessions:', err);
        return [];
    }
}

function buildSessionOptions(sessions) {
    return `<option value="" disabled selected>-- Select a session --</option>` +
        sessions.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
}

function buildSessionCard(index, sessions) {
    return `
        <div class="relation-block border rounded p-3 mb-3" data-index="${index}">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0">New Relation #${index}</h6>
                <button type="button" class="btn btn-sm btn-danger removeRelationBtn">Remove</button>
            </div>
            <div class="mb-3">
                <label class="form-label">Select Session</label>
                <select name="sessions[]" class="form-control sessionSelect" required data-live-search="true">
                    ${buildSessionOptions(sessions)}
                </select>
            </div>
        </div>`;
}

// ==================== ASSIGNED SESSIONS ====================
// NOTE: this always takes the virtual_user row id when isVirtual is true — the
// get_assigned_session_user Flask endpoint resolves virtual -> real user internally.
async function fetchAssignedSessions(id, isVirtual, accountId) {
    try {
        const response = await fetch(`/api/get_assigned_session_user/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
             is_virtual: isVirtual,
             account_id: accountId
              })
        });
        const result = await response.json();
        return result.data ?? [];
    } catch (err) {
        console.error('❌ Error fetching assigned sessions:', err);
        return [];
    }
}

function buildAssignedSessionCard(session) {
    return `
        <div class="relation-block border rounded p-3 mb-3" data-session-id="${session.id}" data-assigned="true">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">${session.name}</h6>
                    <span class="badge bg-success">Assigned</span>
                </div>
                <button type="button" class="btn btn-sm btn-danger removeAssignedSessionBtn" data-session-id="${session.id}">
                    Delete
                </button>
            </div>
        </div>`;
}

function renderSessionRelations(assignedSessions, allSessions) {
    const container = document.getElementById('relationsContainer');
    const assignedIds = new Set(assignedSessions.map(s => s.id));
    const availableSessions = allSessions.filter(s => !assignedIds.has(s.id));

    const assignedHtml = assignedSessions.map(buildAssignedSessionCard).join('');
    const newRelationHtml = buildSessionCard(assignedSessions.length + 1, availableSessions);

    container.innerHTML = assignedHtml + newRelationHtml;
}

// ==================== MANAGE SESSIONS MODAL ====================
document.addEventListener('click', async function (e) {

    // Open modal
    const openBtn = e.target.closest('.btn-manage-sessions-virtual-user');
    if (openBtn) {
        const realId = openBtn.dataset.userId; // real user id — the only id this button provides now

        if (!realId) {
            console.error('❌ Manage Sessions button missing data-user-id');
            return;
        }

        document.getElementById('sessionUserId').value = realId;

        const modalEl = document.getElementById('manageSessionsModal');
        modalEl.dataset.realUserId = realId;
        modalEl.dataset.accountId  = state.accountId;

        const container = document.getElementById('relationsContainer');
        container.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border text-primary" role="status"></div>
            </div>`;

        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        try {
            const [assignedSessions, allSessions] = await Promise.all([
                fetchAssignedSessions(realId, false, state.accountId), // real id — is_virtual no longer relevant here
                fetchSessions()
            ]);
            renderSessionRelations(assignedSessions, allSessions);
        } catch (err) {
            console.error('❌ Error loading assigned sessions:', err);
            container.innerHTML = `<div class="alert alert-danger">Failed to load sessions.</div>`;
        }
        return;
    }

    // Remove a "new relation" select card
    const removeBtn = e.target.closest('.removeRelationBtn');
    if (removeBtn) {
        removeBtn.closest('.relation-block').remove();
    }

    // Delete an already-assigned session
    const deleteAssignedBtn = e.target.closest('.removeAssignedSessionBtn');
    if (deleteAssignedBtn) {
        const sessionId = deleteAssignedBtn.dataset.sessionId;
        const modalEl = document.getElementById('manageSessionsModal');
        const userId = modalEl.dataset.realUserId; // real user id — matches what the endpoint expects

        const result = await Swal.fire({
            title: 'Remove this session?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, remove it',
            cancelButtonText: 'Cancel',
            confirmButtonColor: '#4c4b9e',
            cancelButtonColor: '#d33'
        });
        if (!result.isConfirmed) return;

        try {
            const res = await fetch(`/api/delete_user_session/${userId}/${sessionId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();

            if (!res.ok) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.Message || 'Failed to remove session.',
                    confirmButtonColor: '#4c4b9e'
                });
                return; // don't remove the card if the server call failed
            }

            deleteAssignedBtn.closest('.relation-block').remove();
        } catch (err) {
            console.error('❌ Error deleting session relation:', err);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Failed to remove session. Please try again.',
                confirmButtonColor: '#4c4b9e'
            });
        }
    }

    // Add new relation card
    const addBtn = e.target.closest('#addRelationBtn');
    if (addBtn) {
        const container = document.getElementById('relationsContainer');
        const assignedIds = new Set(
            [...container.querySelectorAll('[data-assigned="true"]')].map(el => el.dataset.sessionId)
        );
        const allSessions = await fetchSessions();
        const availableSessions = allSessions.filter(s => !assignedIds.has(String(s.id)));
        const index = container.querySelectorAll('.relation-block').length + 1;
        container.insertAdjacentHTML('beforeend', buildSessionCard(index, availableSessions));
    }

});

// ==================== SAVE MANAGE SESSIONS ====================
document.getElementById('manageSessionsForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const modalEl = document.getElementById('manageSessionsModal');
    const userId  = document.getElementById('sessionUserId').value; // ✅ real user id (fixed)

    // Only take NEW (not-yet-assigned) selects — assigned ones are plain divs, not selects
    const selects = document.querySelectorAll('#relationsContainer .sessionSelect');
    const sessionIds = Array.from(selects)
        .map(s => s.value)
        .filter(Boolean);

    if (sessionIds.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'No session selected',
            text: 'Please select at least one session before saving.',
            confirmButtonColor: '#4c4b9e'
        });
        return;
    }

    const saveBtn = document.querySelector('#manageSessionsModal .btn-primary[form="manageSessionsForm"]');
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';

    // Fire one request per selected session, sequentially
    (async () => {
        const results = [];
        for (const sessionId of sessionIds) {
            try {
                const res = await fetch(`/api/assign_user_session/${userId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: state.accountId,          // ✅ fixed (was bare `accountId`)
                        session_id: parseInt(sessionId)
                    })
                });
                const data = await res.json();
                results.push({ sessionId, ok: res.ok, data });
            } catch (err) {
                results.push({ sessionId, ok: false, data: { Message: err.message } });
            }
        }
        return results;
    })()
    .then(results => {
        const failed = results.filter(r => !r.ok);

        if (failed.length === 0) {
            bootstrap.Modal.getInstance(modalEl).hide();
            Swal.fire({
                icon: 'success',
                title: 'Sessions assigned',
                text: 'All selected sessions were assigned successfully.',
                confirmButtonColor: '#4c4b9e'
            });
        } else {
            const failedMsgs = failed.map(r => `Session ${r.sessionId}: ${r.data.Message || 'Failed'}`).join('\n');
            Swal.fire({
                icon: 'error',
                title: 'Some sessions failed',
                text: failedMsgs,
                confirmButtonColor: '#4c4b9e'
            });
        }
    })
    .finally(() => {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save';
    });
});

// ==================== INIT ====================
function initPage() {
  loadTableUsers(state.accountId);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPage);
} else {
  initPage();
}