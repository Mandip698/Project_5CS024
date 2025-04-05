// Function to load HTML content into a specific div
function loadHTML(filename, elementId) {
    fetch(filename)
        .then(response => response.text())
        .then(data => {
            document.getElementById(elementId).innerHTML = data;
        })
        .catch(error => {
            console.error('Error loading the file:', error);
        });
}

// Load NavBar, Hero Section, Features, and How It Works once the page content is loaded
document.addEventListener('DOMContentLoaded', function() {
    loadHTML('NavBar.html', 'navbar-container');
    loadHTML('Sidebar.html', 'sidebar-container');
    loadHTML('DashboardBody.html', 'dashboard-container');
    loadHTML('Footer.html', 'footer-container');
    });
