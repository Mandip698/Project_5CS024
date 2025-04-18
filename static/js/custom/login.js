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
    const form = document.getElementById("loginForm");
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const spinnerOverlay = document.getElementById("spinnerOverlay");
        spinnerOverlay.style.display = "block";

        fetch("/login_view/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    if (data.show_otp_modal) {
                        const modalEl = document.getElementById("otpModal");
                        if (modalEl) {
                            var otpModal = new bootstrap.Modal(modalEl, {
                                keyboard: false,
                            });
                            otpModal.show();
                            const uidInput = modalEl.querySelector("input[name='uid']");
                            const tokenInput = modalEl.querySelector("input[name='token']");
                            uidInput.value = data.uid;
                            tokenInput.value = data.token;
                        }
                        toastr.success("OTP sent to your email. Please check.");
                    }
                } else {
                    toastr.error(data.error);
                }
            })
            .catch((error) => {
                toastr.error("Error:", error);
            })
            .finally(() => {
                spinnerOverlay.style.display = "none";
            });
    });
});
