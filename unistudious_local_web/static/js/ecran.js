document.addEventListener('DOMContentLoaded', function () {
	var calendarEl = document.getElementById('calendar');
	var tipEl = document.getElementById('tip');
	var clockEl = document.getElementById('clock');

	// account id comes from data-account-id on #calendar (set from the URL: /ecran/3)
	var ACCOUNT_ID = parseInt(calendarEl.dataset.accountId, 10);
	var DEFAULT_VIEW = calendarEl.dataset.view || 'dayGridMonth';
	var REFRESH_MS = 60000;
	var IDLE_RESET_MS = 120000;
	var MAX_PER_DAY = 3;

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
		if (e.target === modalEl) closeModal();
	});
	document.addEventListener('keydown', function (e) {
		if (e.key === 'Escape') closeModal();
	});

	// height = from the top of the calendar to the bottom of the screen
	function fitHeight() {
		return window.innerHeight - calendarEl.getBoundingClientRect().top - 16;
	}

	// ---------- scroll to the current day (month view) ----------
	var needScroll = true;

	function scrollToToday() {
		var todayEl = calendarEl.querySelector('.fc-daygrid-day.fc-day-today');
		if (!todayEl) return;
		var scroller = todayEl.closest('.fc-scroller');
		if (!scroller) return;
		var top = todayEl.getBoundingClientRect().top - scroller.getBoundingClientRect().top + scroller.scrollTop;
		scroller.scrollTop = Math.max(0, top - 10);
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
		dayMaxEvents: MAX_PER_DAY, // max 3 sessions per day, then "+N more" (click opens a popup)
		moreLinkClick: 'popover',
		navLinks: true,       // click a day number to open that day
		editable: false,      // no drag, no resize
		droppable: false,
		selectable: false,

		// every time the visible dates change, scroll again once the events are drawn
		datesSet: function () {
			needScroll = true;
		},

		// events are drawn -> row heights are final -> scroll to today (only once per date change,
		// so the minute refresh does not move the screen)
		eventsSet: function () {
			if (!needScroll) return;
			needScroll = false;
			setTimeout(scrollToToday, 0);
		},

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
	window.addEventListener('load', function () {
		refit();
		setTimeout(scrollToToday, 100); // once more after the final layout
	});
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
		setTimeout(scrollToToday, 50);
	}, 30000);
});