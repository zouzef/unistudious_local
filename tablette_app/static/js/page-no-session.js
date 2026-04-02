/* ══════════════════════════════════════════════════════════════
   calendar-page.js
   All page-level logic for the tablet calendar page
══════════════════════════════════════════════════════════════ */

/* ─────────────────────────────────────────────────────────────
   1. TABLET & ACADEMIE INITIALISATION
───────────────────────────────────────────────────────────── */

const urlParts  = window.location.pathname.split('/');
const tablet_id = urlParts[urlParts.length - 1];

fetch(`/get-data-account-tablet/${tablet_id}`)
    .then(r => r.json())
    .then(result => {
        if (result.status === 'ok' && result.data) {
            document.getElementById('academie-title').textContent = result.data.name + ' - Calendar';
        }
    })
    .catch(err => console.error('Error fetching academie name:', err));

const _logoImg = document.getElementById('academie-logo');
_logoImg.src     = `/api/get-academie-image/${tablet_id}`;
_logoImg.onload  = () => _logoImg.style.display = 'block';
_logoImg.onerror = () => _logoImg.style.display = 'none';


/* ─────────────────────────────────────────────────────────────
   2. SESSION POLLING — redirect to tablet when a session is active
───────────────────────────────────────────────────────────── */

function checkForSession() {
    fetch(`/tablet/${encodeURIComponent(tablet_id)}/check_session`)
        .then(r => r.json())
        .then(data => {
            if (data.status === 'active') {
                document.getElementById('qr-fullscreen-overlay').style.display = 'none';
                window.location.href = `/tablet/${encodeURIComponent(tablet_id)}`;
            }
        })
        .catch(err => console.error('Error checking session:', err));
}

checkForSession();
setInterval(checkForSession, 10000);


/* ─────────────────────────────────────────────────────────────
   3. SCHEDULE MODAL — duplicate field visibility
───────────────────────────────────────────────────────────── */

document.getElementById('eventDuplicate').addEventListener('change', function () {
    const startTimeFields = document.getElementById('startTimeFields');
    const endTimeFields   = document.getElementById('endTimeFields');
    const eventEndFields  = document.getElementById('eventEndFields');

    if (this.value === 'none') {
        startTimeFields.classList.remove('d-none');
        endTimeFields.classList.remove('d-none');
        eventEndFields.classList.add('d-none');
    } else if (['daily', 'weekly', 'biweekly'].includes(this.value)) {
        startTimeFields.classList.remove('d-none');
        endTimeFields.classList.remove('d-none');
        eventEndFields.classList.remove('d-none');
    } else {
        startTimeFields.classList.add('d-none');
        endTimeFields.classList.add('d-none');
        eventEndFields.classList.add('d-none');
    }
});


/* ─────────────────────────────────────────────────────────────
   4. TEACHER AUTHENTICATION
───────────────────────────────────────────────────────────── */

let isAuthenticated   = false;
let inactivityTimer   = null;
let countdownInterval = null;
const SESSION_DURATION = 5 * 60 * 1000; // 5 minutes

function resetInactivityTimer() {
    if (!isAuthenticated) return;

    clearTimeout(inactivityTimer);
    clearInterval(countdownInterval);

    let secondsLeft = SESSION_DURATION / 1000;
    countdownInterval = setInterval(() => {
        secondsLeft--;
        const mins = Math.floor(secondsLeft / 60);
        const secs = secondsLeft % 60;
        console.log(`⏳ Session expires in: ${mins}:${secs.toString().padStart(2, '0')}`);
        if (secondsLeft <= 0) clearInterval(countdownInterval);
    }, 1000);

    inactivityTimer = setTimeout(() => {
        isAuthenticated = false;
        clearInterval(countdownInterval);
        console.log('🔒 Session expired — teacher disconnected');
    }, SESSION_DURATION);
}

