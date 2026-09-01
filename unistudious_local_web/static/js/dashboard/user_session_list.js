/* ===============================================================
   USER SESSION LIST PAGE
   Handles the "Lists Users" table on the show-all-user-session
   page: loading users for a session, rendering the DataTable,
   and wiring up the group/completion-tag/virtual-user modals.
   =============================================================== */

/**
 * Waits for the global jQuery object to be available before running
 * the rest of this file. Needed because this script is loaded via a
 * component template, and depending on how that component is
 * rendered/injected, jQuery from the base layout might not be fully
 * attached to `window` yet at the exact moment this file executes.
 *
 * Usage: waitForJQuery(function($) { ...your code... });
 */
function waitForJQuery(callback) {
    if (window.jQuery) {
        callback(window.jQuery);
        return;
    }

    var attempts = 0;
    var maxAttempts = 50; // ~5 seconds at 100ms intervals

    var interval = setInterval(function() {
        attempts++;

        if (window.jQuery) {
            clearInterval(interval);
            callback(window.jQuery);
        } else if (attempts > maxAttempts) {
            clearInterval(interval);
            console.error('❌ jQuery never became available — check script load order.');
        }
    }, 100);
}

// Explicit call (no reliance on automatic-semicolon-insertion tricks) —
// everything below only runs once jQuery is confirmed to exist.
waitForJQuery(function($) {

    // ==================== STATE ====================
    // Central place for page-level data. `sessionId` comes from the
    // template via `window.SESSION_ID`; `allUsers` holds the last
    // fetched list so we can re-render without re-fetching if needed.
    const state = {
        sessionId: window.SESSION_ID,
        allUsers: []
    };

    // ==================== DATATABLE INIT ====================
    let dataTableInstance = null;

    /**
     * (Re)initializes the DataTable on #example. Always destroys any
     * existing instance first so we don't get "table already
     * initialized" errors when reloading data.
     */
    function initDataTable() {
        if ($.fn.DataTable.isDataTable('#example')) {
            $('#example').DataTable().destroy();
            dataTableInstance = null;
        }

        dataTableInstance = $('#example').DataTable({
            paging: true,
            pageLength: 10,
            searching: true,
            lengthChange: true,
            language: {
                emptyTable: "No data available",
                paginate: {
                    next: '<i class="fa-solid fa-angle-right"></i>',
                    previous: '<i class="fa-solid fa-angle-left"></i>'
                }
            },
            createdRow: function(row) {
                $(row).addClass('selected');
            },
            drawCallback: function() {
                stylePaginationButtons();
            }
        });
    }

    /**
     * Applies custom inline styling to the DataTables pagination
     * buttons (rounded, purple-accent design) since we can't easily
     * do this with plain CSS overrides on the generated markup.
     */
    function stylePaginationButtons() {
        const paginate = document.querySelector('#example_wrapper .dataTables_paginate');
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

    // ==================== API ====================
    // Wraps every network call this page makes. Keeps fetch logic
    // separate from rendering logic.
    const API = {
        /** Fetches the list of users enrolled in the given session. */
        async fetchUserSessionData(sessionId) {
            const response = await fetch(`/api/get_user_session_info/${sessionId}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const result = await response.json();
            return result.Data ?? [];
        },

        /** Removes a user from a session (relation_user_session row). */
        async deleteUserSession(userId, sessionId) {
            const response = await fetch(`/api/delete_user_session/${userId}/${sessionId}`, {
                method: 'POST'
            });
            return response.json();
        }
    };

    // ==================== HELPERS ====================

    /**
     * Safely converts a value to a string for use inside an HTML
     * attribute, escaping double quotes and handling null/undefined.
     */
    function safeAttr(val) {
        return (val === undefined || val === null) ? '' : String(val).replace(/"/g, '&quot;');
    }

    /**
     * Safely JSON-stringifies a user's extra_data field for embedding
     * in a data-* attribute. Falls back to '[]' for any value that
     * JSON.stringify can't serialize (undefined, functions, symbols),
     * since JSON.stringify silently returns `undefined` in those
     * cases instead of throwing.
     */
    function safeExtraDataJson(extraData) {
        let json = JSON.stringify(extraData);
        if (typeof json !== 'string') json = '[]';
        return json.replace(/'/g, "&#39;");
    }

    // ==================== TABLE ====================

    /**
     * Fetches users for the given session and renders them into the
     * table. Shows an error message in the table body on failure.
     */
    async function loadTableUsers(sessionId) {
        const tbody = document.querySelector('#example tbody');
        if (!tbody) {
            console.error("❌ #example tbody not found in DOM");
            return;
        }

        try {
            const users = await API.fetchUserSessionData(sessionId);
            state.allUsers = users;
            renderTable(state.allUsers);
        } catch (error) {
            console.error("❌ Error loading table users:", error);

            if ($.fn.DataTable.isDataTable('#example')) {
                $('#example').DataTable().destroy();
                dataTableInstance = null;
            }

            tbody.innerHTML = `
                <tr>
                    <td colspan="4">
                        <div class="alert alert-danger m-3">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i>
                            Failed to load users. Please try again.
                        </div>
                    </td>
                </tr>`;
            initDataTable();
        }
    }

    /**
     * Builds and injects the table rows for the given list of users,
     * then (re)initializes the DataTable on top of them.
     */
    function renderTable(users) {
        const tbody = document.querySelector('#example tbody');

        if ($.fn.DataTable.isDataTable('#example')) {
            $('#example').DataTable().destroy();
            dataTableInstance = null;
        }

        if (!users.length) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center">No data available</td></tr>`;
            initDataTable();
            return;
        }

        tbody.innerHTML = users.map(user => {
            const extraDataJson = safeExtraDataJson(user.extra_data);

            return `
                <tr>
                    <td>${safeAttr(user.username)}</td>

                    <td>
                        <div class="d-flex align-items-center">
                            <a class="edit-group-action btn btn-sm btn-outline-success me-2"
                               data-bs-toggle="modal" data-bs-target="#actionGroupModal"
                               data-user-id="${user.user_id}" data-session-id="${user.session_id}"
                               style="cursor:pointer">
                                <i class="fas fa-pencil-alt"></i> Edit
                            </a>
                            <div>${user.relation_group_local_session_id || 'N/A'}</div>
                        </div>
                    </td>

                    <td>
                        <div class="d-flex align-items-center">
                            <a class="edit-completion-tag-action btn btn-sm btn-outline-success me-2"
                               data-bs-toggle="modal" data-bs-target="#actionCompletionTagModal"
                               data-user-id="${user.user_id}" data-session-id="${user.session_id}"
                               style="cursor:pointer">
                                <i class="fas fa-pencil-alt"></i> Edit
                            </a>
                            <div>N/A</div>
                        </div>
                    </td>

                    <td>
                        <div class="d-flex gap-2">
                            <a class="delete-relation-user-session btn btn-rounded btn-outline-danger btn-sm"
                               style="cursor:pointer"
                               data-user-id="${user.user_id}" data-session-id="${user.session_id}">
                                <i class="fa fa-trash"></i> delete
                            </a>
                            <a class="edit-virtual-user-session btn btn-rounded btn-outline-success btn-sm"
                               style="cursor:pointer" data-bs-toggle="modal" data-bs-target="#editVirtualUserSessionModal"
                               data-user-id="${user.user_id}" data-session-id="${user.session_id}"
                               data-user-name="${safeAttr(user.name)}" data-user-phone="${safeAttr(user.phone)}"
                               data-user-email="${safeAttr(user.email)}" data-extra-data-json='${extraDataJson}'>
                                <i class="fa fa-eye"></i> View
                            </a>
                        </div>
                    </td>
                </tr>`;
        }).join('');

        initDataTable();
    }

    // ==================== ACTION GROUP MODAL ====================
    // Toggles which sub-fields are visible inside the "Edit Groups"
    // modal depending on the chosen action (join / change / remove).
    $('#actionSelect').on('change', function() {
        var val = $(this).val();
        $('#dynamicGroupSelect').toggle(val === 'join');
        $('#currentGroupContainer').toggle(val === 'change');
        $('#preferredGroupWrapper').toggle(val === 'change');
        $('#currentGroupRemoveWrapper').toggle(val === 'remove');
    });

    // Stores which user/session the modal was opened for, so the
    // "Confirm" button handler knows what to act on.
    $('#actionGroupModal').on('show.bs.modal', function(e) {
        var trigger = e.relatedTarget;
        if (!trigger) return;
        $(this).data('userId', $(trigger).data('user-id'));
        $(this).data('sessionId', $(trigger).data('session-id'));
    });

    // ==================== DELETE RELATION ====================
    // Removes a user from the current session after confirmation.
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.delete-relation-user-session');
        if (!btn) return;

        const userId = btn.dataset.userId;
        const sessionId = btn.dataset.sessionId;

        Swal.fire({
            title: 'Are you sure?',
            text: 'This will delete the user from this session and cannot be undone!',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'Cancel'
        }).then((result) => {
            if (!result.isConfirmed) return;

            API.deleteUserSession(userId, sessionId)
                .then(data => {
                    Swal.fire({
                        title: 'Deleted!',
                        text: data.Message,
                        icon: 'success',
                        timer: 2000,
                        showConfirmButton: false
                    });
                    loadTableUsers(state.sessionId); // refresh the table
                })
                .catch(error => {
                    Swal.fire('Error!', 'Something went wrong.', 'error');
                });
        });
    });

    // ==================== INIT ====================

    /** Entry point: loads the table data once we have a session id. */
    function initPage() {
        if (state.sessionId) {
            loadTableUsers(state.sessionId);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPage);
    } else {
        initPage();
    }

}); // end waitForJQuery callback