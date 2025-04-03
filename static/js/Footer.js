document.querySelector(".btn-primary").addEventListener("click", function () {
    const emailInput = document.querySelector("input[type='email']");
    if (emailInput.value) {
        alert("Subscribed successfully!");
        emailInput.value = "";
    } else {
        alert("Please enter a valid email address.");
    }
});
