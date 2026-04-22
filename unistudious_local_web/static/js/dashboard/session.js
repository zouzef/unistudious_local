document.getElementById('create_session').addEventListener('click', function (e) {
    e.preventDefault();

    const sessionData = {
        name: document.getElementById('session_name').value,
        formation: document.getElementById('session_formation').value,
        capacity: document.getElementById('session_capacity').value,
        typePay: document.getElementById('session_typePay').value,
        numberSessionForPay: document.getElementById('session_numberSessionForPay').value,
        priceStudentAbsent: document.getElementById('session_priceStudentAbsent').value,
        paymentMethode: document.getElementById('session_paymentMethode').value,
        price: document.getElementById('session_price').value,
        pricePresence: document.getElementById('session_pricePresence').value,
        priceOnline: document.getElementById('session_priceOnline').value,
        currency: document.getElementById('session_currency').value,
        userRegisterAfterStart: document.getElementById('session_userRegisterAfterStart').value,
        startDate: document.getElementById('session_startDate').value,
        endDate: document.getElementById('session_endDate').value,
        season: document.getElementById('season_select').value,
        locals: Array.from(document.getElementById('multi-value-select').selectedOptions).map(o => ({
            value: o.value,
            label: o.text
        })),
        requestChangeGroup: document.getElementById('session_requestChangeGroup').value,
        maxGroupChange: document.getElementById('session_maxGroupChange').value,
        specialGroup: document.getElementById('session_specialGroup').value,
        publicResource: document.getElementById('session_publicResource').value,
        extraSession: document.getElementById('session_extraSession').value,
        extraDataJson: document.getElementById('extraDataJson').value,
        description: document.getElementById('session_description').value,
        logoFile: document.getElementById('session_logoFile').files[0]
            ? document.getElementById('session_logoFile').files[0].name
            : null,
    };

    console.log('📋 Session Data:', sessionData);

    fetch('/api/create-session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Response:', data);
        if (data.Message === 'Session created with success') {
            alert('✅ Session created successfully!');
            // window.location.href = '/dashboard/show-session'; // uncomment to redirect
        } else {
            alert('❌ ' + data.Message);
        }
    })
    .catch(error => {
        console.error('❌ Error:', error);
        alert('❌ Something went wrong, please try again.');
    });
});