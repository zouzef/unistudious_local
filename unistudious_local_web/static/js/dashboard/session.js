document.addEventListener('DOMContentLoaded', function () {
    const accountId = document.getElementById('account-id').value;
    // Load formations
    fetch(`/api/get-formation-info/${accountId}`)
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
        })
        .catch(error => {
            console.error('❌ Failed to load formations:', error);
            document.getElementById('session_formation').innerHTML = '<option disabled>Failed to load formations</option>';
        });

    // Load locals
    fetch(`/api/get-local-info/${accountId}`)
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

    // Create session
    document.getElementById('create_session').addEventListener('click', function (e) {
        e.preventDefault();

        const val = (id) => {
            const el = document.getElementById(id);
            if (!el) { console.warn(`❌ Element not found: ${id}`); return ''; }
            return el.value;
        };

        const sessionData = {
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
    publicResource: val('session_publicResource'),
    extraSession: val('session_extraSession'),
    extraDataJson: val('extraDataJson'),
    description: val('session_description'),
    logoFile: document.getElementById('session_logoFile').files[0]
        ? document.getElementById('session_logoFile').files[0].name
        : null,
};

        console.log('📋 Session Data:', sessionData);

        fetch('/api/create-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(sessionData)
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

});

