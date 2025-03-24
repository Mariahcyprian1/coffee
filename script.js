// script.js
document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let username = document.getElementById("username").value.trim();
    let password = document.getElementById("password").value.trim();
    let isValid = true;

    // Username validation
    if (username === "") {
        document.getElementById("usernameError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("usernameError").style.display = "none";
    }

    // Password validation
    if (password === "") {
        document.getElementById("passwordError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("passwordError").style.display = "none";
    }

    // If valid, proceed with login (dummy authentication)
    if (isValid) {
        if (username === "admin" && password === "123") {
            alert("Login successful!");
            // Redirect or proceed further
        } else {
            alert("Invalid credentials! Try again.");
        }
    }
});
