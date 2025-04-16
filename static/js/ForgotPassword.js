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
  