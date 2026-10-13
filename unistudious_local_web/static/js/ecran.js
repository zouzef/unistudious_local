document.addEventListener('DOMContentLoaded', function () {
	var calendarEl = document.getElementById('calendar');
	var tipEl = document.getElementById('tip');
	var clockEl = document.getElementById('clock');

	// account id comes from data-account-id on #calendar (set from the URL: /ecran/3)
	var ACCOUNT_ID = parseInt(calendarEl.dataset.accountId, 10);
	var DEFAULT_VIEW = calendarEl.dataset.view || 'dayGridMonth';
	var REFRESH_MS = 60000;      // reload events every minute
	var IDLE_RESET_MS = 120000;  // after 2 min without mouse activity, go back to today + default view

	// ---------- clock ----------
	function tick() {
		if (!clockEl) return; // the clock is optional
		var d = new Date();
		clockEl.textContent = d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
	}
	tick();
	setInterval(tick, 1000);

	// ---------- dates ----------
	// Server sends e.g. "Tue, 08 Jul 2025 13:00:00 GMT" but it is really the wall-clock time.
	// Reading it with the UTC getters shows it as-is, whatever the timezone of this PC.
	function parseServerDate(s) {
		var d = new Date(s);
		if (isNaN(d.getTime())) return null;
		return new Date(
			d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(),
			d.getUTCHours(), d.getUTCMinutes(), d.getUTCSeconds()
		);
	}

	function fmtTime(date) {
		return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
	}

	function fmtDate(date) {
		return date.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
	}

	function esc(s) {
		var el = document.createElement('div');
		el.textContent = s == null ? '' : s;
		return el.innerHTML;
	}

	// Teacher full name is inside the description: ... with Teacher "Mkaissi khalil"
	function teacherName(item) {
		var m = /Teacher "([^"]+)"/.exec(item.description || '');
		return (m && m[1]) || item.username || '-';
	}

	// ---------- tooltip (hover) ----------
	function showTip(event, e) {
		var p = event.extendedProps;
		tipEl.innerHTML =
			'<div class="t-title">' + esc(event.title) + '</div>' +
			'<div class="t-row"><span>Time: </span>' + fmtTime(event.start) +
				(event.end ? ' - ' + fmtTime(event.end) : '') + '</div>' +
			'<div class="t-row"><span>Salle: </span>' + esc(p.room_name) + '</div>' +
			'<div class="t-row"><span>Teacher: </span>' + esc(p.teacher_name) + '</div>';
		tipEl.style.display = 'block';
		moveTip(e);
	}

	function moveTip(e) {
		var pad = 16;
		var w = tipEl.offsetWidth;
		var h = tipEl.offsetHeight;
		var x = e.clientX + pad;
		var y = e.clientY + pad;
		if (x + w > window.innerWidth) x = e.clientX - w - pad;
		if (y + h > window.innerHeight) y = e.clientY - h - pad;
		tipEl.style.left = x + 'px';
		tipEl.style.top = y + 'px';
	}

	function hideTip() {
		tipEl.style.display = 'none';
	}

	// ---------- modal (click on a session) ----------
	var modalEl = document.getElementById('ev-modal');
	var modalBody = document.getElementById('ev-modal-body');

	function openModal(event) {
		var p = event.extendedProps;
		modalBody.innerHTML =
			'<div class="m-title" style="border-left:6px solid ' + esc(event.backgroundColor || '#4c4b9e') + '">' + esc(event.title) + '</div>' +
			'<div class="m-row"><span>Date</span><b>' + esc(fmtDate(event.start)) + '</b></div>' +
			'<div class="m-row"><span>Time</span><b>' + fmtTime(event.start) + (event.end ? ' - ' + fmtTime(event.end) : '') + '</b></div>' +
			'<div class="m-row"><span>Salle</span><b>' + esc(p.room_name) + '</b></div>' +
			'<div class="m-row"><span>Teacher</span><b>' + esc(p.teacher_name) + '</b></div>' +
			(p.description ? '<div class="m-row"><span>Details</span><b>' + esc(p.description) + '</b></div>' : '');
		modalEl.style.display = 'flex';
	}

	function closeModal() {
		modalEl.style.display = 'none';
	}

	document.getElementById('ev-modal-close').addEventListener('click', closeModal);
	modalEl.addEventListener('click', function (e) {
		if (e.target === modalEl) closeModal(); // click on the dark background
	});
	document.addEventListener('keydown', function (e) {
		if (e.key === 'Escape') closeModal();
	});

	// height = from the top of the calendar to the bottom of the screen
	function fitHeight() {
		return window.innerHeight - calendarEl.getBoundingClientRect().top - 16;
	}

	// ---------- calendar (the user can navigate, but nothing can be edited) ----------
	var calendar = new FullCalendar.Calendar(calendarEl, {
		initialView: DEFAULT_VIEW,
		initialDate: new Date(),
		headerToolbar: {
			left: 'prev,next today',
			center: 'title',
			right: 'dayGridMonth,timeGridWeek,timeGridDay'
		},
		expandRows: true,
		height: fitHeight(),
		dayMaxEvents: false,  // show all events in the cell, no "+N more"
		navLinks: true,       // click a day number to open that day
		editable: false,      // no drag, no resize
		droppable: false,
		selectable: false,

		events: function (info, successCallback, failureCallback) {
			if (!ACCOUNT_ID) {
				console.error('ecran: missing data-account-id on #calendar');
				successCallback([]);
				return;
			}

			fetch('/api/get-all-calander/' + ACCOUNT_ID, { cache: 'no-store' })
				.then(function (r) {
					if (!r.ok) throw new Error('HTTP ' + r.status);
					return r.json();
				})
				.then(function (res) {
					var events = [];
					(res.data || []).forEach(function (item) {
						var start = parseServerDate(item.start_time);
						var end = parseServerDate(item.end_time);
						if (!start) return;

						events.push({
							title: item.title,
							start: start,
							end: end,
							backgroundColor: item.color,
							borderColor: item.color,
							extendedProps: {
								room_name: item.name || ('Salle ' + item.room_id),
								teacher_name: teacherName(item),
								description: item.description || ''
							}
						});
					});
					successCallback(events);
				})
				.catch(function (err) {
					console.error('ecran fetch error:', err);
					failureCallback(err); // keeps the last display on screen
				});
		},

		// click on a session opens the modal
		eventClick: function (info) {
			info.jsEvent.preventDefault();
			hideTip();
			openModal(info.event);
		},

		eventDidMount: function (info) {
			info.el.addEventListener('mouseenter', function (e) { showTip(info.event, e); });
			info.el.addEventListener('mousemove', moveTip);
			info.el.addEventListener('mouseleave', hideTip);
		}
	});

	calendar.render();

	// keep the calendar filling the screen (after fonts/CSS load, and on resize or F11)
	function refit() {
		calendar.setOption('height', fitHeight());
	}
	window.addEventListener('load', refit);
	window.addEventListener('resize', refit);

	// reload the events every minute (does NOT move the user away from the date he is looking at)
	setInterval(function () {
		calendar.refetchEvents();
	}, REFRESH_MS);

	// when nobody touches the mouse for a while, come back to today in the default view
	var lastActivity = Date.now();
	['mousemove', 'mousedown', 'wheel', 'touchstart', 'keydown'].forEach(function (ev) {
		document.addEventListener(ev, function () { lastActivity = Date.now(); }, true);
	});
	setInterval(function () {
		if (Date.now() - lastActivity < IDLE_RESET_MS) return;
		hideTip();
		closeModal();
		if (calendar.view.type !== DEFAULT_VIEW) calendar.changeView(DEFAULT_VIEW);
		calendar.today();
	}, 30000);
});