['touchstart', 'click', 'mousemove', 'keydown'].forEach(evt => {
    document.addEventListener(evt, () => {
        if (isAuthenticated) resetInactivityTimer();
    });
});

function openAuthModal() {
    if (isAuthenticated) {
        new bootstrap.Modal(document.getElementById('eventModal')).show();
        return;
    }
    document.getElementById('auth-username').value = '';
    document.getElementById('auth-password').value = '';
    document.getElementById('auth-error').style.display = 'none';
    switchAuthTab('password');
    new bootstrap.Modal(document.getElementById('authModal')).show();
}

function switchAuthTab(tab) {
    const passwordTab = document.getElementById('auth-password-tab');
    const qrTab       = document.getElementById('auth-qr-tab');
    const tabPassword = document.getElementById('tab-password');
    const tabQr       = document.getElementById('tab-qr');

    if (tab === 'password') {
        passwordTab.style.display      = 'block';
        qrTab.style.display            = 'none';
        tabPassword.style.color        = '#4D44B5';
        tabPassword.style.borderBottom = '3px solid #4D44B5';
        tabQr.style.color              = '#aaa';
        tabQr.style.borderBottom       = '3px solid transparent';
        stopCamera();
    } else {
        passwordTab.style.display      = 'none';
        qrTab.style.display            = 'block';
        tabPassword.style.color        = '#aaa';
        tabPassword.style.borderBottom = '3px solid transparent';
        tabQr.style.color              = '#4D44B5';
        tabQr.style.borderBottom       = '3px solid #4D44B5';
        startCamera();
    }
}

document.getElementById('authModal')?.addEventListener('hidden.bs.modal', stopCamera);

function submitAuth() {
    const username  = document.getElementById('auth-username').value.trim();
    const password  = document.getElementById('auth-password').value.trim();
    const authError = document.getElementById('auth-error');

    if (!username || !password) {
        authError.style.display = 'block';
        authError.textContent   = '❌ Please enter username and password';
        return;
    }

    authError.style.display = 'none';

    const btn = event.target;
    btn.textContent = 'Verifying...';
    btn.disabled    = true;

    fetch('/api/teacher-authentificate', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ username, password }),
    })
    .then(r => r.json().then(data => ({ status: r.status, body: data })))
    .then(({ status, body }) => {
        btn.textContent = 'Login & Continue';
        btn.disabled    = false;
        if (status === 200) {
            onAuthSuccess();
        } else {
            authError.style.display = 'block';
            authError.textContent   = `❌ ${body.Message || 'Invalid username or password'}`;
        }
    })
    .catch(err => {
        btn.textContent = 'Login & Continue';
        btn.disabled    = false;
        authError.style.display = 'block';
        authError.textContent   = '❌ Network error, please try again';
        console.error('Auth error:', err);
    });
}

function onAuthSuccess() {
    bootstrap.Modal.getInstance(document.getElementById('authModal')).hide();
    stopCamera();
    isAuthenticated = true;
    resetInactivityTimer();

    setTimeout(() => {
        Swal.fire({
            icon: 'success',
            title: 'Authentication Successful',
            html: `✅ Welcome! You can now add a schedule.<br><br>
                   <small style="color:#888;">⏳ Auto-disconnect after <strong>5 minutes</strong> of inactivity.</small>`,
            confirmButtonText:  'Continue',
            confirmButtonColor: '#4D44B5',
            timer: 6000,
            timerProgressBar: true,
        }).then(() => {
            new bootstrap.Modal(document.getElementById('eventModal')).show();
        });
    }, 300);
}

function disconnectTeacher() {
    isAuthenticated = false;
    clearTimeout(inactivityTimer);
    clearInterval(countdownInterval);
    inactivityTimer   = null;
    countdownInterval = null;
    console.log('🔒 Teacher manually disconnected');
}

