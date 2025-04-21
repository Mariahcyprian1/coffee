document.addEventListener("DOMContentLoaded", function() {
    // Login form handling
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", function(event) {
            event.preventDefault();
            
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();
            let isValid = true;

            // Validation
            document.getElementById("usernameError").style.display = username ? "none" : "block";
            document.getElementById("passwordError").style.display = password ? "none" : "block";
            
            if (!username || !password) {
                isValid = false;
            }

            if (isValid) {
                fetch("/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
                })
                .then(response => {
                    if (response.redirected) {
                        window.location.href = response.url;
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                });
            }
        });
    }

    // Menu form handling
    const addCoffeeForm = document.querySelector(".add-coffee-form form");
    if (addCoffeeForm) {
        addCoffeeForm.addEventListener("submit", function(event) {
            const price = parseFloat(this.elements["price"].value);
            const quantity = parseInt(this.elements["quantity"].value);
            
            if (price <= 0 || quantity <= 0) {
                event.preventDefault();
                alert("Price and quantity must be positive numbers");
            }
        });
    }
});