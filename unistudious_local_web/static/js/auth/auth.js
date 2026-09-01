function showOfflineNotice() {
    Swal.fire({
        icon: 'info',
        title: 'Not Available Offline',
        text: 'This action is only available on the online website, not on this local platform.',
        confirmButtonColor: '#4c4b9e'
    });
}

function login(){
    username = document.getElementById("username").value;
    password = document.getElementById("password").value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            window.location.href = data.redirect;
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Login Failed',
                text: data.message,
                confirmButtonColor: '#4c4b9e'
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'An error occurred. Please try again.',
            confirmButtonColor: '#4c4b9e'
        });
    });
}