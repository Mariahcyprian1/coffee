document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent default form submission

    // Get input values
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    // Hardcoded credentials (In real projects, use a database)
    const correctUsername = "admin";
    const correctPassword = "123";

    if (username === correctUsername && password === correctPassword) {
        // Save login status in sessionStorage
        sessionStorage.setItem("loggedIn", "true");

        // Redirect to dashboard
        window.location.href = "dashboard.html";
    } else {
        alert("Invalid username or password. Please try again.");
    }
});
