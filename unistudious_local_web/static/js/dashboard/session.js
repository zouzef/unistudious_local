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
    document.getElementById('publicResource').addEventListener('change', function () {
        const extraDataWrapper = document.getElementById('extraDataWrapper');
        if (this.value === '1') {
            extraDataWrapper.style.display = 'block';
        } else {
            extraDataWrapper.style.display = 'none';
        }
    });

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

    // Shared function to collect form data (JSON part only — logoFile is sent separately as a real file)
    function collectSessionDataForSubmit() {
        return {
            account_id: accountId,
            name: val('session_name'),
            formation: val('session_formation'),
            capacity: val('session_capacity'),
            typePay: val('session_typePay'),
            numberSessionForPay: val('session_numberSessionForPay'),
            priceStudentAbsent: val('session_priceStudentAbsent'),
            paymentMethode: val('session_paymentMethode'),
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
                    alert('✅ Session created successfully!');
                } else {
                    alert('❌ ' + data.Message);
                }
            })
            .catch(error => {
                console.error('❌ Error:', error);
                alert('❌ Something went wrong, please try again.');
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
                    alert('✅ Session updated successfully!');
                } else {
                    alert('❌ ' + data.Message);
                }
            })
            .catch(error => {
                console.error('❌ Error:', error);
                alert('❌ Something went wrong, please try again.');
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
            document.getElementById('session_name').value     = s.name ?? '';
            document.getElementById('session_status').value   = s.status ?? '';
            document.getElementById('session_capacity').value = s.capacity ?? '';
            document.getElementById('session_description').value = s.description ?? '';

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
                document.getElementById('session_pricePresence').value = s.price_presence ?? '';
                document.getElementById('session_priceOnline').value   = s.price_online ?? '';
            } else {
                document.getElementById('priceTotal').style.display = 'block';
                document.getElementById('priceMixed').style.display = 'none';
                document.getElementById('session_price').value = s.price ?? '';
            }

            // Payment
            document.getElementById('session_typePay').value         = s.type_pay ?? '';
            document.getElementById('session_paymentMethode').value  = s.payment_methode ?? '';
            document.getElementById('session_numberSessionForPay').value = s.number_session_for_pay ?? '';
            document.getElementById('session_priceStudentAbsent').value  = s.price_student_absent ?? '';

            // Show numberSessionForPay section if type is Session
            if (s.type_pay === 'Session') {
                document.getElementById('numberSessionForPay').style.display = 'block';
            } else {
                document.getElementById('numberSessionForPay').style.display = 'none';
            }

            // Currency — show the field and set value
            document.getElementById('currencySession').style.display = 'block';
            document.getElementById('session_currency').value = s.currency ?? '';

            // Dates
            if (s.start_date)
                document.getElementById('session_startDate').value = new Date(s.start_date).toISOString().split('T')[0];
            if (s.end_date)
                document.getElementById('session_endDate').value = new Date(s.end_date).toISOString().split('T')[0];

            // Registration & Groups
            document.getElementById('session_userRegisterAfterStart').value = s.user_register_after_start ?? '';
            document.getElementById('session_requestChangeGroup').value     = s.request_change_group ?? '';
            document.getElementById('session_maxGroupChange').value         = s.max_group_change ?? '';
            document.getElementById('session_specialGroup').value           = s.special_group ?? '';

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
            if (seasonSelect) seasonSelect.value = s.season ?? '';

            // Extra fields
            const publicResource = document.getElementById('publicResource');
            if (publicResource) {
                publicResource.value = s.public_resource ?? '';
                // Show/hide the extra data section to match the loaded value
                document.getElementById('extraDataWrapper').style.display =
                    (String(s.public_resource) === '1') ? 'block' : 'none';
            }

            const extraSession = document.getElementById('session_extraSession');
            if (extraSession) extraSession.value = s.extra_session ?? '';

            // Extra data JSON — populate hidden input, preview, and rebuild modal rows
            const extraDataJsonInput = document.getElementById('extraDataJson');
            const extraDataJsonView = document.getElementById('extraDataJsonView');
            let parsedExtraData = [];

            if (s.extra_data_json) {
                try {
                    parsedExtraData = typeof s.extra_data_json === 'string'
                        ? JSON.parse(s.extra_data_json)
                        : s.extra_data_json;
                } catch (e) {
                    console.warn('❌ Could not parse extra_data_json:', e);
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
            document.getElementById('imagePreview').src = `/api/get_session_img/${s.id}`;

            console.log('✅ Session info loaded:', s);
        })
        .catch(error => console.error('❌ Failed to load session info:', error));
    }
});