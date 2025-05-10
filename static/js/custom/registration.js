document.addEventListener("DOMContentLoaded", function () {
    // === Elements ===
    const form = document.getElementById("voterForm");

    const userPhotoInput = document.getElementById("userPhotoUpload");
    const voterCardInput = document.getElementById("voterCardUpload");

    const userPhotoPreview = document.getElementById("userPhotoPreview");
    const voterCardPreview = document.getElementById("voterCardPreview");

    const photoDropAreas = document.querySelectorAll("#drop-area");
    const clickToBrowseLinks = document.querySelectorAll("#clickToBrowse");

    // === Constants ===
    const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2MB

    // === Utility Functions ===
    function isEmailValid(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    function showImagePreview(fileInput, previewImg) {
        const file = fileInput.files[0];
        if (!file) return;

        if (!file.type.startsWith("image/")) {
            toastr.error("Please upload a valid image.");
            fileInput.value = "";
            return;
        }

        if (file.size > MAX_FILE_SIZE) {
            toastr.error("File size should be less than 2MB.");
            fileInput.value = "";
            return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            previewImg.src = e.target.result;
            previewImg.style.display = "block";
        };
        reader.readAsDataURL(file);
    }

    // === Event Listeners for Click to Browse ===
    clickToBrowseLinks[0].addEventListener("click", () => userPhotoInput.click());
    clickToBrowseLinks[1].addEventListener("click", () => voterCardInput.click());

    // === Image Previews ===
    userPhotoInput.addEventListener("change", () => showImagePreview(userPhotoInput, userPhotoPreview));
    voterCardInput.addEventListener("change", () => showImagePreview(voterCardInput, voterCardPreview));

    // === Drag and Drop ===
    photoDropAreas.forEach((area, index) => {
        const input = index === 0 ? userPhotoInput : voterCardInput;
        const preview = index === 0 ? userPhotoPreview : voterCardPreview;

        area.addEventListener("dragover", (e) => {
            e.preventDefault();
            area.classList.add("border-primary");
        });

        area.addEventListener("dragleave", () => {
            area.classList.remove("border-primary");
        });

        area.addEventListener("drop", (e) => {
            e.preventDefault();
            area.classList.remove("border-primary");

            const file = e.dataTransfer.files[0];
            if (file) {
                input.files = e.dataTransfer.files;
                showImagePreview(input, preview);
            }
        });
    });

    // === Form Validation ===
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        // Clear previous error messages
        const errorElements = form.querySelectorAll(".error-message");
        errorElements.forEach((el) => (el.textContent = ""));
        const inputs = form.querySelectorAll("input");
        inputs.forEach((input) => input.classList.remove("is-invalid"));

        const firstName = document.getElementById("firstName");
        const middleName = document.getElementById("middleName");
        const lastName = document.getElementById("lastName");
        const username = document.getElementById("username");
        const email = document.getElementById("email");
        const dob = document.getElementById("dob");

        let isValid = true;

        function showError(input, message) {
            const errorSpan = input.parentElement.querySelector(".error-message");
            if (errorSpan) {
                errorSpan.textContent = message;
                input.classList.add("is-invalid");
                isValid = false;
            }
        }

        if (!firstName.value.trim()) showError(firstName, "First name is required.");
        if (!lastName.value.trim()) showError(lastName, "Last name is required.");
        if (!username.value.trim() || username.value.trim().length < 3)
            showError(username, "Username must be at least 3 characters.");
        if (!email.value.trim() || !isEmailValid(email.value.trim()))
            showError(email, "A valid email is required.");
        if (!dob.value.trim()) {
            showError(dob, "Date of Birth is required.");
        } else {
            const birthDate = new Date(dob.value);
            if (isNaN(birthDate.getTime())) {
                showError(dob, "Please enter a valid date.");
            } else {
                const today = new Date();
                const age = today.getFullYear() - birthDate.getFullYear();
                const monthDiff = today.getMonth() - birthDate.getMonth();
                const dayDiff = today.getDate() - birthDate.getDate();
                const isBirthdayPassedThisYear = monthDiff > 0 || (monthDiff === 0 && dayDiff >= 0);
                const realAge = isBirthdayPassedThisYear ? age : age - 1;
                if (realAge < 18) {
                    showError(dob, "You must be at least 18 years old to register.");
                }
            }
        }

        if (!userPhotoInput.files.length) showError(userPhotoInput, "User photo is required.");
        if (!voterCardInput.files.length) showError(voterCardInput, "Voter card image is required.");

        if (!isValid) return;

        const spinnerOverlay = document.getElementById("spinnerOverlay");
        spinnerOverlay.style.display = "block";

        const formData = new FormData();
        formData.append("csrfmiddlewaretoken", document.querySelector("[name=csrfmiddlewaretoken]").value);
        formData.append("firstName", firstName.value.trim());
        formData.append("middleName", middleName.value.trim());
        formData.append("lastName", lastName.value.trim());
        formData.append("username", username.value.trim());
        formData.append("email", email.value.trim());
        formData.append("dob", dob.value.trim());
        formData.append("userPhotoUpload", userPhotoInput.files[0]);
        formData.append("voterCardUpload", voterCardInput.files[0]);

        fetch("/registration/", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === "success") {
                    toastr.success(data.message);
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 2000); // Delay to show toast
                } else {
                    toastr.error(data.message || "An error occurred.");
                }
            })
            .catch((error) => {
                toastr.error("Something went wrong.");
                console.error("Error:", error);
            })
            .finally(() => {
                spinnerOverlay.style.display = "none";
            });
    });
});
