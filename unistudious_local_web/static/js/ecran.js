document.addEventListener('DOMContentLoaded', function () {
	var calendarEl = document.getElementById('calendar');
	var tipEl = document.getElementById('tip');
	var clockEl = document.getElementById('clock');

	// account id comes from data-account-id on #calendar (set from the URL: /ecran/3)
	var ACCOUNT_ID = parseInt(calendarEl.dataset.accountId, 10);
	var DEFAULT_VIEW = calendarEl.dataset.view || 'dayGridMonth';
	var REFRESH_MS = 60000;      // reload events every minute
	var IDLE_RESET_MS = 120000;  // after 2 min without activity, go back to today + default view + all salles

	// ---------- keypad: one key per salle ----------
	// The Arduino keypad sends F13..F16. Put the REAL room id of each salle here.
	var ROOMS = {
		F13: { id: 7, name: 'Salle 1' },
		F14: { id: 10, name: 'Salle 2' },
		F15: { id: 12, name: 'Salle 3' },
		F16: { id: 13, name: 'Salle 4' }
	};
	// keys 1-4 on a normal keyboard do the same (handy for testing without the Arduino)
	var KEY_ALIASES = { '1': 'F13', '2': 'F14', '3': 'F15', '4': 'F16' };
	// the keypad is detected by the PHYSICAL key (e.code), so it works with any keyboard layout
	// (on a French AZERTY layout the key "1" types "&" and "2" types "é")
	var CODE_ALIASES = {
		Digit1: 'F13', Digit2: 'F14', Digit3: 'F15', Digit4: 'F16',
		Numpad1: 'F13', Numpad2: 'F14', Numpad3: 'F15', Numpad4: 'F16'
	};
	var ALSO_DIGITS = true;

	var currentKey = null; // null = all salles

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
		if (!s) return null;
		var str = String(s);
		var d = new Date(str);
		if (isNaN(d.getTime())) return null;

		// "…GMT" / "…UTC" / "…Z": wall-clock time disguised as UTC, so read it with the UTC getters
		if (/GMT|UTC|Z$/.test(str)) {
			return new Date(
				d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(),
				d.getUTCHours(), d.getUTCMinutes(), d.getUTCSeconds()
			);
		}

		// no timezone in the string: it was already parsed as local wall-clock, keep it as is
		return d;
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
		if (modalEl.style.display === 'flex') return; // a session window is open

		var down = e.code === 'ArrowDown' || e.code === 'PageDown' || e.code === 'KeyD';
		var up = e.code === 'ArrowUp' || e.code === 'PageUp' || e.code === 'KeyC';
		var next = e.code === 'ArrowRight' || e.code === 'KeyA';
		var prev = e.code === 'ArrowLeft' || e.code === 'KeyB';

		if (down) {
			e.preventDefault();
			scrollCalendar(1);
		} else if (up) {
			e.preventDefault();
			scrollCalendar(-1);
		} else if (next) {
			e.preventDefault();
			hideTip();
			calendar.next();   // next week (or day/month, depending on the view)
		} else if (prev) {
			e.preventDefault();
			hideTip();
			calendar.prev();   // previous week
		}
	});
	// ---------- label of the selected salle (a button in the calendar toolbar) ----------
	var styleEl = document.createElement('style');
	styleEl.textContent =
		'.fc .fc-roomLabel-button{' +
			'pointer-events:none;' +
			'background:#4c4b9e !important;border:3px solid #4c4b9e !important;color:#fff !important;' +
			'font-size:1.6rem !important;font-weight:800 !important;line-height:1.2 !important;' +
			'padding:8px 28px !important;margin-left:16px !important;border-radius:12px !important;' +
			'text-transform:uppercase;letter-spacing:1px;box-shadow:0 4px 12px rgba(0,0,0,.25);' +
		'}' +
		'.fc .fc-roomLabel-button.room-active{' +
			'background:#2e9e5b !important;border-color:#1f7a43 !important;' +
			'font-size:2rem !important;padding:10px 36px !important;' +
			'animation:roomPulse 1.2s ease-out 1;' +
		'}' +
		'@keyframes roomPulse{0%{transform:scale(.85)}60%{transform:scale(1.08)}100%{transform:scale(1)}}';
	document.head.appendChild(styleEl);

	function updateRoomLabel() {
		var btn = calendarEl.querySelector('.fc-roomLabel-button');
		if (!btn) return;
		btn.textContent = currentKey ? ROOMS[currentKey].name : 'All salles';
		btn.classList.toggle('room-active', !!currentKey);
	}

	// height = from the top of the calendar to the bottom of the screen
	function fitHeight() {
		return window.innerHeight - calendarEl.getBoundingClientRect().top - 16;
	}

	// ---------- calendar (the user can navigate, but nothing can be edited) ----------
	var calendar = new FullCalendar.Calendar(calendarEl, {
		initialView: DEFAULT_VIEW,
		initialDate: new Date(),
		customButtons: {
			roomLabel: { text: 'All salles', click: function () {} }
		},
		headerToolbar: {
			left: 'prev,next today roomLabel',
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

		// the toolbar is redrawn when the date or the view changes: put the label back
		datesSet: function () {
			setTimeout(updateRoomLabel, 0);
		},

		events: function (info, successCallback, failureCallback) {
			var url;

			if (currentKey) {
				// one salle only
				url = '/api/get_calander_per_room/' + ROOMS[currentKey].id;
			} else {
				if (!ACCOUNT_ID) {
					console.error('ecran: missing data-account-id on #calendar');
					successCallback([]);
					return;
				}
				url = '/api/get-all-calander/' + ACCOUNT_ID;
			}

			fetch(url, { cache: 'no-store' })
				.then(function (r) {
					if (!r.ok) throw new Error('HTTP ' + r.status);
					return r.json();
				})
				.then(function (res) {
					console.log('ecran: response from', url, res); // open F12 > Console to see it
					var list = Array.isArray(res) ? res : (res.data || res.Data || res.result || []);
					var events = [];

					list.forEach(function (item) {
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
								room_name: item.room_name || item.name || (currentKey ? ROOMS[currentKey].name : 'Salle ' + item.room_id),
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
	updateRoomLabel();

	// ---------- keypad handling ----------
	function selectRoom(key) {
		// same key again = back to all salles
		currentKey = (currentKey === key) ? null : key;
		closeModal();
		hideTip();
		updateRoomLabel();
		calendar.refetchEvents();
	}

	function resetRoom() {
		if (!currentKey) return;
		currentKey = null;
		updateRoomLabel();
		calendar.refetchEvents();
	}

	document.addEventListener('keydown', function (e) {
		var key = e.key;
		if (ALSO_DIGITS) {
			if (CODE_ALIASES[e.code]) key = CODE_ALIASES[e.code];
			else if (KEY_ALIASES[e.key]) key = KEY_ALIASES[e.key];
		}
		if (!ROOMS[key]) return;
		e.preventDefault();
		if (e.repeat) return;
		selectRoom(key);
	});

		// ---------- scroll the calendar with the keypad (D = down, C = up) ----------
        // the keypad sends Arrow Down / Arrow Up (or letters D / C), so a normal keyboard works too
        var SCROLL_STEP = 0.6; // fraction of the visible height scrolled by one press

        	function findScroller() {
		var best = null;
		var bestOverflow = 1;
		var all = calendarEl.querySelectorAll('*');
		for (var i = 0; i < all.length; i++) {
			var el = all[i];
			var oy = getComputedStyle(el).overflowY;
			if (oy !== 'auto' && oy !== 'scroll' && oy !== 'hidden') continue;
			var overflow = el.scrollHeight - el.clientHeight;
			if (overflow > bestOverflow) {
				best = el;
				bestOverflow = overflow;
			}
		}
		if (!best) {
			var page = document.scrollingElement || document.documentElement;
			console.log('ecran: no scroller. page', page.scrollHeight, 'vs', page.clientHeight,
				'| calendar', calendarEl.scrollHeight, 'vs', calendarEl.clientHeight);
			if (page.scrollHeight > page.clientHeight + 1) best = page;
		}
		return best;
	}

        function scrollCalendar(direction) {
            var target = findScroller();
            console.log('ecran: scroll', direction, target);
            if (!target) return;
            target.scrollBy({ top: direction * target.clientHeight * SCROLL_STEP, behavior: 'smooth' });
        }

        document.addEventListener('keydown', function (e) {
            if (modalEl.style.display === 'flex') return; // a session window is open

            var down = e.code === 'ArrowDown' || e.code === 'PageDown' || e.code === 'KeyD';
            var up = e.code === 'ArrowUp' || e.code === 'PageUp' || e.code === 'KeyC';

            if (down) {
                e.preventDefault();
                scrollCalendar(1);
            } else if (up) {
                e.preventDefault();
                scrollCalendar(-1);
            }
        });

	// keep the calendar filling the screen (after fonts/CSS load, and on resize or F11)
	function refit() {
		calendar.setOption('height', fitHeight());
	}
	window.addEventListener('load', refit);
	window.addEventListener('resize', refit);

	// reload the events every minute (keeps the selected salle and the date being viewed)
	setInterval(function () {
		calendar.refetchEvents();
	}, REFRESH_MS);

	// when nobody touches anything for a while: today, default view, all salles
	var lastActivity = Date.now();
	['mousemove', 'mousedown', 'wheel', 'touchstart', 'keydown'].forEach(function (ev) {
		document.addEventListener(ev, function () { lastActivity = Date.now(); }, true);
	});
	setInterval(function () {
		if (Date.now() - lastActivity < IDLE_RESET_MS) return;
		hideTip();
		closeModal();
		resetRoom();
		if (calendar.view.type !== DEFAULT_VIEW) calendar.changeView(DEFAULT_VIEW);
		calendar.today();
	}, 30000);
});