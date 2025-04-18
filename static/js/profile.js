document.addEventListener("DOMContentLoaded", () => {
    const profileNameEl = document.getElementById("profileName");
    const profileEmailEl = document.getElementById("profileEmail");
    const nameInput = document.getElementById("nameInput");
    const emailInput = document.getElementById("emailInput");
    const saveProfileBtn = document.getElementById("saveProfileBtn");
  
    // Initialize input fields with current profile values
    nameInput.value = profileNameEl.textContent;
    emailInput.value = profileEmailEl.textContent;
  
    // Update profile info on button click
    saveProfileBtn.addEventListener("click", () => {
      const newName = nameInput.value.trim();
      const newEmail = emailInput.value.trim();
  
      if (newName && newEmail) {
        profileNameEl.textContent = newName;
        profileEmailEl.textContent = newEmail;
        alert("Profile updated successfully!");
      } else {
        alert("Please enter both name and email.");
      }
    });
  });