document.getElementById('saveAndDisconnectButton').addEventListener('click', function () {
    document.getElementById('saveEventButton').click();
    setTimeout(() => {
        bootstrap.Modal.getInstance(document.getElementById('eventModal'))?.hide();
        disconnectTeacher();
        Swal.fire({
            icon: 'info',
            title: 'Disconnected',
            text:  '🔒 You have been disconnected successfully.',
            confirmButtonColor: '#4D44B5',
            timer: 3000,
            timerProgressBar: true,
        });
    }, 300);
});


/* ─────────────────────────────────────────────────────────────
   5. CAMERA — QR code scanning for auth
───────────────────────────────────────────────────────────── */

let cameraStream   = null;
let qrScanInterval = null;

function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
        .then(stream => {
            cameraStream = stream;
            const video  = document.getElementById('auth-camera');
            video.srcObject = stream;
            document.getElementById('qr-scan-status').textContent = '🔍 Scanning for QR code...';
            qrScanInterval = setInterval(scanQRFrame, 500);
        })
        .catch(err => {
            document.getElementById('qr-scan-status').textContent = '❌ Camera not available';
            console.error('Camera error:', err);
        });
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(t => t.stop());
        cameraStream = null;
    }
    if (qrScanInterval) {
        clearInterval(qrScanInterval);
        qrScanInterval = null;
    }
}

function scanQRFrame() {
    const video  = document.getElementById('auth-camera');
    const canvas = document.getElementById('auth-canvas');
    if (!video || video.readyState !== video.HAVE_ENOUGH_DATA) return;

    canvas.width  = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    // const code = jsQR(...); if (code) verifyQRCode(code.data);
}


/* ─────────────────────────────────────────────────────────────
   6. QR FULLSCREEN OVERLAY — idle screensaver
───────────────────────────────────────────────────────────── */

let qrOverlayTimer     = null;
let qrOverlayGenerated = false;
const QR_IDLE_SECONDS  = 10;

function generateOverlayQRCodes() {
    if (qrOverlayGenerated) return;
    new QRCode(document.getElementById('qr-overlay-ios'), {
        text: 'https://apps.apple.com/ch/app/unistudious/id6756975616',
        width: 280, height: 280,
        colorDark: '#2d2680', colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H,
    });
    new QRCode(document.getElementById('qr-overlay-android'), {
        text: 'https://play.google.com/store/apps/details?id=com.unistudious.projet1v2&hl=fr',
        width: 280, height: 280,
        colorDark: '#1a7a40', colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H,
    });
    qrOverlayGenerated = true;
}

function isAnyModalOrSwalOpen() {
    return !!(document.querySelector('.modal.show') || document.querySelector('.swal2-container'));
}

function showQROverlay() {
    if (isAnyModalOrSwalOpen()) { resetQROverlayTimer(); return; }
    generateOverlayQRCodes();
    document.getElementById('qr-fullscreen-overlay').style.display = 'flex';
}

function hideQROverlay() {
    document.getElementById('qr-fullscreen-overlay').style.display = 'none';
    resetQROverlayTimer();
}

function resetQROverlayTimer() {
    clearTimeout(qrOverlayTimer);
    if (isAnyModalOrSwalOpen()) return;
    qrOverlayTimer = setTimeout(showQROverlay, QR_IDLE_SECONDS * 1000);
}

['touchstart', 'mousemove', 'keydown', 'click'].forEach(evt => {
    document.addEventListener(evt, () => {
        const overlay = document.getElementById('qr-fullscreen-overlay');
        if (overlay.style.display === 'flex') { hideQROverlay(); return; }
        if (isAnyModalOrSwalOpen()) return;
        resetQROverlayTimer();
    });
});

document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('show.bs.modal', () => {
        clearTimeout(qrOverlayTimer);
        document.getElementById('qr-fullscreen-overlay').style.display = 'none';
    });
    modal.addEventListener('hidden.bs.modal', () => {
        if (!document.querySelector('.modal.show')) resetQROverlayTimer();
    });
});

resetQROverlayTimer();


