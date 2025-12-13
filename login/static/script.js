const form = document.getElementById("loginForm");
const button = document.querySelector(".btn");

if (form && button) {
    form.addEventListener("submit", (e) => {
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        // Simple front-end check
        if (!email || !password) {
            e.preventDefault();
            showInlineToast("Please fill in both fields.");
            return;
        }

        // Show loading animation on button
        button.classList.add("loading");
    });
}

function showInlineToast(message) {
    let toast = document.querySelector(".toast-inline");

    if (!toast) {
        toast = document.createElement("div");
        toast.className = "toast toast-inline";
        document.querySelector(".login-container").prepend(toast);
    }

    toast.textContent = message;

    setTimeout(() => {
        toast.remove();
    }, 2500);
}
