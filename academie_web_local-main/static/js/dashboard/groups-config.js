$(document).ready(function() {

    // Initialize draggable students
    function initializeDraggableStudents() {
        $(".external-event-session").draggable({
            revert: "invalid",
            helper: "clone",
            cursor: "move",
            zIndex: 1000,
            start: function(event, ui) {
                $(this).css('opacity', '0.5');
            },
            stop: function(event, ui) {
                $(this).css('opacity', '1');
            }
        });
    }

    // Initialize droppable group areas
    function initializeDroppableGroups() {
        $(".droppable-area-session").droppable({
            accept: ".external-event-session",
            hoverClass: "drop-hover",
            drop: function(event, ui) {
                var droppedStudent = ui.draggable;
                var groupArea = $(this);
                var groupId = groupArea.data('group-id');
                var capacity = parseInt(groupArea.data('capacity'));
                var currentStudents = groupArea.find('.user-item-session').length;

                // Check if group is full
                if (currentStudents >= capacity) {
                    alert('This group is full! Capacity: ' + capacity);
                    return false;
                }

                // Get student data
                var studentId = droppedStudent.data('id');
                var userId = droppedStudent.data('user-id');
                var sessionId = droppedStudent.data('session-id');
                var studentName = droppedStudent.find('.user-name').text().trim();

                // Check if student already exists in this group
                var existingStudent = groupArea.find('.user-item-session[data-user-id="' + userId + '"]');
                if (existingStudent.length > 0) {
                    alert('This student is already in this group!');
                    return false;
                }

                // Create the student item in the group
                var studentItem = `
                    <div class="user-item-session"
                         data-id="${studentId}"
                         data-session-id="${sessionId}"
                         data-user-id="${userId}">
                        ${studentName}
                        <button class="btn btn-xs btn-danger remove-user-session">x</button>
                    </div>
                `;

                // Add student to group
                groupArea.append(studentItem);

                // Update the session count badge
                updateSessionCount(droppedStudent, 1);

                // ✅ ADD THIS - DETECTION WHEN STUDENT IS DROPPED
                console.log('🎯 STUDENT DROPPED!');
                console.log('Student ID:', studentId);
                console.log('User ID:', userId);
                console.log('Student Name:', studentName);
                console.log('Dropped to Group ID:', groupId);
                console.log('Session ID:', sessionId);
                console.log('-------------------');

                // Send to server (optional - uncomment and modify as needed)
                // saveStudentToGroup(userId, groupId, sessionId);

                // Visual feedback
                groupArea.effect("highlight", {}, 1000);
            }
        });
    }

    // Remove student from group
    $(document).on('click', '.remove-user-session', function() {
        var studentItem = $(this).parent();
        var userId = studentItem.data('user-id');
        var studentId = studentItem.data('id');
        var sessionId = studentItem.data('session-id');
        var groupArea = studentItem.closest('.droppable-area-session');
        var groupId = groupArea.data('group-id');

        // Find the corresponding external student and update count
        var externalStudent = $('.external-event-session[data-user-id="' + userId + '"]');
        updateSessionCount(externalStudent, -1);

        // ✅ ADD THIS - DETECTION WHEN STUDENT IS REMOVED
        console.log('❌ STUDENT REMOVED!');
        console.log('Student ID:', studentId);
        console.log('User ID:', userId);
        console.log('Removed from Group ID:', groupId);
        console.log('Session ID:', sessionId);
        console.log('-------------------');

        // Remove from group
        studentItem.remove();

        // Optional: Send removal to server
        // removeStudentFromGroup(userId, groupArea.data('group-id'));
    });

    // Update session count badge
    function updateSessionCount(studentElement, change) {
        var badge = studentElement.find('.session-count');
        var currentCount = parseInt(badge.text());
        var newCount = currentCount + change;
        badge.text(newCount);

        // Update data attribute
        studentElement.attr('data-count', newCount);
    }

    // Search/Filter students
    $('#filtre-Student-group').on('keyup', function() {
        var searchText = $(this).val().toLowerCase();

        $('.external-event-session').each(function() {
            var studentName = $(this).find('.user-name').text().toLowerCase();
            if (studentName.includes(searchText)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });

    // Optional: Save to server via AJAX
    function saveStudentToGroup(userId, groupId, sessionId) {
        $.ajax({
            url: '/api/assign-student-to-group',
            method: 'POST',
            data: {
                user_id: userId,
                group_id: groupId,
                session_id: sessionId
            },
            success: function(response) {
                console.log('Student assigned successfully');
            },
            error: function(error) {
                console.error('Error assigning student:', error);
                alert('Failed to assign student to group');
            }
        });
    }

    // Optional: Remove from server
    function removeStudentFromGroup(userId, groupId) {
        $.ajax({
            url: '/api/remove-student-from-group',
            method: 'POST',
            data: {
                user_id: userId,
                group_id: groupId
            },
            success: function(response) {
                console.log('Student removed successfully');
            },
            error: function(error) {
                console.error('Error removing student:', error);
            }
        });
    }

    // Initialize everything
    initializeDraggableStudents();
    initializeDroppableGroups();
});