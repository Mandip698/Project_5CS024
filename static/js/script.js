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
			const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
			fetch("/resend-otp/", {
				method: "GET",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrftoken,
				},
			})
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

document.querySelectorAll("tr[data-url]").forEach((row) => {
	row.style.cursor = "pointer";
	row.addEventListener("click", () => {
		window.location.href = row.dataset.url;
	});
});

document.getElementById("resetForm").addEventListener("submit", function (e) {
	e.preventDefault();
	const email = document.getElementById("email").value.trim();

	if (email) {
		alert(`Password reset link sent to ${email}`);
		// Here you could add an actual API call if needed
	} else {
		alert("Please enter a valid email address.");
	}
});


function submitVote() {
	const selectedOption = document.querySelector('input[name="pollOption"]:checked');
	if (selectedOption) {
		alert(`You voted for: ${selectedOption.value}`);
	} else {
		alert("Please select an option to vote.");
	}
}

function showResults() {
	alert("Displaying poll results... (this can be replaced with real results UI)");
}

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
