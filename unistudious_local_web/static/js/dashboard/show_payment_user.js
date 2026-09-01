/* ==========================================================================
   Payment Session Management
   Handles: payment table rendering (DataTable), payment modal (view/edit/
   accept/cancel a payment), and status update modal (Not Registered -> Paid).
   ========================================================================== */

/* --------------------------------------------------------------------------
   1. Page context & shared state
   -------------------------------------------------------------------------- */

const pathParts = window.location.pathname.split('/').filter(Boolean);
const idUser    = parseInt(pathParts[pathParts.length - 2], 10);
const idSession = parseInt(pathParts[pathParts.length - 1], 10);

// Fixed price per session (separate from "amount", which is what's actually
// been paid so far). Set once loadPaymentData() fetches the session info.
let sessionPrice = 0;


/* --------------------------------------------------------------------------
   2. Formatting helpers
   -------------------------------------------------------------------------- */

/**
 * Format an ISO/date string as dd/mm/yyyy (en-GB), or 'N/A' if empty.
 */
const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-GB');
};

/**
 * Build a Bootstrap badge <span> for a given payment status.
 */
const getStatusBadge = (status) => {
    const badges = {
        'Paid':      'badge-success',
        'Unpaid':    'badge-danger',
        'Cancelled': 'badge-danger',
        'Pending':   'badge-warning',
    };
    const cls = badges[status] || 'badge-secondary';
    return `<span class="badge ${cls} light badge-sm">${status}</span>`;
};

/**
 * Apply custom styling to the DataTable pagination buttons.
 * Must be re-run on every draw (drawCallback) since DataTable re-renders them.
 */
function stylePaginationButtons() {
    const paginate = document.querySelector('.dataTables_paginate');
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
        btn.style.cursor  = 'default';
    });
}


/* --------------------------------------------------------------------------
   3. Payment modal — dynamic sub-section visibility
   -------------------------------------------------------------------------- */

/**
 * Shows/hides the "Accept Payment? Yes/No" section based on the amount
 * currently typed into the modal's amount field.
 * Only relevant when: status is Unpaid AND the entered amount is a partial
 * payment (0 < amount < sessionPrice).
 */
function updateAcceptSectionVisibility() {
    const status              = document.getElementById('hiddenOrderStatus').value;
    const enteredAmount       = parseFloat(document.getElementById('amount').value);
    const acceptSection       = document.getElementById('acceptPaymentSection');
    const remainingContainer  = document.getElementById('remainingPaymentContainer');
    const changePriceSection  = document.getElementById('changePriceSection');
    const newPriceSection     = document.getElementById('newPriceSection');

    const isPartialAmount = !isNaN(enteredAmount)
        && enteredAmount > 0
        && enteredAmount < sessionPrice;

    if (status === 'Unpaid' && isPartialAmount) {
        // Unpaid + partial amount -> ask "Accept Payment?" flow.
        acceptSection.style.display      = '';
        remainingContainer.style.display = 'none';
    } else if (status === 'Pending' && isPartialAmount) {
        // Pending + partial amount -> just show the Remaining Payment field.
        remainingContainer.style.display = '';
        acceptSection.style.display      = 'none';
        changePriceSection.style.display = 'none';
        newPriceSection.style.display    = 'none';
    } else {
        acceptSection.style.display      = 'none';
        remainingContainer.style.display = 'none';
        changePriceSection.style.display = 'none';
        newPriceSection.style.display    = 'none';
    }
}


/* --------------------------------------------------------------------------
   4. Data loading & table rendering
   -------------------------------------------------------------------------- */

/**
 * Build the action button(s) for a single payment row, based on its status.
 * Business rules:
 *  - "Not Registered" -> show a button to open the Status Update modal.
 *  - "Cancelled"       -> no action.
 *  - "Unpaid"          -> only the FIRST unpaid row in the list is payable;
 *                         subsequent unpaid rows are locked until the
 *                         earlier one is settled ("pay the previous week first").
 *  - anything else (Paid, Pending, ...) -> open the View Payment modal.
 *
 * @param {Object} item              Payment record from the API.
 * @param {boolean} firstUnpaidHandled  Whether an unpaid row has already been made actionable.
 * @returns {{ html: string, firstUnpaidHandled: boolean }}
 */
