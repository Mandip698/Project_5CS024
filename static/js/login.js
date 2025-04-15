// Toggle password visibility
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.querySelector('.toggle-password');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.textContent = 'Hide'; // Change icon to indicate password is visible
    } else {
        passwordInput.type = 'password';
        toggleIcon.textContent = 'show'; // Change icon back to indicate password is hidden
    }
}

// Form submission alert (for demo purposes)
document.querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Login functionality would be implemented here!');
});