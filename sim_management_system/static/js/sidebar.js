document.addEventListener('DOMContentLoaded', function () {
    const sidebarToggle = document.getElementById('sidebarToggle')
    const sidebar = document.getElementById('sidebar')
    const wrapper = document.getElementById('wrapper')
    const mobileNavToggle = document.getElementById('mobileNavToggle')

    // Check for saved state
    const sidebarState = localStorage.getItem('sidebarState')
    if (sidebarState === 'collapsed') {
        sidebar.classList.add('collapsed')
        wrapper.classList.add('sidebar-collapsed')
        document.getElementById('sidebarToggle').querySelector('i').classList.remove('fa-chevron-left')
        document.getElementById('sidebarToggle').querySelector('i').classList.add('fa-chevron-right')
    }

    // Desktop sidebar toggle
    sidebarToggle.addEventListener('click', function () {
        sidebar.classList.toggle('collapsed')
        wrapper.classList.toggle('sidebar-collapsed')

        // Toggle icon
        if (sidebar.classList.contains('collapsed')) {
            this.querySelector('i').classList.remove('fa-chevron-left')
            this.querySelector('i').classList.add('fa-chevron-right')
            localStorage.setItem('sidebarState', 'collapsed')
        } else {
            this.querySelector('i').classList.remove('fa-chevron-right')
            this.querySelector('i').classList.add('fa-chevron-left')
            localStorage.setItem('sidebarState', 'expanded')
        }
    })

    // Mobile sidebar toggle
    mobileNavToggle.addEventListener('click', function () {
        sidebar.classList.toggle('active')
        this.classList.toggle('active')

        // Toggle icon
        if (sidebar.classList.contains('active')) {
            this.querySelector('i').classList.remove('fa-bars')
            this.querySelector('i').classList.add('fa-times')
        } else {
            this.querySelector('i').classList.remove('fa-times')
            this.querySelector('i').classList.add('fa-bars')
        }
    })

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert')
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.classList.add('fade-out')
            setTimeout(() => {
                alert.remove()
            }, 300)
        }, 5000)
    })
})