function buildActionButton(item, firstUnpaidHandled) {
    if (item.status === 'Not Registered') {
        return {
            html: `
                <button class="btn btn-outline-primary btn-sm update-status-btn"
                    data-id="${item.id}"
                    data-current-status="${item.status}"
                    data-next-status="Paid"
                    data-next-id="${item.id}"
                    data-bs-toggle="modal"
                    data-bs-target="#statusUpdateModal">
                    <i class="fa fa-sync-alt"></i> Update Status
                </button>`,
            firstUnpaidHandled
        };
    }

    if (item.status === 'Cancelled') {
        return { html: '', firstUnpaidHandled };
    }

    if (item.status === 'Unpaid' || item.status === 'Pending') {
        if (!firstUnpaidHandled) {
            return { html: buildViewPaymentButton(item), firstUnpaidHandled: true };
        }
        return {
            html: `
                <button class="btn btn-outline-warning btn-sm" disabled
                    title="Pay the previous week first">
                    <i class="fa fa-lock"></i>
                    View Payment
                </button>`,
            firstUnpaidHandled
        };
    }

    // Paid, Pending, or any other status: always viewable.
    return { html: buildViewPaymentButton(item), firstUnpaidHandled };
}

/**
 * Standard "View Payment" button that opens the payment modal pre-filled
 * with this row's data (via data-* attributes read in show.bs.modal below).
 */
function buildViewPaymentButton(item) {
    return `
        <button class="btn btn-outline-info btn-sm"
            data-bs-toggle="modal"
            data-bs-target="#paymentModal"
            data-id="${item.id}"
            data-user-id="${idUser}"
            data-session-id="${idSession}"
            data-amount="${item.amount ?? ''}"
            data-price="${item.price ? parseFloat(item.price).toFixed(2) : '0.00'} TND"
            data-description="${item.description ?? ''}"
            data-type-date="${item.type_date ?? ''}"
            data-status="${item.status}">
            <i class="fa fa-eye"></i>
            View Payment
        </button>`;
}

/**
 * Render a single <tr> for a payment record.
 */
function buildRow(item, firstUnpaidHandled) {
    const { html: actionHtml, firstUnpaidHandled: updatedFlag } = buildActionButton(item, firstUnpaidHandled);

    const rowHtml = `
        <tr>
            <td class="py-2">${item.id}</td>
            <td class="py-2">${item.type_date ?? 'N/A'}</td>
            <td class="py-2">${item.description ?? 'N/A'}</td>
            <td class="py-2 text-end">${getStatusBadge(item.status)}</td>
            <td class="py-2 text-end font-w600">${item.amount ? parseFloat(item.amount).toFixed(2) : '0.00'} TND</td>
            <td class="py-2 text-end font-w600">${formatDate(item.date_payment)}</td>
            <td class="py-2 text-end">${actionHtml}</td>
        </tr>`;

    return { rowHtml, firstUnpaidHandled: updatedFlag };
}

/**
 * Initialize (or re-initialize) the DataTable on #example with our
 * standard pagination icons and pagination button styling.
 */
function initDataTable(extraOptions = {}) {
    if ($.fn.dataTable.isDataTable('#example')) {
        $('#example').DataTable().destroy();
    }

    $('#example').DataTable({
        pageLength: 10,
        lengthChange: false,
        language: {
            paginate: {
                next:     '<i class="fas fa-angle-right"></i>',
                previous: '<i class="fas fa-angle-left"></i>'
            }
        },
        drawCallback: function () { stylePaginationButtons(); },
        ...extraOptions
    });
}

/**
 * Fetch the payment history for the current session/user and render:
 *  - header info (session name, student name, fixed session price)
 *  - the payments table with per-row action buttons
 */
function loadPaymentData() {
    fetch(`/api/get_payment_user_info_service/${idSession}/${idUser}`)
        .then(res => res.json())
        .then(data => {
            console.log(data);

            if (!data || data.length === 0) {
                document.getElementById('orders').innerHTML = `
                    <tr><td colspan="7" class="text-center">No payment records found</td></tr>`;
                initDataTable();
                return;
            }

            // Header info comes from the first record (session-level fields).
            const first = data[0];
            document.getElementById('info-session-name').textContent = first.name;
            document.getElementById('info-student-name').textContent = first.username;

            // Price is a fixed field per session (distinct from "amount" paid so far).
            sessionPrice = parseFloat(first.price) || 0;
            document.getElementById('info-price').textContent = `${sessionPrice.toFixed(2)} TND`;

            // Build all table rows, tracking which unpaid row (if any) is actionable.
            let firstUnpaidHandled = false;
            const rowsHtml = data.map(item => {
                const result = buildRow(item, firstUnpaidHandled);
                firstUnpaidHandled = result.firstUnpaidHandled;
                return result.rowHtml;
            }).join('');

            document.getElementById('orders').innerHTML = rowsHtml;

            initDataTable({ order: [[0, 'asc']] });
        })
        .catch(err => console.error('Error loading payment data:', err));
}


