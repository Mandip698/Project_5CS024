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
        },
        body: new FormData(), // even if empty, still mimics a real form POST
    })
        .then((res) => {
            if (!res.ok) {
                throw new Error("Network response was not ok");
            }
            return res.text();
        })
        .then((html) => {
            toastr.success("OTP resent successfully.");
        })
        .catch((err) => {
            toastr.error("Resend OTP failed.", err.message);
        })
        .finally(() => {
            spinnerOverlay.style.display = "none";
        });
});
