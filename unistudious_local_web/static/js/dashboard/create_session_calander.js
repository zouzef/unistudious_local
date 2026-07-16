/* ==========================================================================
   create_session_calander.js
   Session calendar page: loads dropdown data (rooms, teachers, groups,
   completion tags) and wires up the Create Event / Delete Interval modals.
   ========================================================================== */


/* ==========================================================================
   1. LOAD GROUPS -> rendered as draggable "external events" in the sidebar
   ========================================================================== */
function loadGroupsToExternalEvents(sessionId, accountId, localId) {
    fetch(`/api/get-group/${sessionId}/${accountId}`, { method: 'GET' })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (!data.data) {
                console.error('No data.data found');
                return;
            }

            const groups = data.data;
            const container = document.getElementById('my-custom-events');
            container.innerHTML = '';

            if (!groups.length) {
                container.innerHTML = '<p class="text-muted">No groups found.</p>';
                return;
            }

            const colors = ['bg-info'];

            groups.forEach((group, index) => {
                const color = colors[index % colors.length];
                const buttonClass = color.replace('bg-', 'btn-');

                const groupDiv = document.createElement('div');
                groupDiv.className = `external-event ${buttonClass} light`;
                groupDiv.setAttribute('data-class', color);

                // Carry group identity so it can be used when creating an event
                groupDiv.setAttribute('data-group-id', group.id);
                groupDiv.setAttribute('data-capacity', group.capacity ?? '');
                groupDiv.setAttribute('data-session-id', group.session_id ?? sessionId);
                groupDiv.setAttribute('data-local-id', group.local_id ?? localId);
                groupDiv.setAttribute('data-status', group.status ?? '');

                groupDiv.innerHTML = `
                    <i class="fa fa-move"></i>
                    <span>${group.name}</span>
                `;

                // Clicking a group opens the Create Event modal pre-filled
                // with this group's id/capacity/session/local ids.
                groupDiv.addEventListener('click', () => {
                    const groupIdField = document.getElementById('createEventGroupId');
                    const groupCapacityField = document.getElementById('createEventGroupCapacity');
                    const sessionIdField = document.getElementById('createEventSessionId');
                    const localIdField = document.getElementById('createEventLocalId');
                    const accountIdField = document.getElementById('createEventAccountId');

                    if (groupIdField) groupIdField.value = group.id;
                    if (groupCapacityField) groupCapacityField.value = group.capacity ?? '';
                    if (sessionIdField) sessionIdField.value = group.session_id ?? sessionId;
                    if (localIdField) localIdField.value = group.local_id ?? localId;
                    if (accountIdField) accountIdField.value = accountId;

                    const createEventModalEl = document.getElementById('createEventModal');
                    if (createEventModalEl) {
                        bootstrap.Modal.getOrCreateInstance(createEventModalEl).show();
                    }
                });

                container.appendChild(groupDiv);
            });
        })
        .catch(error => console.error('Error fetching groups:', error));
}


/* ==========================================================================
   1b. GROUP SEARCH FILTER -> live-filters the rendered groups by name
   Works on whatever is currently in #my-custom-events, so it stays correct
   even after loadGroupsToExternalEvents() re-renders the list.
   ========================================================================== */
function initGroupSearchFilter() {
    const filterInput = document.getElementById('group-calander-filter');
    const container = document.getElementById('my-custom-events');

    if (!filterInput || !container) return;

    filterInput.addEventListener('input', function () {
        const searchTerm = this.value.trim().toLowerCase();

        container.querySelectorAll('.external-event').forEach(groupDiv => {
            // The group name lives in the <span> set by loadGroupsToExternalEvents()
            const nameEl = groupDiv.querySelector('span');
            const groupName = (nameEl ? nameEl.textContent : groupDiv.textContent).trim().toLowerCase();

            const matches = searchTerm === '' || groupName.includes(searchTerm);
            groupDiv.style.display = matches ? '' : 'none';
        });
    });
}


/* ==========================================================================
   2. LOAD ROOMS -> populates the "Room" custom-select
   ========================================================================== */