/* ─────────────────────────────────────────────────────────────
   7. LANGUAGE SWITCHER (i18n)
───────────────────────────────────────────────────────────── */

const translations = {
    en: {
        subtitle: 'Schedule & Calendar System',
        addSchedule: '+ Add Schedule',
        modalTitle: 'Add New Schedule',
        labelSession: 'Session', labelGroup: 'Group', labelType: 'Type',
        labelStartDate: 'Start Date', labelRoom: 'Room',
        labelSubject: 'Teacher And Subject', labelCompletion: 'Completion Tag',
        labelDuplicate: 'Duplicate', labelStartTime: 'Start Time',
        labelEndTime: 'End Time', labelEndDate: 'End Date (for recurring events)',
        labelDescription: 'Description', btnCancel: 'Cancel', btnSave: 'Save',
        btnClose: 'Close', authTitle: 'Teacher Authentication',
        authSubtitle: 'Please verify your identity to continue',
        tabPassword: '🔑 Username & Password', tabQr: '📷 Scan QR Code',
        labelUsername: 'Username', labelPassword: 'Password',
        btnLogin: 'Login & Continue', btnBack: '← Back to Login',
    },
    fr: {
        subtitle: 'Système de Planning & Calendrier',
        addSchedule: '+ Ajouter un Planning',
        modalTitle: 'Ajouter un Nouveau Planning',
        labelSession: 'Session', labelGroup: 'Groupe', labelType: 'Type',
        labelStartDate: 'Date de début', labelRoom: 'Salle',
        labelSubject: 'Enseignant et Matière', labelCompletion: 'Tag de Complétion',
        labelDuplicate: 'Dupliquer', labelStartTime: 'Heure de début',
        labelEndTime: 'Heure de fin', labelEndDate: 'Date de fin (événements récurrents)',
        labelDescription: 'Description', btnCancel: 'Annuler', btnSave: 'Enregistrer',
        btnClose: 'Fermer', authTitle: 'Authentification Enseignant',
        authSubtitle: 'Veuillez vérifier votre identité pour continuer',
        tabPassword: '🔑 Nom d\'utilisateur & Mot de passe', tabQr: '📷 Scanner le QR Code',
        labelUsername: 'Nom d\'utilisateur', labelPassword: 'Mot de passe',
        btnLogin: 'Se connecter & Continuer', btnBack: '← Retour à la connexion',
    },
};

function setLang(lang) {
    localStorage.setItem('lang', lang);
    document.querySelectorAll('[data-key]').forEach(el => {
        const key = el.getAttribute('data-key');
        if (translations[lang]?.[key]) el.textContent = translations[lang][key];
    });
    const select = document.getElementById('lang-select');
    if (select) select.value = lang;
    document.documentElement.lang = lang;
    window.currentLang = lang;
}

setLang(localStorage.getItem('lang') || 'en');


/* ─────────────────────────────────────────────────────────────
   8. SPECIAL GROUP — helpers
───────────────────────────────────────────────────────────── */

let allStudents        = [];
let selectedStudentIds = [];

function renderStudentList(students) {
    const container = document.getElementById('sg-student-list');
    if (!container) return;
    if (!students.length) {
        container.innerHTML = '<p style="text-align:center;color:#aaa;font-size:13px;padding:20px 0;margin:0;">No students found</p>';
        return;
    }
    container.innerHTML = students.map(s => `
        <label style="display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;
                      cursor:pointer;transition:background 0.15s;font-size:13px;"
               onmouseover="this.style.background='#f5f5ff'"
               onmouseout="this.style.background='transparent'">
            <input type="checkbox" value="${s.id}"
                   ${selectedStudentIds.includes(String(s.id)) ? 'checked' : ''}
                   onchange="toggleStudent(this)"
                   style="width:16px;height:16px;accent-color:#4D44B5;cursor:pointer;">
            <span>${s.name || s.full_name || (s.first_name + ' ' + s.last_name)}</span>
        </label>
    `).join('');
}

