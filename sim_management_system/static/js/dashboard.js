// Toggle user dropdown menu
document.getElementById('userMenu').addEventListener('click', function () {
    document.getElementById('userDropdown').classList.toggle('active');
});

// Close dropdown when clicking outside
document.addEventListener('click', function (event) {
    if (!event.target.closest('.user-profile')) {
        document.getElementById('userDropdown').classList.remove('active');
    }
});

// Function to show alerts
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = 'alert';

    if (type === 'error') alert.classList.add('alert-error');
    if (type === 'warning') alert.classList.add('alert-warning');
    if (type === 'info') alert.classList.add('alert-info');

    document.addEventListener('DOMContentLoaded', function () {
        // Toggle sidebar on mobile
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');

        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('active');
                mainContent.classList.toggle('active');
            });
        }

        // User profile dropdown
        const userMenu = document.getElementById('userMenu');
        const userDropdown = document.getElementById('userDropdown');

        if (userMenu) {
            userMenu.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('show');
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            if (userDropdown) {
                userDropdown.classList.remove('show');
            }
        });
    }); alert.innerHTML = message;
    alertContainer.appendChild(alert);
    alertContainer.style.display = 'block';

    setTimeout(() => {
        alert.remove();
        if (alertContainer.children.length === 0) {
            alertContainer.style.display = 'none';
        }
    }, 5000);
}