function load_room(local_id) {
    fetch(`/api/get_room/${local_id}`, { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            if (!data.Room) {
                console.error('No Room data found');
                return;
            }

            const rooms = data.Room;
            const roomOptions = document.querySelector('.custom-select[data-name="createEventRoom"] .options');

            if (!roomOptions) {
                console.error('Room options container not found');
                return;
            }

            // Clear existing options, keep only the placeholder
            roomOptions.innerHTML = '<div data-value="">Select a Room</div>';

            rooms.forEach(room => {
                const optionDiv = document.createElement('div');
                optionDiv.setAttribute('data-value', room.id);
                optionDiv.textContent = room.name;
                roomOptions.appendChild(optionDiv);
            });
        })
        .catch(error => console.error('Error fetching room:', error));
}


/* ==========================================================================
   3. LOAD TEACHERS -> populates the "Teacher And Subject" custom-select
   ========================================================================== */
function load_teachers(session_id) {
    fetch(`/api/get_teacher/${session_id}`, { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            if (!data.teacher) {
                console.error('No teacher data found');
                return;
            }

            const teachers = data.teacher;
            const teacherOptions = document.querySelector('.custom-select[data-name="createEventSubject"] .options');

            if (!teacherOptions) {
                console.error('Teacher options container not found');
                return;
            }

            teacherOptions.innerHTML = '<div data-value="">Select a Subject and Teacher</div>';

            teachers.forEach(teacher => {
                const optionDiv = document.createElement('div');

                // API field name for the teacher's id varies - fall back
                // through the common alternatives instead of assuming `id`.
                const teacherId = teacher.id ?? teacher.teacher_id ?? teacher.user_id ?? '';
                if (teacherId === '') {
                    console.warn('Could not find an id field for teacher:', teacher);
                }

                optionDiv.setAttribute('data-value', teacherId);
                optionDiv.setAttribute('data-subject', teacher.subject_id || '1');
                optionDiv.setAttribute('data-user', teacherId);

                const subjectName = teacher.subject_name || 'Math';
                const teacherName = `${teacher.full_name}`;
                optionDiv.textContent = `Subject : ${subjectName} - Teacher : ${teacherName}`;

                teacherOptions.appendChild(optionDiv);
            });

            // Re-attach the generic single-select click handlers for the
            // newly created options (Room / Type / Subject / Duplicate).
            initCustomSelects();
        })
        .catch(error => console.error('Error fetching teachers:', error));
}


/* ==========================================================================
   4. LOAD COMPLETION TAGS -> populates the "Completion Tag" custom-select
   This one is MULTI-select, so it is intentionally NOT handled by the
   generic initCustomSelects() logic (see initCustomSelects() below for why).
   ========================================================================== */
function load_completion_tags(accountId) {
    fetch(`/api/get_completion_tag/${accountId}`, { method: 'GET' })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            // This endpoint returns a raw array directly, not wrapped in a key
            const tags = Array.isArray(data) ? data : [];

            const tagSelect = document.getElementById('createEventCompletionTag');
            const tagOptions = tagSelect?.querySelector('.options');
            const tagSelected = tagSelect?.querySelector('.selected');

            if (!tagOptions || !tagSelected) {
                console.error('Completion tag options container not found');
                return;
            }

            tagOptions.innerHTML = '';

            if (!tags.length) {
                tagOptions.innerHTML = '<div class="text-muted px-2">No completion tags found</div>';
                return;
            }

            tags.forEach(tag => {
                const optionDiv = document.createElement('div');
                optionDiv.setAttribute('data-value', tag.id);
                optionDiv.textContent = tag.name;
                tagOptions.appendChild(optionDiv);
            });

            // Single delegated listener handles toggling for all tag
            // options and keeps the visible "selected" label in sync with
            // every tag currently picked (not just the last one clicked).
            tagOptions.addEventListener('click', (e) => {
                const optionDiv = e.target.closest('div[data-value]');
                if (!optionDiv) return;

                e.stopPropagation();
                optionDiv.classList.toggle('selected-option');
                updateCompletionTagLabel(tagSelect);
            });
        })
        .catch(error => console.error('Error fetching completion tags:', error));
}

// Rebuilds the "Select Completion Tag(s)" label from whichever option divs
// currently carry the 'selected-option' class.
function updateCompletionTagLabel(tagSelect) {
    const tagSelected = tagSelect.querySelector('.selected');
    const chosen = tagSelect.querySelectorAll('.options .selected-option');

    tagSelected.textContent = chosen.length
        ? Array.from(chosen).map(opt => opt.textContent).join(', ')
        : 'Select Completion Tag(s)';
}


