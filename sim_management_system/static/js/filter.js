document.addEventListener('DOMContentLoaded', function () {
    // Auto-submit form on filter change for better UX
    const filterSelects = document.querySelectorAll('#filterStatus, #filterType');
    filterSelects.forEach(select => {
        select.addEventListener('change', function () {
            // Optional: Auto-submit form when filters change
            // this.form.submit();
        });
    });

    // Enhanced search with debouncing
    const searchInput = document.getElementById('searchQuery');
    let searchTimeout;

    searchInput.addEventListener('input', function () {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            // Optional: Auto-submit search after typing stops
            // this.form.submit();
        }, 500);
    });

    // Add loading state to buttons
    const submitBtn = document.querySelector('.btn-primary');
    const form = document.querySelector('.filter-bar');

    form.addEventListener('submit', function () {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Applying...';
        submitBtn.disabled = true;
    });

    // Smooth scroll to results
    if (window.location.search) {
        const firstDepartment = document.querySelector('.department-container');
        if (firstDepartment) {
            firstDepartment.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
});