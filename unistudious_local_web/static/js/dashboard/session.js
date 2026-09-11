document.addEventListener('DOMContentLoaded', function () {
    const accountId = document.getElementById('account-id').value;

    // Detect page type
    const lastPart = window.location.pathname.split('/').pop();
    const sessionId = parseInt(lastPart);
    const isEditPage = !isNaN(sessionId) && sessionId > 0;

    // Load formations
    const formationsLoaded = fetch(`/api/get-formation-info/${accountId}`)
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('session_formation');
            select.innerHTML = '<option value="" selected>Choose the Formation...</option>';

            if (data.Data && data.Data.length > 0) {
                data.Data.forEach(formation => {
                    const typeLabel = {
                        'M': 'Mixed',
                        'Mixed': 'Mixed',
                        'Presence': 'Presence',
                        'Online': 'Online'
                    }[formation.type_session] || formation.type_session;

                    const option = document.createElement('option');
                    option.value = formation.id;
                    option.setAttribute('data-type', formation.type_session);
                    option.textContent = `${formation.name} (${typeLabel})`;
                    select.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.disabled = true;
                option.textContent = 'No formations available';
                select.appendChild(option);
            }

            return data;
        })
        .catch(error => {
            console.error('❌ Failed to load formations:', error);
            document.getElementById('session_formation').innerHTML = '<option disabled>Failed to load formations</option>';
        });

    // Load locals
    const localsLoaded = fetch(`/api/get-local-info/${accountId}`)
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('multi-value-select');
            select.innerHTML = '';

            if (data.Data && data.Data.length > 0) {
                data.Data.forEach(local => {
                    const option = document.createElement('option');
                    option.value = local.id;
                    option.textContent = local.name;
                    select.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.disabled = true;
                option.textContent = 'No locals available';
                select.appendChild(option);
            }

            return data;
        })
        .catch(error => console.error('❌ Failed to load locals:', error));

    // Show/hide price fields based on formation type
    document.getElementById('session_formation').addEventListener('change', function () {
        const selectedOption = this.options[this.selectedIndex];
        const type = selectedOption.getAttribute('data-type');
        const priceMixed = document.getElementById('priceMixed');
        const priceTotal = document.getElementById('priceTotal');

        if (type === 'M' || type === 'Mixed') {
            priceMixed.style.display = 'block';
            priceTotal.style.display = 'none';
        } else {
            priceMixed.style.display = 'none';
            priceTotal.style.display = 'block';
        }
    });

    // Show/hide number of sessions for payment based on type pay
    document.getElementById('session_typePay').addEventListener('change', function () {
        const numberSessionForPay = document.getElementById('numberSessionForPay');
        if (this.value === 'Session') {
            numberSessionForPay.style.display = 'block';
        } else {
            numberSessionForPay.style.display = 'none';
            document.getElementById('session_numberSessionForPay').value = '';
            document.getElementById('session_priceStudentAbsent').value = '';
        }
    });

    // Show/hide extra data section based on publicResource select
    const publicResourceEl = document.getElementById('publicResource');
    if (publicResourceEl) {
        publicResourceEl.addEventListener('change', function () {
            const extraDataWrapper = document.getElementById('extraDataWrapper');
            if (this.value === '1') {
                extraDataWrapper.style.display = 'block';
            } else {
                extraDataWrapper.style.display = 'none';
            }
        });
    }

    // ---- Add / Remove extra data field rows inside the "Extra Data" modal ----
    let extraDataRowCount = 1; // the static row already in the HTML has data-row-id="1"

    const extraDataContainer = document.getElementById('extraDataContainer');
    const addExtraDataRowBtn = document.getElementById('addExtraDataRow');

    if (addExtraDataRowBtn && extraDataContainer) {
        // Add a new row by cloning the first one
        addExtraDataRowBtn.addEventListener('click', function () {
            extraDataRowCount++;

            const firstRow = extraDataContainer.querySelector('.extra-data-row');
            const newRow = firstRow.cloneNode(true);

            newRow.setAttribute('data-row-id', extraDataRowCount);

            // Reset all values in the cloned row
            newRow.querySelectorAll('input[type="text"]').forEach(input => input.value = '');
            newRow.querySelectorAll('select').forEach(select => select.selectedIndex = 0);
            newRow.querySelectorAll('input[type="checkbox"]').forEach(checkbox => checkbox.checked = false);

            // Give the "Required" checkbox/label a unique id so they don't collide with other rows
            const checkbox = newRow.querySelector('input[type="checkbox"]');
            const label = newRow.querySelector('label.form-check-label');
            if (checkbox && label) {
                const newId = `requiredCheck${extraDataRowCount}`;
                checkbox.id = newId;
                label.setAttribute('for', newId);
            }

            extraDataContainer.appendChild(newRow);
        });

        // Remove a row (event delegation so it also works on dynamically added rows)
        extraDataContainer.addEventListener('click', function (e) {
            if (e.target.classList.contains('removeExtraData')) {
                const row = e.target.closest('.extra-data-row');
                if (row) row.remove();
            }
        });
    }
    // ---- End Add / Remove extra data field rows ----

    // ---- Collect & Save Extra Data (modal "Save Information" button) ----
    const saveExtraDataBtn = document.getElementById('saveExtraData');
    if (saveExtraDataBtn) {
        saveExtraDataBtn.addEventListener('click', function () {
            const rows = extraDataContainer.querySelectorAll('.extra-data-row');
            const extraData = [];

            rows.forEach(row => {
                const nameInput = row.querySelector('input[name="extraDataName[]"]');
                const typeSelect = row.querySelector('select[name="extraDataType[]"]');
                const requiredCheckbox = row.querySelector('input[name="extraDataRequired[]"]');
                const exampleInput = row.querySelector('input[name="extraDataExample[]"]');
                const descriptionInput = row.querySelector('input[name="extraDataDescription[]"]');

                const name = nameInput ? nameInput.value.trim() : '';
                if (!name) return; // skip empty rows

                extraData.push({
                    field_name: name,
                    type: typeSelect ? typeSelect.value : '',
                    required: requiredCheckbox && requiredCheckbox.checked ? 1 : 0,
                    example: exampleInput ? exampleInput.value.trim() : '',
                    description: descriptionInput ? descriptionInput.value.trim() : ''
                });
            });

            // Store as JSON string in the hidden input used by collectSessionDataForSubmit()
            const extraDataJsonInput = document.getElementById('extraDataJson');
            if (extraDataJsonInput) extraDataJsonInput.value = JSON.stringify(extraData);

            // Update the readonly preview shown to the user
            const extraDataJsonView = document.getElementById('extraDataJsonView');
            if (extraDataJsonView) {
                extraDataJsonView.value = extraData.length
                    ? `${extraData.length} field(s) added`
                    : '';
            }

            // Close the modal
            const modalEl = document.getElementById('extraDataModal');
            const modalInstance = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            modalInstance.hide();
        });
    }
    // ---- End Collect & Save Extra Data ----

    // Shared val() helper
    const val = (id) => {
        const el = document.getElementById(id);
        if (!el) { console.warn(`❌ Element not found: ${id}`); return ''; }
        return el.value;
    };

    // Shared setVal() helper — mirror of val(), but for WRITING values safely.
    // Prevents "Cannot set properties of null" crashes when a field doesn't
    // exist on a given page's HTML (e.g. payment_deadline missing on view-session.html).
    const setVal = (id, value) => {
        const el = document.getElementById(id);
        if (!el) { console.warn(`❌ Element not found (setVal): ${id}`); return; }
        el.value = value ?? '';
    };

    // Shared function to collect form data (JSON part only — logoFile is sent separately as a real file)
    function collectSessionDataForSubmit() {
    return {
        account_id: accountId,
        name: val('session_name'),
        status: val('session_status'),
        formation: val('session_formation'),
        capacity: val('session_capacity'),
        typePay: val('session_typePay'),
        numberSessionForPay: val('session_numberSessionForPay'),
        priceStudentAbsent: val('session_priceStudentAbsent'),
        paymentMethode: val('session_paymentMethode'),
        paymentDeadline: val('payment_deadline'),
        price: val('session_price'),
        pricePresence: val('session_pricePresence'),
        priceOnline: val('session_priceOnline'),
        currency: val('session_currency'),
        userRegisterAfterStart: val('session_userRegisterAfterStart'),
        startDate: val('session_startDate'),
        endDate: val('session_endDate'),
        season: val('season_select'),
        locals: Array.from(document.getElementById('multi-value-select').selectedOptions).map(o => ({
            value: o.value,
            label: o.text
        })),
        requestChangeGroup: val('session_requestChangeGroup'),
        maxGroupChange: val('session_maxGroupChange'),
        specialGroup: val('session_specialGroup'),
        publicResource: val('publicResource'),
        extraSession: val('session_extraSession'),
        extraDataJson: val('extraDataJson'),
        description: val('session_description'),
    };
}

    // Shared helper: build a FormData payload (JSON blob + real image file)
    function buildSessionFormData() {
        const sessionData = collectSessionDataForSubmit();
        console.log('📋 Session Data:', sessionData);

        const formData = new FormData();
        formData.append('data', JSON.stringify(sessionData));

        const fileInput = document.getElementById('session_logoFile');
        if (fileInput && fileInput.files[0]) {
            formData.append('logoFile', fileInput.files[0]);
        }

        return formData;
    }

    // CREATE button (create page only)
    const createBtn = document.getElementById('create_session');
    if (createBtn) {
        createBtn.addEventListener('click', function (e) {
            e.preventDefault();

            const formData = buildSessionFormData();

            fetch('/api/create-session', {
                method: 'POST',
                body: formData
                // No headers set — browser sets multipart/form-data + boundary automatically
            })
            .then(response => response.json())
            .then(data => {
                console.log('✅ Response:', data);
                if (data.Message === 'Session created with success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success!',
                        text: 'Session created with success',
                        confirmButtonColor: '#4c4b9e'
                    }).then(() => {
                        window.location.href = 'https://172.28.20.156:5016/dashboard/show-session';
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.Message,
                        confirmButtonColor: '#4c4b9e'
                    });
                }
            })
            .catch(error => {
                console.error('❌ Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Something went wrong, please try again.',
                    confirmButtonColor: '#4c4b9e'
                });
            });
        });
    }

    // UPDATE button (edit page only)
    const updateBtn = document.getElementById('update_session');
    if (updateBtn) {
        updateBtn.addEventListener('click', function (e) {
            e.preventDefault();

            const formData = buildSessionFormData();

            fetch(`/api/update-session/${sessionId}`, {
                method: 'POST',
                body: formData
                // No headers set — browser sets multipart/form-data + boundary automatically
            })
            .then(response => response.json())
            .then(data => {
                console.log('✅ Response:', data);
                if (data.Message === 'Session updated with success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success!',
                        text: 'Session updated with success',
                        confirmButtonColor: '#4c4b9e'
                    }).then(() => {
                        window.location.href = 'https://172.28.20.156:5016/dashboard/show-session';
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.Message,
                        confirmButtonColor: '#4c4b9e'
                    });
                }
            })
            .catch(error => {
                console.error('❌ Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Something went wrong, please try again.',
                    confirmButtonColor: '#4c4b9e'
                });
            });
        });
    }

    // Populate form on edit page
    if (isEditPage) {
        Promise.all([
            formationsLoaded,
            localsLoaded,
            fetch(`/api/get-session-info/${sessionId}`).then(r => r.json())
        ])
        .then(([_formations, _locals, sessionData]) => {
            if (!sessionData || !sessionData.length) return;
            const s = sessionData[0];

            // Basic Info
            setVal('session_name', s.name);
            setVal('session_status', s.status);
            setVal('session_capacity', s.capacity);
            setVal('session_description', s.description);

            // Formation
            const formationSelect = document.getElementById('session_formation');
            formationSelect.value = s.formation_id ?? '';

            // Get the data-type of the selected formation option
            const selectedOption = formationSelect.options[formationSelect.selectedIndex];
            const formationType = selectedOption ? selectedOption.getAttribute('data-type') : null;

            console.log('🏗️ Formation type:', formationType);

            // Manually show/hide price sections based on formation type
            if (formationType === 'M' || formationType === 'Mixed') {
                document.getElementById('priceMixed').style.display = 'block';
                document.getElementById('priceTotal').style.display = 'none';
                setVal('session_pricePresence', s.price_presence);
                setVal('session_priceOnline', s.price_online);
            } else {
                document.getElementById('priceTotal').style.display = 'block';
                document.getElementById('priceMixed').style.display = 'none';
                setVal('session_price', s.price);
            }

            // Payment
            setVal('session_typePay', s.type_pay);
            setVal('session_paymentMethode', s.payment_methode);
            setVal('session_numberSessionForPay', s.number_session_for_pay);
            setVal('session_priceStudentAbsent', s.price_student_absent);
            setVal('payment_deadline', s.payment_deadline);

            // Show numberSessionForPay section if type is Session
            const numberSessionForPayEl = document.getElementById('numberSessionForPay');
            if (numberSessionForPayEl) {
                numberSessionForPayEl.style.display = (s.type_pay === 'Session') ? 'block' : 'none';
            }

            // Currency — show the field and set value
            const currencySessionEl = document.getElementById('currencySession');
            if (currencySessionEl) currencySessionEl.style.display = 'block';
            setVal('session_currency', s.currency);

            // Dates
            if (s.start_date)
                setVal('session_startDate', new Date(s.start_date).toISOString().split('T')[0]);
            if (s.end_date)
                setVal('session_endDate', new Date(s.end_date).toISOString().split('T')[0]);

            // Registration & Groups
            setVal('session_userRegisterAfterStart', s.user_register_after_start);
            setVal('session_requestChangeGroup', s.request_change_group);
            setVal('session_maxGroupChange', s.max_group_change);
            setVal('session_specialGroup', s.special_group);

            // Locals — pre-select matching options
            if (s.locals && Array.isArray(s.locals)) {
                const localIds = s.locals.map(l => String(l.id ?? l.value));
                const select = document.getElementById('multi-value-select');
                Array.from(select.options).forEach(opt => {
                    opt.selected = localIds.includes(opt.value);
                });
            }

            // Season
            const seasonSelect = document.getElementById('season_select');
            if (seasonSelect) seasonSelect.value = s.season_id ?? s.season ?? '';

            // Extra fields
            const publicResource = document.getElementById('publicResource');
            if (publicResource) {
                publicResource.value = s.public_resource ?? '';
                // Show/hide the extra data section to match the loaded value
                const extraDataWrapperEl = document.getElementById('extraDataWrapper');
                if (extraDataWrapperEl) {
                    extraDataWrapperEl.style.display =
                        (String(s.public_resource) === '1') ? 'block' : 'none';
                }
            }

            const extraSession = document.getElementById('session_extraSession');
            if (extraSession) extraSession.value = s.extra_session ?? '';

            // Extra data — API returns it under "extra_data" (can be null,
            // a JSON string, or an already-parsed array depending on the endpoint)
            const extraDataJsonInput = document.getElementById('extraDataJson');
            const extraDataJsonView = document.getElementById('extraDataJsonView');
            let parsedExtraData = [];

            const rawExtraData = s.extra_data ?? s.extra_data_json;
            if (rawExtraData) {
                try {
                    parsedExtraData = typeof rawExtraData === 'string'
                        ? JSON.parse(rawExtraData)
                        : rawExtraData;
                } catch (e) {
                    console.warn('❌ Could not parse extra_data:', e);
                    parsedExtraData = [];
                }
            }

            if (extraDataJsonInput) extraDataJsonInput.value = JSON.stringify(parsedExtraData);
            if (extraDataJsonView) {
                extraDataJsonView.value = parsedExtraData.length
                    ? `${parsedExtraData.length} field(s) added`
                    : '';
            }

            // Rebuild the modal rows so the user can edit existing extra data
            if (extraDataContainer && parsedExtraData.length > 0) {
                extraDataContainer.innerHTML = '';
                extraDataRowCount = 0;

                parsedExtraData.forEach(field => {
                    extraDataRowCount++;

                    const row = document.createElement('div');
                    row.className = 'extra-data-row mb-3';
                    row.setAttribute('data-row-id', extraDataRowCount);

                    const checkboxId = `requiredCheck${extraDataRowCount}`;

                    row.innerHTML = `
                        <input type="text" class="form-control mb-2" placeholder="Field Name" name="extraDataName[]" value="${field.field_name ?? ''}">
                        <select class="form-control mb-2 extraDataSessionSelect" name="extraDataType[]">
                            <option value="string">Text</option>
                            <option value="integer">Number</option>
                            <option value="float">Decimal Number</option>
                            <option value="image">Photo</option>
                            <option value="file">File Upload</option>
                            <option value="date">Date</option>
                            <option value="Boolean">Yes / No</option>
                            <option value="Link">Link</option>
                        </select>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" name="extraDataRequired[]" id="${checkboxId}" ${field.required ? 'checked' : ''}>
                            <label class="form-check-label" for="${checkboxId}">Required</label>
                        </div>
                        <input type="text" class="form-control mb-2" placeholder="Example value" name="extraDataExample[]" value="${field.example ?? ''}">
                        <input type="text" class="form-control mb-2" placeholder="Description (optional)" name="extraDataDescription[]" value="${field.description ?? ''}">
                        <button type="button" class="btn btn-danger btn-sm removeExtraData">Remove</button>
                        <hr>
                    `;

                    const typeSelect = row.querySelector('select[name="extraDataType[]"]');
                    if (typeSelect && field.type) typeSelect.value = field.type;

                    extraDataContainer.appendChild(row);
                });
            }

            // Image preview
            const imagePreviewEl = document.getElementById('imagePreview');
            if (imagePreviewEl) imagePreviewEl.src = `/api/get_session_img/${s.id}`;

            console.log('✅ Session info loaded:', s);
        })
        .catch(error => console.error('❌ Failed to load session info:', error));
    }
});