/* ==========================================================================
   5. INITIAL PAGE LOAD -> fire all the loaders once PAGE_DATA is available
   ========================================================================== */
document.addEventListener('DOMContentLoaded', function () {
    const { sessionId, accountId, localId } = window.PAGE_DATA;

    load_room(localId);
    load_teachers(sessionId);
    loadGroupsToExternalEvents(sessionId, accountId, localId);
    load_completion_tags(accountId);
    initGroupSearchFilter();
});


/* ==========================================================================
   6. VIEW EVENT MODAL -> duplicate field toggling + save handler
   ========================================================================== */
document.addEventListener('DOMContentLoaded', function () {

    // Prevent Bootstrap Select from initializing on modal selects
    $('#createEventModal select, #viewEventModal select').addClass('no-selectpicker');

    // Show/hide duplicate-related fields depending on the chosen option
    const createEventDuplicate = document.getElementById('createEventDuplicate');
    if (createEventDuplicate) {
        createEventDuplicate.addEventListener('change', function () {
            const value = this.value;
            const startTimeFields = document.getElementById('createStartTimeFields');
            const endTimeFields = document.getElementById('createEndTimeFields');
            const eventEndFields = document.getElementById('createEventEndFields');

            if (value !== 'none' && value !== '') {
                startTimeFields.style.display = 'block';
                endTimeFields.style.display = 'block';
                eventEndFields.style.display = 'block';
            } else {
                startTimeFields.style.display = 'none';
                endTimeFields.style.display = 'none';
                eventEndFields.style.display = 'none';
            }
        });
    }

    // Save button for the VIEW event modal
    const viewSaveEventButton = document.getElementById('viewSaveEventButton');
    if (viewSaveEventButton) {
        viewSaveEventButton.addEventListener('click', function () {
            const viewEventForm = document.getElementById('viewEventForm');

            if (!viewEventForm.checkValidity()) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Missing Information',
                    text: 'Please fill in all required fields',
                    confirmButtonColor: '#4c4b9e'
                });
                return;
            }

            const formData = {
                title: document.getElementById('viewEventTitle').value,
                date: document.getElementById('viewEventDate').value,
                type: document.getElementById('viewTypeSessionSelect').value,
                room: document.getElementById('viewEventRoom').value,
                subject: document.getElementById('viewEventSubject').value,
                completionTags: (() => {
                    const element = document.getElementById('createEventCompletionTag');
                    if (!element) return [];

                    const selectedOptions = element.querySelectorAll('.options .selected-option');
                    return Array.from(selectedOptions)
                        .map(option => option.getAttribute('data-value'))
                        .filter(value => value !== null && value !== '');
                })(),
                duplicate: document.getElementById('viewEventDuplicate').value,
                startTime: document.getElementById('viewEventStartTime').value || null,
                endTime: document.getElementById('viewEventEndTime').value || null,
                endDate: document.getElementById('viewEventEndDate').value || null,
                description: document.getElementById('viewEventDescription').value,
                groupId: document.getElementById('viewEventGroupId').value,
                groupCapacity: document.getElementById('viewEventGroupCapacity').value,
                sessionId: document.getElementById('viewEventSessionId').value,
                accountId: document.getElementById('viewEventAccountId').value,
                localId: document.getElementById('viewEventLocalId').value
            };

            fetch('/api/update-event', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Event Updated',
                            text: 'Event updated successfully!',
                            confirmButtonColor: '#4c4b9e'
                        }).then(() => {
                            const viewEventModal = bootstrap.Modal.getInstance(document.getElementById('viewEventModal'));
                            viewEventModal.hide();
                            location.reload();
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: toDisplayText(data.message) || 'Failed to update event',
                            confirmButtonColor: '#4c4b9e'
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Failed to update event',
                        confirmButtonColor: '#4c4b9e'
                    });
                });
        });
    }
});


/* ==========================================================================
   7. GENERIC CUSTOM-SELECT BEHAVIOR (single-select dropdowns)
   Handles: Room, Type, Teacher/Subject, Duplicate.
   NOTE: #createEventCompletionTag is intentionally EXCLUDED here because it
   is a multi-select managed entirely by load_completion_tags() above. Their
   click handlers used to both attach to the same option divs, which caused
   the tag options to look unresponsive / "disabled" on click - the
   single-select handler here would immediately overwrite the label and
   close the dropdown right after the toggle handler ran.
   ========================================================================== */
