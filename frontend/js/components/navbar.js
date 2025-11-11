/**
 * Navbar Component JavaScript
 * Xử lý các tương tác của navbar
 */

document.addEventListener('DOMContentLoaded', function() {
    initNavbarComponent();
});

/**
 * Initialize navbar component
 */
function initNavbarComponent() {
    // Mobile sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }
    
    // Active nav item
    highlightActiveNavItem();
}

/**
 * Highlight active navigation item based on current page
 */
function highlightActiveNavItem() {
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href)) {
            item.classList.add('active');
        }
    });
}