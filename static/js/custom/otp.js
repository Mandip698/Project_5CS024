document.getElementById("otpForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    const spinnerOverlay = document.getElementById("spinnerOverlay");
    spinnerOverlay.style.display = "block";

    fetch("/verify-otp/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: formData,
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                setTimeout(() => {
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    }
                }, 2500);
            } else {
                toastr.error(data.error);
            }
        })
        .catch((err) => {
            toastr.error("OTP Verification Error", err);
        })
        .finally(() => {
            spinnerOverlay.style.display = "none";
        });
});

document.getElementById("resendBtn").addEventListener("click", function () {
    const spinnerOverlay = document.getElementById("spinnerOverlay");
    spinnerOverlay.style.display = "block";

    fetch("/resend-otp/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ resend: true }) // dummy payload
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                toastr.success("OTP resent successfully.");
            } else {
                toastr.error(data.error || "Failed to resend OTP.");
            }
        })
        .catch((err) => {
            toastr.error("Network error during resend OTP.");
        })
        .finally(() => {
            spinnerOverlay.style.display = "none";
        });
});