function initCustomSelects() {
    document.querySelectorAll('.custom-select').forEach(selectEl => {
        // Skip the completion tag select - it manages its own listeners.
        if (selectEl.id === 'createEventCompletionTag') return;

        const selected = selectEl.querySelector('.selected');

        // Remove old listeners to avoid duplicates by cloning the node
        const newSelected = selected.cloneNode(true);
        selected.parentNode.replaceChild(newSelected, selected);

        // Toggle dropdown open/closed
        newSelected.onclick = (e) => {
            e.stopPropagation();
            document.querySelectorAll('.custom-select').forEach(s => {
                if (s !== selectEl) s.classList.remove('active');
            });
            selectEl.classList.toggle('active');
        };

        // Handle option selection (single-select behavior)
        const updatedOptions = selectEl.querySelector('.options');
        updatedOptions.querySelectorAll('div').forEach(opt => {
            opt.onclick = (e) => {
                e.stopPropagation();
                const value = opt.getAttribute('data-value');
                const text = opt.textContent;

                const currentSelected = selectEl.querySelector('.selected');
                currentSelected.textContent = text;
                currentSelected.setAttribute('data-value', value);

                // The "Teacher And Subject" select picks a teacher AND a
                // subject in one click - load_teachers() puts the subject id
                // on each option as data-subject; capture it here so it
                // survives past this click.
                const subjectId = opt.getAttribute('data-subject');
                if (subjectId !== null) {
                    currentSelected.setAttribute('data-subject-id', subjectId);
                }

                selectEl.classList.remove('active');

                if (selectEl.getAttribute('data-name') === 'createEventDuplicate') {
                    handleDuplicateChange(value);
                }
            };
        });
    });

    // Close any open dropdown when clicking outside of it
    document.addEventListener('click', (e) => {
        document.querySelectorAll('.custom-select.active').forEach(selectEl => {
            if (!selectEl.contains(e.target)) {
                selectEl.classList.remove('active');
            }
        });
    });
}

// Reads the data-subject-id captured above for the Teacher/Subject select.
function getSelectedSubjectId() {
    const select = document.querySelector('.custom-select[data-name="createEventSubject"] .selected');
    return select ? (select.getAttribute('data-subject-id') || '') : '';
}

// Shows/hides the start/end time and end-date fields based on the chosen
// duplicate option.
function handleDuplicateChange(value) {
    const startTimeFields = document.getElementById('createStartTimeFields');
    const endTimeFields = document.getElementById('createEndTimeFields');
    const eventEndFields = document.getElementById('createEventEndFields');

    if (!startTimeFields || !endTimeFields || !eventEndFields) return;

    if (value === 'none') {
        // "Not Duplicate" - show time fields but hide end date
        startTimeFields.style.display = 'block';
        endTimeFields.style.display = 'block';
        eventEndFields.style.display = 'none';
    } else if (value && value !== '') {
        // Any duplicate option - show all fields
        startTimeFields.style.display = 'block';
        endTimeFields.style.display = 'block';
        eventEndFields.style.display = 'block';
    } else {
        // No selection - hide all
        startTimeFields.style.display = 'none';
        endTimeFields.style.display = 'none';
        eventEndFields.style.display = 'none';
    }
}

// Safely converts a backend response value into displayable text. Guards
// against showing the literal string "[object Object]" in SweetAlert when
// a Message/Error field unexpectedly comes back as an object or array
// instead of a plain string.
function toDisplayText(value) {
    if (typeof value === 'string') return value;
    if (value === null || value === undefined) return '';
    try {
        return JSON.stringify(value);
    } catch {
        return String(value);
    }
}

// Some backend responses wrap the real error payload as a JSON *string*
// inside the outer "Message" field, e.g.:
//   { "Message": "{\"Error\":\"Room-Conflict\",\"Message\":\"Room already reserved...\"}" }
// instead of the inner fields being top-level. This detects that case and
// returns the parsed inner object so we can read its real Error/Message/
// occurrence_date/created_before_failure. Falls back to the original data
// unchanged if Message isn't a JSON string.
function unwrapNestedErrorPayload(data) {
    if (data && typeof data.Message === 'string') {
        const trimmed = data.Message.trim();
        if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
            try {
                const inner = JSON.parse(trimmed);
                // Merge so any outer fields not present inside are kept too
                return { ...data, ...inner };
            } catch {
                // Not actually JSON - leave data as-is
            }
        }
    }
    return data;
}

