/**
 * =====================================================================
 *  GROUP CONFIGURATION PAGE — MAIN SCRIPT
 * =====================================================================
 *  Handles:
 *    - Loading groups & unaffected users
 *    - Drag & drop assignment of users to groups
 *    - Removing (disaffecting) a user from a group
 *    - Creating / editing / deleting groups
 *    - Dynamic Subject/Teacher relation rows in the "Add Group" form
 * =====================================================================
 */


/* =====================================================================
 * SECTION 1: LOAD GROUPS
 * ===================================================================== */
let groupsDataMap = {};

async function loadGroupsToGroupConfig(accountId, sessionId) {
    const container = document.getElementById('group-container');

    if (!container) {
        return;
    }

    try {
        const response = await fetch(`/api/get-group/${sessionId}/${accountId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        container.innerHTML = '';

        if (result.Message === "Success" && result.data && result.data.length > 0) {
            groupsDataMap = {};

            result.data.forEach((group) => {
                groupsDataMap[group.id] = group;
                const groupCard = createGroupCard(group);
                container.innerHTML += groupCard;
            });

            container.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(el => {
                new bootstrap.Dropdown(el);
            });
        } else {
            container.innerHTML = '<div class="col-12 text-center py-5"><p>No groups found.</p></div>';
            console.log('No groups found or error occurred');
        }

    } catch (error) {
        console.error('Error loading groups:', error);
        container.innerHTML = '<div class="col-12 text-center py-5"><p class="text-danger">Error loading groups.</p></div>';
    }
}


/* =====================================================================
 * SECTION 2: GROUP CARD RENDERING
 * ===================================================================== */
function createGroupCard(group) {
    const studentItems = group.list_student.map(student => `
        <div class="user-item-session" data-id="${student.relation_id}" data-session-id="${group.session_id}" data-user-id="${student.user_id}">
            ${student.full_name}
            <button class="btn btn-xs btn-danger remove-user-session">x</button>
        </div>
    `).join('');

    return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card contact_list text-center group-card">
                <div class="card-body">
                    <div class="user-content-session" data-group-id="${group.id}">

                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div class="user-details text-start">
                                <h4 class="user-name mb-0">${group.name}</h4>
                                    <p class="mb-0 text-muted group-capacity-text">
                                        Capacity: ${group.list_student.length}/${group.capacity}
                                    </p>
                            </div>

                            <div class="dropdown">
                                <button class="btn sharp btn-light"
                                        type="button"
                                        data-bs-toggle="dropdown"
                                        aria-expanded="false">
                                        <svg width="24" height="6" viewBox="0 0 24 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M12.0012 0.359985C11.6543 0.359985 11.3109 0.428302 10.9904 0.561035C10.67 0.693767 10.3788 0.888317 10.1335 1.13358C9.88829 1.37883 9.69374 1.67 9.56101 1.99044C9.42828 2.31089 9.35996 2.65434 9.35996 3.00119C9.35996 3.34803 9.42828 3.69148 9.56101 4.01193C9.69374 4.33237 9.88829 4.62354 10.1335 4.8688C10.3788 5.11405 10.67 5.3086 10.9904 5.44134C11.3109 5.57407 11.6543 5.64239 12.0012 5.64239C12.7017 5.64223 13.3734 5.36381 13.8686 4.86837C14.3638 4.37294 14.6419 3.70108 14.6418 3.00059C14.6416 2.3001 14.3632 1.62836 13.8677 1.13315C13.3723 0.637942 12.7004 0.359826 12 0.359985H12.0012ZM3.60116 0.359985C3.25431 0.359985 2.91086 0.428302 2.59042 0.561035C2.26997 0.693767 1.97881 0.888317 1.73355 1.13358C1.48829 1.37883 1.29374 1.67 1.16101 1.99044C1.02828 2.31089 0.959961 2.65434 0.959961 3.00119C0.959961 3.34803 1.02828 3.69148 1.16101 4.01193C1.29374 4.33237 1.48829 4.62354 1.73355 4.8688C1.97881 5.11405 2.26997 5.3086 2.59042 5.44134C2.91086 5.57407 3.25431 5.64239 3.60116 5.64239C4.30165 5.64223 4.97339 5.36381 5.4686 4.86837C5.9638 4.37294 6.24192 3.70108 6.24176 3.00059C6.2416 2.3001 5.96318 1.62836 5.46775 1.13315C4.97231 0.637942 4.30045 0.359826 3.59996 0.359985H3.60116ZM20.4012 0.359985C20.0543 0.359985 19.7109 0.428302 19.3904 0.561035C19.07 0.693767 18.7788 0.888317 18.5336 1.13358C18.2883 1.37883 18.0937 1.67 17.961 1.99044C17.8283 2.31089 17.76 2.65434 17.76 3.00119C17.76 3.34803 17.8283 3.69148 17.961 4.01193C18.0937 4.33237 18.2883 4.62354 18.5336 4.8688C18.7788 5.11405 19.07 5.3086 19.3904 5.44134C19.7109 5.57407 20.0543 5.64239 20.4012 5.64239C21.1017 5.64223 21.7734 5.36381 22.2686 4.86837C22.7638 4.37294 23.0419 3.70108 23.0418 3.00059C23.0416 2.3001 22.7632 1.62836 22.2677 1.13315C21.7723 0.637942 21.1005 0.359826 20.4 0.359985H20.4012Z" fill="#A098AE"></path>
                                        </svg>
                                </button>

                                <ul class="dropdown-menu dropdown-menu-end">
                                    <li>
                                        <a class="dropdown-item delete-group"
                                           href="javascript:void(0);"
                                           data-id="${group.id}">
                                            Delete
                                        </a>
                                    </li>
                                    <li>
                                        <a class="dropdown-item edit-group"
                                           href="javascript:void(0);"
                                           data-id="${group.id}"
                                           data-name="${group.name}"
                                           data-capacity="${group.capacity}"
                                           data-bs-toggle="modal"
                                           data-bs-target="#groupUpdateModal">
                                            Edit
                                        </a>
                                    </li>
                                    <li>
                                        <a class="dropdown-item show-student"
                                           href="javascript:void(0);"
                                           data-id="${group.id}"
                                           data-name="${group.name}"
                                           data-capacity="${group.capacity}"
                                           data-bs-toggle="modal"
                                           data-bs-target="#groupShowStudentModal">
                                            Show students
                                        </a>
                                    </li>
                                </ul>
                            </div>
                        </div>

                        <div class="droppable-area-session ui-droppable"
                             style="max-height: 250px !important; overflow-y: auto;"
                             data-group-id="${group.id}"
                             data-capacity="${group.capacity}">

                            ${studentItems || `
                                <p class="text-muted text-center mb-0">
                                    No students in this group
                                </p>
                            `}
                        </div>

                    </div>
                </div>
            </div>
        </div>
    `;
}


/* =====================================================================
 * SECTION 3: REMOVE (DISAFFECT) USER FROM GROUP
 * ===================================================================== */
$(document).on('click', '.remove-user-session', async function () {
    const userItemDiv = $(this).closest('.user-item-session');

    const sessionId = userItemDiv.data('session-id');
    const userId = userItemDiv.data('user-id');
    const groupId = userItemDiv.closest('.droppable-area-session').data('group-id');

    if (!groupId || !userId || !sessionId) {
        alert('Missing required data to remove user from group');
        return;
    }

    try {
        const response = await fetch(`/api/disaffect_user_group/${sessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                group_id: groupId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const capacityText = userItemDiv.closest('.user-content-session').find('.group-capacity-text');
        const [current, max] = capacityText.text().replace('Capacity:', '').trim().split('/').map(Number);
        capacityText.text(`Capacity: ${Math.max(current - 1, 0)}/${max}`);

        userItemDiv.remove();

        const accountId = window.ACCOUNT_ID;
        await loadUsersNotAffected(sessionId, accountId);

    } catch (error) {
        console.error('Error deleting user from group:', error);
        alert('Failed to remove user from group');
    }
});


/* =====================================================================
 * SECTION 4: DELETE GROUP
 * ===================================================================== */

$(document).on('click', '.delete-group', function (e) {
    e.preventDefault();
    const groupId = $(this).data('id');

    Swal.fire({
        title: 'Are you sure?',
        text: 'This Group will be deleted permanently. You will not be able to undo this action.',
        icon: 'error',
        showCancelButton: true,
        confirmButtonColor: '#dd3333',
        cancelButtonColor: '#64c5b1',
        confirmButtonText: 'Yes, delete it.',
        cancelButtonText: 'No, cancel.',
        width: '500px',
        padding: '20px'
    }).then((result) => {
        if (result.isConfirmed) {
            deleteGroup(groupId);
        }
    });
});

function deleteGroup(groupId) {
    $.ajax({
        url: `/api/delete-group/${groupId}`,
        type: 'DELETE',
        headers: {
            'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
        },
        success: function (response) {
            Swal.fire({
                title: 'Deleted!',
                text: 'Group has been deleted successfully.',
                icon: 'success',
                confirmButtonColor: '#64c5b1',
                timer: 2000,
                showConfirmButton: false
            });

            $(`.user-content-session[data-group-id="${groupId}"]`)
                .closest('.col-md-6, .col-lg-4')
                .fadeOut(300, function () {
                    $(this).remove();
                });
        },
        error: function (xhr, status, error) {
            Swal.fire({
                title: 'Error!',
                text: 'Failed to delete the group. Please try again.',
                icon: 'error',
                confirmButtonColor: '#dd3333'
            });
        }
    });
}


/* =====================================================================
 * SEARCH GROUPS BY NAME
 * ===================================================================== */
$(document).on('keyup', '#filtre-group', function () {
    const query = $(this).val().toLowerCase().trim();
    const container = $('#group-container');

    const cards = container.find('.group-card').closest('.col-md-6, .col-lg-4').get();

    cards.sort((a, b) => {
        const nameA = $(a).find('.user-name').text().toLowerCase();
        const nameB = $(b).find('.user-name').text().toLowerCase();

        const matchA = nameA.includes(query);
        const matchB = nameB.includes(query);

        if (matchA && !matchB) return -1;
        if (!matchA && matchB) return 1;
        return 0;
    });

    cards.forEach(card => container.append(card));

    container.find('.group-card').each(function () {
        const groupName = $(this).find('.user-name').text().toLowerCase();
        $(this).closest('.col-md-6, .col-lg-4').toggle(groupName.includes(query));
    });
});


/* =====================================================================
 * MANUAL DROPDOWN TOGGLE (GROUP CARDS ONLY)
 * ===================================================================== */
$(document).on('click', '.user-content-session .dropdown > .btn.sharp', function (e) {
    e.preventDefault();
    e.stopPropagation();

    const menu = $(this).siblings('.dropdown-menu');
    const isOpen = menu.hasClass('show');

    $('.user-content-session .dropdown-menu.show').removeClass('show');

    if (!isOpen) {
        menu.addClass('show');
    }
});

$(document).on('click', function (e) {
    if (!$(e.target).closest('.user-content-session .dropdown').length) {
        $('.user-content-session .dropdown-menu.show').removeClass('show');
    }
});


/* =====================================================================
 * SHARED STATE + HELPERS FOR SUBJECT/TEACHER DROPDOWNS
 * (Top-level so both Section 6 and Section 11 can use them)
 * ===================================================================== */

let relationIndex = 0;
let subjectsData = [];
let teachersData = [];
let subjectsLoaded = false;
let teachersLoaded = false;

function getSubjectOptions() {
    if (subjectsData.length === 0) {
        return '<option value="" selected="selected">No subjects available</option>';
    }

    let options = '<option value="" selected="selected">Choose the Subject...</option>';
    subjectsData.forEach(subject => {
        options += `<option value="${subject.id}">${subject.subject_name}</option>`;
    });
    return options;
}

function getTeacherOptions() {
    if (teachersData.length === 0) {
        return '<option value="" selected="selected">No teachers available</option>';
    }

    let options = '<option value="" selected="selected">Choose the Teacher...</option>';
    teachersData.forEach(teacher => {
        const teacherName = teacher.full_name || teacher.username || teacher.email || 'Unknown';
        options += `<option value="${teacher.user_id}">${teacherName}</option>`;
    });
    return options;
}

function addRelationItem(relation = null) {
    const selectedSubject = relation ? String(relation.subject_id) : '';
    const selectedTeacher = relation ? String(relation.teacher_id) : '';
    const relationId = relation ? relation.id : '';   // <-- NEW

    const relationForm = `
        <div class="form-group relation-item mb-3 p-3 border rounded" data-relation-id="${relationId}">
            <div class="mb-3">
                <label class="form-label">Subject</label>
                <select class="form-control relation-subject">
                    ${getSubjectOptions()}
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Teacher</label>
                <select class="form-control relation-teacher">
                    ${getTeacherOptions()}
                </select>
            </div>
            <button type="button" class="btn btn-danger remove-relation" style="width: 100%;">
                Remove
            </button>
        </div>
    `;

    $('#relation-collection').append(relationForm);

    if (relation) {
        const $lastItem = $('#relation-collection .relation-item').last();
        $lastItem.find('.relation-subject').val(selectedSubject);
        $lastItem.find('.relation-teacher').val(selectedTeacher);
    }
}




$(document).on('click', '#updateGroupBtn', async function () {
    const groupId = $('#groupId').val();
    const groupName = $('#groupName').val().trim();
    const groupCapacity = $('#groupCapacity').val();

    if (!groupName || !groupCapacity) {
        alert('Please fill in all required fields');
        return;
    }

    const relations = [];
    $('#relation-collection .relation-item').each(function () {
        const subjectId = $(this).find('.relation-subject').val();
        const teacherId = $(this).find('.relation-teacher').val();
        const relationId = $(this).data('relation-id');   // <-- NEW

        if (subjectId && teacherId) {
            relations.push({
                relation_id: relationId ? parseInt(relationId) : null,  // <-- NEW
                subject_id: parseInt(subjectId),
                teacher_id: parseInt(teacherId)
            });
        }
    });

    const payload = {
        group_name: groupName,
        capacity: parseInt(groupCapacity),
        relations: relations
    };

    try {
        const response = await fetch(`/api/update-group/${groupId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
            $('#groupUpdateModal').modal('hide');
            location.reload();
        } else {
            alert('Error: ' + (result.Message || 'Failed to update group'));
        }
    } catch (error) {
        console.error('Error updating group:', error);
        alert('Failed to update group');
    }
});


/* =====================================================================
 * SECTION 5: DELETE STUDENT (FROM "SHOW STUDENTS" MODAL)
 * ===================================================================== */
$(document).on('click', '.delete-student', function (e) {
    e.preventDefault();
    const relationId = $(this).data('id');
});


/* =====================================================================
 * SECTION 6: EDIT GROUP
 * ===================================================================== */
$(document).on('click', '.edit-group', function (e) {
    const groupId = $(this).data('id');
    const groupName = $(this).data('name');
    const groupCapacity = $(this).data('capacity');

    $('#groupId').val(groupId);
    $('#groupName').val(groupName);
    $('#groupCapacity').val(groupCapacity);

    $('#relation-collection').empty();

    function renderRelations() {
        const group = groupsDataMap[groupId];
        const relations = group && group.relations ? group.relations : [];

        if (relations.length > 0) {
            relations.forEach(relation => {
                addRelationItem(relation);
            });
        } else {
            addRelationItem();
        }
    }

    // Wait for subjects/teachers dropdown data before building the selects,
    // otherwise there's nothing for .val() to match against.
    if (subjectsLoaded && teachersLoaded) {
        renderRelations();
    } else {
        const waitForData = setInterval(() => {
            if (subjectsLoaded && teachersLoaded) {
                clearInterval(waitForData);
                renderRelations();
            }
        }, 100);
    }
});

$(document).on('click', '#add-relation', function (e) {
    e.preventDefault();
    addRelationItem();
});

/* =====================================================================
 * SECTION 7: SHOW STUDENTS MODAL
 * ===================================================================== */
$(document).on('click', '.show-student', function (e) {
    e.preventDefault();

    const groupId = $(this).data('id');
    const groupName = $(this).data('name');

    $('#groupShowStudentModalLabel').text(`Students - ${groupName}`);
    $('#students-list').empty();

    const groupCard = $(`.user-content-session[data-group-id="${groupId}"]`);
    const students = groupCard.find('.user-item-session');

    if (students.length > 0) {
        students.each(function () {
            const studentName = $(this).text().trim().replace('x', '').trim();
            const relationId = $(this).data('id');
            const sessionId = $(this).data('session-id');
            const userId = $(this).data('user-id');

            const studentItem = `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    ${studentName}
                    <button class="btn btn-danger btn-sm delete-student"
                            data-session-id="${sessionId}"
                            data-user-id="${userId}"
                            data-id="${relationId}"
                            data-name="${studentName}"
                            data-group-id="${groupId}">
                        Delete
                    </button>
                </li>
            `;
            $('#students-list').append(studentItem);
        });
    } else {
        $('#students-list').html('<li class="list-group-item text-center text-muted">No students in this group</li>');
    }
});


/* =====================================================================
 * SECTION 8: LOAD USERS NOT AFFECTED TO A GROUP
 * ===================================================================== */
async function loadUsersNotAffected(sessionId, accountId) {
    const container = document.getElementById('external-events');

    if (!container) {
        console.log('external-events container not found');
        return;
    }

    try {
        const response = await fetch(`/api/show_user_not_affected/${sessionId}/${accountId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        const existingUsers = container.querySelectorAll('.external-event-session');
        existingUsers.forEach(user => user.remove());

        if (result.Message === "Success" && result.students && result.students.length > 0) {
            result.students.forEach((user) => {
                const userElement = createUserElement(user, sessionId);
                container.appendChild(userElement);
            });

            initializeDragAndDrop();

        } else {
            const noUsersDiv = document.createElement('div');
            noUsersDiv.className = 'text-center py-3';
            noUsersDiv.innerHTML = '<p class="text-muted">No users without groups found.</p>';
            container.appendChild(noUsersDiv);
        }

    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function createUserElement(user, sessionId) {
    const userDiv = document.createElement('div');
    userDiv.className = 'external-event-session btn btn-primary light';
    userDiv.setAttribute('data-id', user.userId);
    userDiv.setAttribute('data-user-id', user.userId);
    userDiv.setAttribute('data-count', user.sessionCount);
    userDiv.setAttribute('data-session-id', sessionId);

    userDiv.innerHTML = `
        <i class="fa fa-move"></i>
        <span class="user-name">
            ${user.userName}
        </span>
        <small class="badge bg-warning ms-1 session-count">
            ${user.sessionCount}
        </small>
    `;

    return userDiv;
}


/* =====================================================================
 * SECTION 9: ASSIGN (AFFECT) USER TO GROUP
 * ===================================================================== */
async function assignUserToGroup(userId, groupId, sessionId) {
    try {
        const response = await fetch(`/api/affect_user/${sessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                group_id: groupId
            })
        });

        const result = await response.json();

        if (response.ok && result.Message === "Success") {
            return { success: true, data: result };
        } else {
            return { success: false, message: result.Message };
        }
    } catch (error) {
        console.error('Error assigning user to group:', error);
        return { success: false, message: error.message };
    }
}


/* =====================================================================
 * SECTION 10: DRAG & DROP (jQuery UI)
 * ===================================================================== */
function initializeDragAndDrop() {
    if (typeof jQuery !== 'undefined' && jQuery.fn.draggable) {

        jQuery('.external-event-session').draggable({
            revert: 'invalid',
            helper: 'clone',
            cursor: 'move',
            zIndex: 999
        });

        jQuery('.droppable-area-session').droppable({
            accept: '.external-event-session',
            drop: async function (event, ui) {
                const userElement = ui.draggable;
                const groupId = jQuery(this).data('group-id');
                const userId = userElement.data('user-id');
                const sessionId = userElement.data('session-id');

                const result = await assignUserToGroup(userId, groupId, sessionId);

                if (result.success) {
                    const clone = userElement.clone();
                    clone.removeClass('ui-draggable ui-draggable-handle');
                    clone.addClass('user-item-session');
                    clone.append('<button class="btn btn-xs btn-danger remove-user-session">x</button>');
                    jQuery(this).append(clone);

                    const capacityText = jQuery(this).closest('.user-content-session').find('.group-capacity-text');
                    const [current, max] = capacityText.text().replace('Capacity:', '').trim().split('/').map(Number);
                    capacityText.text(`Capacity: ${current + 1}/${max}`);

                    const remainingCount = parseInt(userElement.data('count')) - 1;
                    if (remainingCount > 0) {
                        userElement.attr('data-count', remainingCount);
                        userElement.find('.session-count').text(remainingCount);
                    } else {
                        userElement.remove();
                    }
                } else {
                    alert('Failed to assign user: ' + (result.message || 'Unknown error'));
                }
            }
        });

        console.log('Drag and drop initialized');
    } else {
        console.error('jQuery UI not loaded - drag and drop will not work');
    }
}


/* =====================================================================
 * SECTION 11: ADD GROUP MODAL — SUBMIT + MODAL FEEDBACK
 * ===================================================================== */
$(document).ready(function () {

    /* ---------------------------------------------------------------
     * Modal feedback helpers
     * --------------------------------------------------------------- */

    function showErrorModal(message) {
        $('#successMessage').text(message);
        $('#successModal .text-success').removeClass('text-success').addClass('text-danger');
        $('#successModal h3').text('Error');
        $('#successModal .btn-success').removeClass('btn-success').addClass('btn-danger');
        $('#successModal .check-icon').css('border-color', '#dc3545');
        $('#successModal .icon-line').css('background-color', '#dc3545');
        $('#successModal').modal('show');

        $('#successModal').on('hidden.bs.modal', function () {
            $('#successModal .text-danger').removeClass('text-danger').addClass('text-success');
            $('#successModal h3').text('Success!');
            $('#successModal .btn-danger').removeClass('btn-danger').addClass('btn-success');
            $('#successModal .check-icon').css('border-color', '#4CAF50');
            $('#successModal .icon-line').css('background-color', '#4CAF50');
        });
    }

    function showSuccessModal(message) {
        $('#successMessage').text(message);
        $('#successModal').modal('show');
    }

    /* ---------------------------------------------------------------
     * Data loading: Subjects & Teachers (for relation dropdowns)
     * --------------------------------------------------------------- */

    async function loadSubjects() {
        try {
            const accountId = window.ACCOUNT_ID;

            if (!accountId) {
                console.error('Account ID not found');
                return;
            }

            const response = await fetch(`/api/get_subject_group/${accountId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.Data) {
                subjectsData = result.Data;
                subjectsLoaded = true;
            }
        } catch (error) {
            console.error('Error loading subjects:', error);
            showErrorModal('Failed to load subjects. Please refresh the page.');
        }
    }

    async function loadTeachers() {
        try {
            const sessionId = window.SESSION_ID;

            if (!sessionId) {
                console.error('Session ID not found');
                return;
            }

            const response = await fetch(`/api/get_teacher/${sessionId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.data) {
                teachersData = result.data;
                teachersLoaded = true;
            } else if (result.teacher) {
                teachersData = result.teacher;
                teachersLoaded = true;
            }
        } catch (error) {
            console.error('Error loading teachers:', error);
            showErrorModal('Failed to load teachers. Please refresh the page.');
        }
    }

    loadSubjects();
    loadTeachers();

    /* ---------------------------------------------------------------
     * Dynamic Subject/Teacher relation rows (Add Group modal)
     * --------------------------------------------------------------- */

    $('#add-relationn').on('click', function (e) {
        e.preventDefault();

        const $collectionHolder = $('#relation_group_local_session_relationTeacherToSubjectGroups');

        if (!subjectsLoaded || !teachersLoaded) {
            showErrorModal('Please wait, loading data...');
            return;
        }

        const newRelationForm = `
            <div class="form-group relation-item mb-3 p-3 border rounded" data-index="${relationIndex}">
                <div id="relation_group_local_session_relationTeacherToSubjectGroups_${relationIndex}">
                    <div class="mb-3">
                        <label for="relation_group_local_session_relationTeacherToSubjectGroups_${relationIndex}_subject" class="required" style="display: block; margin-bottom: 0.5rem; font-weight: bold; color: #333;">
                            Subject
                        </label>
                        <select id="relation_group_local_session_relationTeacherToSubjectGroups_${relationIndex}_subject"
                                name="relation_group_local_session[relationTeacherToSubjectGroups][${relationIndex}][subject]"
                                required="required"
                                class="form-control relation-subject"
                                style="width: 100%; box-sizing: border-box;">
                            ${getSubjectOptions()}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="relation_group_local_session_relationTeacherToSubjectGroups_${relationIndex}_user" class="required" style="display: block; margin-bottom: 0.5rem; font-weight: bold; color: #333;">
                            Teacher
                        </label>
                        <select id="relation_group_local_session_relationTeacherToSubjectGroups_${relationIndex}_user"
                                name="relation_group_local_session[relationTeacherToSubjectGroups][${relationIndex}][user]"
                                required="required"
                                class="form-control relation-teacher"
                                style="width: 100%; box-sizing: border-box;">
                            ${getTeacherOptions()}
                        </select>
                    </div>
                </div>
                <button type="button" class="btn btn-danger remove-relation" style="width: 100%; text-align: center; border-radius: 5px; padding: 0.5rem;">
                    Remove
                </button>
            </div>
        `;

        $collectionHolder.append(newRelationForm);

        relationIndex++;
    });

    $(document).on('click', '.remove-relation', function () {
        $(this).closest('.relation-item').remove();
    });

    /* ---------------------------------------------------------------
     * Add Group form submission
     * --------------------------------------------------------------- */

    $('#group-local-session-form').on('submit', async function (e) {
        e.preventDefault();

        const sessionId = window.SESSION_ID;
        const accountId = window.ACCOUNT_ID;

        if (!sessionId || !accountId) {
            showErrorModal('Missing session or account information');
            return;
        }

        const groupName = $('#relation_group_local_session_name').val().trim();
        const capacity = $('#relation_group_local_session_capacity').val();

        if (!groupName) {
            showErrorModal('Please enter a group name');
            return;
        }

        if (!capacity || capacity <= 0) {
            showErrorModal('Please enter a valid capacity');
            return;
        }

        const relations = [];
        $('.relation-item').each(function () {
            const subjectId = $(this).find('.relation-subject').val();
            const teacherId = $(this).find('.relation-teacher').val();

            if (subjectId && teacherId) {
                relations.push({
                    subject_id: parseInt(subjectId),
                    teacher_id: parseInt(teacherId)
                });
            }
        });

        if (relations.length === 0) {
            showErrorModal('Please add at least one subject and teacher relation');
            return;
        }

        const formData = {
            group_name: groupName,
            capacity: parseInt(capacity),
            relations: relations,
            account_id: accountId,
            local_id: window.LOCAL_ID,
            access_type: 0
        };

        try {
            const submitButton = $(this).find('button[type="submit"]');
            const originalText = submitButton.text();
            submitButton.prop('disabled', true).text('Creating...');

            const response = await fetch(`/api/create_group/${sessionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                $('#groupModal').modal('hide');

                setTimeout(() => {
                    showSuccessModal(`Group "${groupName}" created successfully!`);

                    $('#successModal').on('hidden.bs.modal', function () {
                        location.reload();
                    });
                }, 300);
            } else {
                showErrorModal('Error: ' + (result.Message || 'Failed to create group'));
            }

            submitButton.prop('disabled', false).text(originalText);

        } catch (error) {
            console.error('Error creating group:', error);
            showErrorModal('Failed to create group. Please try again.');

            const submitButton = $(this).find('button[type="submit"]');
            submitButton.prop('disabled', false).text('Create');
        }
    });

    $('#groupModal').on('hidden.bs.modal', function () {
        $('#relation_group_local_session_relationTeacherToSubjectGroups').empty();
        relationIndex = 0;
        $('#group-local-session-form')[0].reset();
    });

});