function toggleStudent(checkbox) {
    const id = checkbox.value;
    if (checkbox.checked) {
        if (!selectedStudentIds.includes(id)) selectedStudentIds.push(id);
    } else {
        selectedStudentIds = selectedStudentIds.filter(x => x !== id);
    }
}

function generateDescription() {
    const name        = document.getElementById('sg-name').value.trim();
    const startDate   = document.getElementById('sg-end-date').value;
    const startTime   = document.getElementById('sg-start-time').value;
    const endTime     = document.getElementById('sg-end-time').value;
    const subjectEl   = document.getElementById('sg-subject');
    const subjectText = subjectEl.options[subjectEl.selectedIndex]?.text || '';

    if (!name && !startDate && !startTime && !endTime && !subjectText) return;

    let subject = '', teacher = '';
    if (subjectText.includes(' - ')) {
        [subject, teacher] = subjectText.split(' - ');
    } else {
        subject = subjectText;
    }

    const dateTime    = (startDate && startTime) ? `${startDate} ${startTime}` : (startDate || '');
    const dateTimeEnd = (startDate && endTime)   ? `${startDate} ${endTime}`   : (endTime   || '');

    let desc = '';
    if (name)        desc += `Group "${name}" has learning`;
    if (dateTime)    desc += ` from ${dateTime}`;
    if (dateTimeEnd) desc += ` to ${dateTimeEnd}`;
    if (subject)     desc += ` on Subject "${subject}"`;
    if (teacher)     desc += ` with Teacher "${teacher}"`;

    document.getElementById('sg-description').value = desc;
}


/* ─────────────────────────────────────────────────────────────
   9. SPECIAL GROUP — dynamic dropdowns - calls endpoints
───────────────────────────────────────────────────────────── */