// Reads the current value of a single-select custom-select by name.
function getCustomSelectValue(name) {
    const select = document.querySelector(`.custom-select[data-name="${name}"]`);
    if (!select) return '';

    const value = select.querySelector('.selected').getAttribute('data-value');

    // Guard against the literal strings "undefined"/"null" being treated
    // as valid selected values.
    if (!value || value === 'undefined' || value === 'null') return '';
    return value;
}


/* ==========================================================================
   8. CREATE EVENT MODAL -> init on open + save handler
   ========================================================================== */
document.addEventListener('DOMContentLoaded', function () {
    const createModalElement = document.getElementById('createEventModal');
    if (createModalElement) {
        createModalElement.addEventListener('shown.bs.modal', function () {
            initCustomSelects();
        });
    }

    const createSaveEventButton = document.getElementById('createSaveEventButton');
    if (createSaveEventButton) {
        createSaveEventButton.addEventListener('click', function () {
            // Backend (create_calander) requires these exact snake_case
            // keys: session_id, account_id, local_id, group_id, room_id,
            // teacher_id, subject_id, description, start_time, end_time,
            // title, type.
            const date = document.getElementById('createEventDate').value;
            const startTime = document.getElementById('createEventStartTime').value;
            const endTime = document.getElementById('createEventEndTime').value;
            const teacherId = getCustomSelectValue('createEventSubject'); // data-value = teacher id
            const subjectId = getSelectedSubjectId(); // data-subject captured on selection

            // Read session/account/local ids directly from PAGE_DATA (sourced
            // from the URL server-side) instead of the hidden inputs, which
            // only get populated if the user clicked a group first.
            const { sessionId, accountId, localId } = window.PAGE_DATA;

            const formData = {
                title: document.getElementById('createEventTitle').value,
                type: getCustomSelectValue('createTypeSessionSelect'),
                room_id: getCustomSelectValue('createEventRoom'),
                teacher_id: teacherId,
                subject_id: subjectId,
                description: document.getElementById('createEventDescription').value,
                // Backend uses start_time as a full date+time value - combine
                // the separate date/time inputs instead of sending a bare
                // "12:30" with no date attached.
                start_time: date && startTime ? `${date} ${startTime}:00` : null,
                end_time: date && endTime ? `${date} ${endTime}:00` : null,
                group_id: document.getElementById('createEventGroupId').value,
                session_id: sessionId,
                account_id: accountId,
                local_id: localId,

                // Not required by the backend route shown, but harmless to
                // include if other logic downstream reads them:
                completionTags: (() => {
                    const element = document.getElementById('createEventCompletionTag');
                    if (!element) return [];

                    const selectedOptions = element.querySelectorAll('.options .selected-option');
                    return Array.from(selectedOptions)
                        .map(option => option.getAttribute('data-value'))
                        .filter(value => value !== null && value !== '');
                })(),
                duplicate: (() => {
                    const element = document.getElementById('createEventDuplicate');
                    if (!element) return '';

                    const selectedElement = element.querySelector('.selected');
                    return selectedElement ? selectedElement.getAttribute('data-value') || '' : '';
                })(),
                endDate: document.getElementById('createEventEndDate').value || null,
                groupCapacity: document.getElementById('createEventGroupCapacity').value
            };

            // Validate only the fields the backend actually requires
            const requiredCheck = {
                title: formData.title,
                type: formData.type,
                room_id: formData.room_id,
                teacher_id: formData.teacher_id,
                subject_id: formData.subject_id,
                start_time: formData.start_time,
                end_time: formData.end_time,
                group_id: formData.group_id,
                session_id: formData.session_id,
                account_id: formData.account_id,
                local_id: formData.local_id
            };
            const missing = Object.entries(requiredCheck)
                .filter(([, v]) => v === null || v === undefined || v === '')
                .map(([k]) => k);

            if (missing.length) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Missing Information',
                    text: 'Please fill in all required fields: ' + missing.join(', '),
                    confirmButtonColor: '#4c4b9e'
                });
                return;
            }

            // Backend returns {"Message": message} with NO "success" key -
            // success/failure is signaled only via HTTP status code (200 vs
            // 400), so check response.ok and read data.Message.
            fetch('/api/create-calander', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
                .then(async response => {
                    const data = await response.json();
                    return { ok: response.ok, data };
                })
                .then(({ ok, data }) => {
                    if (ok) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Calendar Created',
                            text: toDisplayText(data.Message) || 'The calendar was created successfully!',
                            confirmButtonColor: '#4c4b9e'
                        }).then(() => {
                            const eventModal = bootstrap.Modal.getInstance(document.getElementById('createEventModal'));
                            eventModal.hide();
                            location.reload();
                        });
                    } else {
                        // Some responses (e.g. conflict errors) come back
                        // with the real payload double-encoded inside
                        // Message as a JSON string - unwrap it first so we
                        // read the actual Error/Message/occurrence_date
                        // fields instead of printing raw JSON text.
                        data = unwrapNestedErrorPayload(data);

                        // Missing/empty required fields (400)
                        const fieldDetail = data.missing_fields || data.empty_fields;

                        // Room / Group / Teacher conflicts (402) — recurring
                        // events may also report how many occurrences were
                        // already created before the conflicting one.
                        const partialCount = Array.isArray(data.created_before_failure)
                            ? data.created_before_failure.length
                            : 0;

                        let text = toDisplayText(data.Message) || 'Something went wrong.';
                        if (Array.isArray(fieldDetail)) {
                            text += ' (' + fieldDetail.join(', ') + ')';
                        }
                        if (data.occurrence_date) {
                            text += ` — conflict on ${data.occurrence_date}.`;
                        }
                        if (partialCount > 0) {
                            text += ` ${partialCount} occurrence(s) were already created before this conflict.`;
                        }

                        Swal.fire({
                            icon: 'warning',
                            title: toDisplayText(data.Error) || 'Error',
                            text: text,
                            confirmButtonColor: '#4c4b9e'
                        }).then(() => {
                            // If part of a recurring series was created, the
                            // calendar view is now out of date — reload so
                            // it reflects the entries that did succeed.
                            if (partialCount > 0) {
                                location.reload();
                            }
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Failed to create event. Check your connection or contact support if this persists.',
                        confirmButtonColor: '#4c4b9e'
                    });
                });
        });
    }
});


