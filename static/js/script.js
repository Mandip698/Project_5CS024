$(function () {
    $("#table").bootstrapTable();
});

function togglePassword() {
    const passwordInput = document.getElementById("password");
    const toggleIcon = document.querySelector(".toggle-password");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        toggleIcon.textContent = "Hide";
    } else {
        passwordInput.type = "password";
        toggleIcon.textContent = "show";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const modalEl = document.getElementById("otpModal");
    if (modalEl) {
        var otpModal = new bootstrap.Modal(modalEl, {
            keyboard: false,
        });
        otpModal.show();
    } else {
        console.warn("OTP modal not found in the DOM.");
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const resendBtn = document.getElementById("resendBtn");
    if (resendBtn) {
        resendBtn.addEventListener("click", function () {
            fetch("{% url 'resend_otp' %}")
                .then((response) => response.json())
                .then((data) => {
                    const statusEl = document.getElementById("resendStatus");
                    if (data.message) {
                        statusEl.innerText = data.message;
                        statusEl.classList.remove("text-danger");
                        statusEl.classList.add("text-success");
                    } else {
                        statusEl.innerText = data.error || "Something went wrong.";
                        statusEl.classList.remove("text-success");
                        statusEl.classList.add("text-danger");
                    }
                })
                .catch(() => {
                    document.getElementById("resendStatus").innerText = "Network error.";
                });
        });
    }
});

// document.getElementById("otpForm").addEventListener("submit", function (event) {
//     event.preventDefault();
//     const otp = document.getElementById("otp").value;
//     const uid = "{{ uid }}"; // This should be dynamically passed from your view
//     const token = "{{ token }}"; // This too

//     fetch("{% url 'verify_otp' %}", {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json",
//             "X-CSRFToken": getCookie("csrftoken"), // Handle CSRF token
//         },
//         body: JSON.stringify({ uid, token, otp }),
//     })
//         .then((response) => response.json())
//         .then((data) => {
//             if (data.error) {
//                 alert(data.error); // Handle error response
//             } else {
//                 window.location.href = "{% url 'dashboard' %}"; // Redirect on success
//             }
//         })
//         .catch((error) => console.error("Error:", error));
// });

// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== "") {
//         const cookies = document.cookie.split(";");
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === name + "=") {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }
