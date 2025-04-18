document.getElementById("resetForm").addEventListener("submit", function (e) {
    e.preventDefault();
    const email = document.getElementById("email1").value;

    const spinnerOverlay = document.getElementById("spinnerOverlay");
    spinnerOverlay.style.display = "block";

    fetch("/forgot-password/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        },
        body: JSON.stringify({ email }),
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                toastr.success("OTP sent to your email. Please check.");
                const forgotModalEl = document.getElementById("forgotModal");
                if (forgotModalEl) {
                    var forgotModal = bootstrap.Modal.getInstance(forgotModalEl);
                    forgotModal.hide();
                }
                const modalEl = document.getElementById("forgotOtpModal");
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
            } else {
                toastr.error(data.error);
            }
        })
        .finally(() => {
            spinnerOverlay.style.display = "none";
        });
});