/* ==========================================================================
   9. DELETE INTERVAL MODAL -> confirm handler
   ========================================================================== */
document.addEventListener('DOMContentLoaded', function () {
    const confirmDeleteBtn = document.getElementById('confirmDeleteInterval');
    if (!confirmDeleteBtn) return;

    confirmDeleteBtn.addEventListener('click', async function () {
        // Reads this modal's own hidden field (not the unrelated
        // #copyIntervalModal's #sessionId, which was the earlier bug).
        const sessionId = document.getElementById('deleteIntervalSessionId').value;
        const startDate = document.getElementById('deleteTargetStartDate').value;
        const endDate = document.getElementById('deleteTargetEndDate').value;

        if (!startDate || !endDate) {
            alert('Please select both start and end dates');
            return;
        }

        if (new Date(endDate) < new Date(startDate)) {
            alert('End date must be after start date');
            return;
        }

        try {
            const deleteBtn = document.getElementById('confirmDeleteInterval');
            deleteBtn.disabled = true;
            deleteBtn.textContent = 'Deleting...';

            const response = await fetch(`/api/delete-calander/${sessionId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start_date: startDate, end_date: endDate })
            });

            const result = await response.json();

            if (response.ok) {
                alert('Calendar interval deleted successfully!');

                const modal = bootstrap.Modal.getInstance(document.getElementById('deleteIntervalModal'));
                modal.hide();

                document.getElementById('deleteTargetStartDate').value = '';
                document.getElementById('deleteTargetEndDate').value = '';

                location.reload();
            } else {
                console.error('Server error:', result);
                alert(`Error: ${result.message || 'Failed to delete interval'}`);
            }
        } catch (error) {
            console.error('Fetch error details:', error);
            alert('An error occurred while deleting the interval. Check console for details.');
        } finally {
            const deleteBtn = document.getElementById('confirmDeleteInterval');
            deleteBtn.disabled = false;
            deleteBtn.textContent = 'Delete';
        }
    });
});