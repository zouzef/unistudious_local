function login(){
    username = document.getElementById("username").value;
    password = document.getElementById("password").value;

    // Send POST request to Flask
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
            // Login successful - redirect to dashboard
            window.location.href = data.redirect;
        } else {
            // Login failed - show error message
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}