/* --------------------------------------------------------------------------
   5. API calls
   -------------------------------------------------------------------------- */

/**
 * PATCH-style update of a payment record.
 */
function updatePayment(paymentId, sessionId, userId, payload) {
    return fetch(`/api/update_payment_session_user/${paymentId}/${sessionId}/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).then(res => res.json());
}


/* --------------------------------------------------------------------------
   6. Page bootstrap & event wiring
   -------------------------------------------------------------------------- */

window.addEventListener('load', function () {

    // Destroy any pre-existing DataTable instance before the first load.
    if ($.fn.dataTable.isDataTable('#example')) {
        $('#example').DataTable().destroy();
    }

    loadPaymentData();

    /* ---------------- Payment Modal ---------------- */

    // Populate the modal with the clicked row's data.
    document.getElementById('paymentModal').addEventListener('show.bs.modal', function (e) {
        const btn = e.relatedTarget;
        if (!btn) return;

        const id          = btn.dataset.id;
        const userId      = btn.dataset.userId;
        const sessionId   = btn.dataset.sessionId;
        const amount      = btn.dataset.amount;
        const description = btn.dataset.description;
        const typeDate    = btn.dataset.typeDate;
        const status      = btn.dataset.status;

        // --- Display fields ---
        document.getElementById('modalOrderId').textContent  = id;
        document.getElementById('modalPrice').textContent    = `${sessionPrice.toFixed(2)} TND`;
        document.getElementById('modalTypeDate').textContent = typeDate || 'N/A';

        // --- Hidden fields (used on save) ---
        document.getElementById('hiddenOrderId').value     = id;
        document.getElementById('hiddenUserId').value      = userId;
        document.getElementById('hiddenSessionId').value   = sessionId;
        document.getElementById('hiddenOrderStatus').value = status;

        // --- Form fields ---
        const amountInput = document.getElementById('amount');
        amountInput.value = amount || '';

        // Amount is only editable when the order isn't already Paid or Pending.
        if (status === 'Paid' || status === 'Pending') {
            amountInput.setAttribute('disabled', 'disabled');
        } else {
            amountInput.removeAttribute('disabled');
        }

        document.getElementById('description').value = description || '';

        // Hide the cancel button / absent message once a payment is already Paid.
        const isPaid = status === 'Paid';
        document.getElementById('absentMessage').style.display  = isPaid ? 'none' : '';
        document.getElementById('cancel-payment').style.display = isPaid ? 'none' : '';

        // Reset sub-sections every time the modal opens; visibility is then
        // recalculated based on the (possibly pre-filled) amount.
        document.getElementById('remainingPayment').value = '';
        document.getElementById('newPrice').value         = '';
        document.getElementById('changePrice').value      = '';
        updateAcceptSectionVisibility();
    });

    // Re-evaluate the "Accept Payment" section live as the user types an amount.
    document.getElementById('amount').addEventListener('input', updateAcceptSectionVisibility);

    // Reset the modal's form/UI state when it's closed.
    document.getElementById('paymentModal').addEventListener('hidden.bs.modal', function () {
        document.getElementById('addPaymentForm').reset();
        document.getElementById('modalOrderId').textContent  = '';
        document.getElementById('modalPrice').textContent    = '';
        document.getElementById('modalTypeDate').textContent = '';

        document.getElementById('absentMessage').style.display             = '';
        document.getElementById('cancel-payment').style.display            = '';
        document.getElementById('acceptPaymentSection').style.display      = 'none';
        document.getElementById('remainingPaymentContainer').style.display = 'none';
        document.getElementById('changePriceSection').style.display        = 'none';
        document.getElementById('newPriceSection').style.display           = 'none';
    });

    // Accept Payment -> "Yes": reveal the "change price?" follow-up question.
    document.getElementById('acceptYes').addEventListener('click', function () {
        document.getElementById('changePriceSection').style.display = '';
    });

    // Accept Payment -> "No": show a rejection alert, then close the modal.
    document.getElementById('acceptNo').addEventListener('click', function () {
        Swal.fire({
            icon: 'error',
            title: 'Payment Rejected',
            text: 'You cannot proceed without accepting the payment.',
            confirmButtonText: 'OK',
            confirmButtonColor: '#4c4b9e'
        }).then(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
            modal.hide();
        });
    });

    // "Change price?" dropdown toggles the new-price input.
    document.getElementById('changePrice').addEventListener('change', function () {
        document.getElementById('newPriceSection').style.display = (this.value === 'yes') ? '' : 'none';
    });

    // Save Payment: build the payload and submit the update.
    document.getElementById('save-payment-session-user').addEventListener('click', function () {
        const paymentId        = document.getElementById('hiddenOrderId').value;
        const userId           = document.getElementById('hiddenUserId').value;
        const sessionId        = document.getElementById('hiddenSessionId').value;
        const status           = document.getElementById('hiddenOrderStatus').value;
        const amount           = document.getElementById('amount').value;
        const description      = document.getElementById('description').value;
        const remainingPayment = document.getElementById('remainingPayment').value;
        const newPrice         = document.getElementById('newPrice').value;

                let payload = {};

        if (status === 'Pending' && remainingPayment) {
            // Pending + remaining payment entered -> dedicated payload shape:
            // only remaining_payment / amount_remaining are meaningful,
            // everything else is forced to null/0.
            payload = {
                remaining_payment: 1,
                amount_remaining:  remainingPayment,
                description:       null,
                amount:            0,
                forcing:           0,
                change_price:      0,
                new_price:         null
            };
        } else {
            if (description)                 payload.description = description;
            if (amount && status !== 'Paid') payload.amount = amount;
            if (remainingPayment)            payload.remainingPayment = remainingPayment;

            // For Unpaid orders with an amount entered, always send forcing,
            // change_price and new_price (regardless of whether the Accept
            // Payment section was ever shown to the user).
            if (amount && status === 'Unpaid') {
                const enteredAmount = parseFloat(amount);

                // forcing = 1 when the entered amount is below the session price, 0 when it matches.
                payload.forcing = (enteredAmount < sessionPrice) ? 1 : 0;

                // change_price = 1 if the user explicitly chose "Yes", 0 otherwise (default/"No"/untouched).
                const changePriceValue = document.getElementById('changePrice').value;
                payload.change_price = (changePriceValue === 'yes') ? 1 : 0;

                // new_price = the entered value, or null if left empty.
                payload.new_price = newPrice ? newPrice : null;
            }
        }

        if (Object.keys(payload).length === 0) {
            alert('Please fill in at least one field to update.');
            return;
        }

        updatePayment(paymentId, sessionId, userId, payload)
            .then(res => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
                modal.hide();
                window.location.reload();
            })
            .catch(err => console.error('Error saving payment:', err));
    });

    // Cancel Payment: mark the record as Cancelled with a zeroed amount.
    document.getElementById('cancel-payment').addEventListener('click', function () {
        const paymentId = document.getElementById('hiddenOrderId').value;
        const userId    = document.getElementById('hiddenUserId').value;
        const sessionId = document.getElementById('hiddenSessionId').value;

        const payload = {
            status: 'Cancelled',
            amount: '0'
        };

        updatePayment(paymentId, sessionId, userId, payload)
            .then(res => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
                modal.hide();
                window.location.reload();
            })
            .catch(err => console.error('Error cancelling payment:', err));
    });

    /* ---------------- Status Update Modal ---------------- */

    // Populate the status-update modal with the clicked row's data.
    document.getElementById('statusUpdateModal').addEventListener('show.bs.modal', function (e) {
        const btn = e.relatedTarget;
        if (!btn) return;

        const id          = btn.dataset.id;
        const nextId      = btn.dataset.nextId;
        const currentStat = btn.dataset.currentStatus;
        const nextStat    = btn.dataset.nextStatus;

        document.getElementById('paymentId').value      = id;
        document.getElementById('nextPaymentId').value  = nextId;
        document.getElementById('currentStatus').value  = currentStat;
        document.getElementById('nextStatus').value      = nextStat;

        document.getElementById('statusSelect').value = nextStat;
    });

    document.getElementById('statusUpdateModal').addEventListener('hidden.bs.modal', function () {
        document.getElementById('changeStatusForm').reset();
    });

    document.getElementById('confirmStatusUpdate').addEventListener('click', function () {
        const paymentId = document.getElementById('paymentId').value;
        const newStatus = document.getElementById('statusSelect').value;

        if (!newStatus) {
            alert('Please select a status.');
            return;
        }

        updatePayment(paymentId, idSession, idUser, { status: newStatus })
            .then(res => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('statusUpdateModal'));
                modal.hide();
                window.location.reload();
            })
            .catch(err => console.error('Error updating status:', err));
    });

});