async function loadSpecialGroupDropdowns() {
    const accountId = document.getElementById('eventAccountId').value;
    const sessionSelect = document.getElementById('sg-session');
    const roomSelect = document.getElementById('sg-room');
    const subjectSelect = document.getElementById('sg-subject');

    if (!sessionSelect) return console.error('Session select not found');

    // --- SESSION LOADING ---
    sessionSelect.innerHTML = '<option value="" selected disabled>Select a Session</option>';
    if (!accountId) return console.warn('No account ID provided');

    try {
        const response = await fetch(`/get-session/${accountId}`, {
            headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
            const result   = await response.json();
            const sessions = result.data || result;
            if (Array.isArray(sessions) && sessions.length > 0) {
                sessions.forEach(s => _addOption(sessionSelect, s.id, s.formation));
            } else {
                _addOption(sessionSelect, '', 'No sessions available', true);
            }
        } else {
            _addOption(sessionSelect, '', 'Error loading sessions', true);
        }
    } catch {
        _addOption(sessionSelect, '', 'Connection error', true);
    }

    try { $(sessionSelect).selectpicker('refresh'); } catch(e) {}

    // --- ROOM LOADING ---
    if (!roomSelect) return console.error('Room select not found');
    roomSelect.innerHTML = '<option value="" selected disabled>Select a Room</option>';

    try {
        const localId = document.getElementById('eventLocalId')?.value
                     || document.getElementById('local_id')?.value
                     || accountId;

        const roomResponse = await fetch(`/get-room-local/${localId}`, {
            headers: { 'Content-Type': 'application/json' }
        });
        if (roomResponse.ok) {
            const result = await roomResponse.json();
            const { data: rooms } = result;
            if (Array.isArray(rooms) && rooms.length > 0) {
                rooms.forEach(room => _addOption(roomSelect, room.id, room.name));
            } else {
                _addOption(roomSelect, '', 'No rooms available', true);
            }
        } else {
            _addOption(roomSelect, '', 'Error loading rooms', true);
        }
    } catch(e) {
        _addOption(roomSelect, '', 'Connection error', true);
    }

    try { $(roomSelect).selectpicker('refresh'); } catch(e) {}

    // --- TEACHER LOADING — remove old listener first, then attach fresh one ---
    if (!subjectSelect) return console.error('Subject select not found');

    subjectSelect.innerHTML = '<option value="" selected disabled>Select a Subject and Teacher</option>';
    try { $(subjectSelect).selectpicker('refresh'); } catch(e) {}

    // ✅ Remove old handler if exists, then attach new one
    if (sessionSelect._teacherLoadHandler) {
        sessionSelect.removeEventListener('change', sessionSelect._teacherLoadHandler);
    }

    sessionSelect._teacherLoadHandler = async function () {
        const sessionId = this.value;
        if (!sessionId) return;

        subjectSelect.innerHTML = '<option value="" selected disabled>Loading teachers...</option>';
        try { $(subjectSelect).selectpicker('refresh'); } catch(e) {}

        try {
            const response = await fetch(`/get-teacher/${sessionId}`, {
                headers: { 'Content-Type': 'application/json' }
            });
            if (response.ok) {
                const result   = await response.json();
                const teachers = result.data || result;
                subjectSelect.innerHTML = '<option value="" selected disabled>Select a Subject and Teacher</option>';

                if (Array.isArray(teachers) && teachers.length > 0) {
                    teachers.forEach(t => {
                        const opt = document.createElement('option');
                        opt.value = t.id;
                        opt.setAttribute('data-subject', t.subject_id);
                        opt.setAttribute('data-user',    t.user_id);
                        opt.textContent = `Subject : ${t.subject_name} - Teacher : ${t.full_name}`;
                        subjectSelect.appendChild(opt);
                    });
                } else {
                    _addOption(subjectSelect, '', 'No teachers available', true);
                }
            } else {
                _addOption(subjectSelect, '', 'Error loading teachers', true);
            }
        } catch {
            _addOption(subjectSelect, '', 'Connection error', true);
        }

        try { $(subjectSelect).selectpicker('refresh'); } catch(e) {}
    };

    sessionSelect.addEventListener('change', sessionSelect._teacherLoadHandler);
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/* ─────────────────────────────────────────────────────────────
   10. SPECIAL GROUP — modal open / close / save
───────────────────────────────────────────────────────────── */

function openSpecialGroupModal() {
    bootstrap.Modal.getInstance(document.getElementById('eventModal'))?.hide();
    document.getElementById('specialGroupForm').reset();

    ['sg-name-error','sg-capacity-error','sg-access-error','sg-type-error',
     'sg-session-error','sg-startdate-error','sg-starttime-error',
     'sg-endtime-error','sg-room-error','sg-subject-error','sg-date-error']
    .forEach(id => document.getElementById(id).classList.add('d-none'));

    const modalElement = document.getElementById('specialGroupModal');
    const modal = new bootstrap.Modal(modalElement);

    // Remove any existing event listeners to avoid duplicates
    modalElement.removeEventListener('shown.bs.modal', loadSpecialGroupDropdowns);

    // Add event listener to load dropdowns when modal is fully shown
    modalElement.addEventListener('shown.bs.modal', function onShown() {
        loadSpecialGroupDropdowns();
        // Remove the event listener after execution
        modalElement.removeEventListener('shown.bs.modal', onShown);
    });

    modal.show();
}

document.getElementById('specialGroupBackBtn').addEventListener('click', () => {
    bootstrap.Modal.getInstance(document.getElementById('specialGroupModal'))?.hide();
    setTimeout(() => new bootstrap.Modal(document.getElementById('eventModal')).show(), 300);
});

document.getElementById('specialGroupCloseBtn').addEventListener('click', () => {
    bootstrap.Modal.getInstance(document.getElementById('specialGroupModal'))?.hide();
    setTimeout(() => new bootstrap.Modal(document.getElementById('eventModal')).show(), 300);
});

// Live description generation
['sg-name','sg-end-date','sg-start-time','sg-end-time','sg-subject'].forEach(id => {
    document.getElementById(id).addEventListener('change', generateDescription);
    document.getElementById(id).addEventListener('input',  generateDescription);
});

document.getElementById('specialGroupSaveBtn').addEventListener('click', function () {
    let valid = true;

    const fields = [
        { id: 'sg-name',        errId: 'sg-name-error',      msg: '❌ Group name is required',         check: v => !!v.trim() },
        { id: 'sg-capacity',    errId: 'sg-capacity-error',   msg: '❌ Capacity is required',           check: v => v && parseInt(v) >= 1 },
        { id: 'sg-access-type', errId: 'sg-access-error',     msg: '❌ Please select an access type',   check: v => !!v },
        { id: 'sg-type',        errId: 'sg-type-error',       msg: '❌ Please select a type',           check: v => !!v },
        { id: 'sg-session',     errId: 'sg-session-error',    msg: '❌ Please select a session',        check: v => !!v },
        { id: 'sg-end-date',    errId: 'sg-startdate-error',  msg: '❌ Start date is required',         check: v => !!v },
        { id: 'sg-start-time',  errId: 'sg-starttime-error',  msg: '❌ Start time is required',         check: v => !!v },
        { id: 'sg-end-time',    errId: 'sg-endtime-error',    msg: '❌ End time is required',           check: v => !!v },
        { id: 'sg-room',        errId: 'sg-room-error',       msg: '❌ Please select a room',           check: v => !!v },
        { id: 'sg-subject',     errId: 'sg-subject-error',    msg: '❌ Please select a subject',        check: v => !!v },
    ];

    fields.forEach(({ id, errId, msg, check }) => {
        const val = document.getElementById(id).value;
        const err = document.getElementById(errId);
        if (!check(val)) {
            err.textContent = msg;
            err.classList.remove('d-none');
            valid = false;
        } else {
            err.classList.add('d-none');
        }
    });

    if (!valid) return;

    const payload = {
        name:        document.getElementById('sg-name').value.trim(),
        subject_id:  document.getElementById('sg-subject').value,
        capacity:    parseInt(document.getElementById('sg-capacity').value) || null,
        start_date:  document.getElementById('sg-end-date').value || null,
        end_date:    null,
        description: document.getElementById('sg-description').value.trim(),
        is_special:  true,
    };

    const btn = this;
    btn.textContent = 'Saving...';
    btn.disabled    = true;

    fetch('/api/create-special-group', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
    })
    .then(r => r.json())
    .then(data => {
        btn.textContent = '✅ Create Group & Continue';
        btn.disabled    = false;

        if (data.status === 'ok' || data.id) {
            const groupSelect = document.getElementById('group_id');
            const newOption   = new Option(`⭐ ${payload.name} (Special)`, data.id || data.group_id, true, true);
            newOption.style.color = '#4D44B5';
            groupSelect.appendChild(newOption);

            bootstrap.Modal.getInstance(document.getElementById('specialGroupModal'))?.hide();
            setTimeout(() => {
                new bootstrap.Modal(document.getElementById('eventModal')).show();
                Swal.fire({
                    icon: 'success',
                    title: 'Special Group Created!',
                    html:  `<b>${payload.name}</b> has been created and selected.`,
                    confirmButtonColor: '#4D44B5',
                    timer: 3000, timerProgressBar: true,
                });
            }, 300);
        } else {
            Swal.fire({ icon: 'error', title: 'Error', text: data.message || 'Failed to create special group.', confirmButtonColor: '#4D44B5' });
        }
    })
    .catch(() => {
        btn.textContent = '✅ Create Group & Continue';
        btn.disabled    = false;
        Swal.fire({ icon: 'error', title: 'Network Error', text: 'Could not reach the server. Please try again.', confirmButtonColor: '#4D44B5' });
    });
});