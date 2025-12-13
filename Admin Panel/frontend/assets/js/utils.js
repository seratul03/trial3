/**
 * Utility functions for the admin panel
 */

// Toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Show loading spinner
function showLoader(container) {
    const loader = document.createElement('div');
    loader.className = 'flex justify-center items-center p-8';
    loader.innerHTML = '<div class="loader"></div>';
    container.innerHTML = '';
    container.appendChild(loader);
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Format relative time
function formatRelativeTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hours ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return formatDate(dateString);
}

// Check if user is authenticated
function checkAuth() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        window.location.href = '/index.html';
        return false;
    }
    return true;
}

// Get current user from localStorage
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

// Logout function
async function logout() {
    await api.logout();
    localStorage.clear();
    window.location.href = '/index.html';
}

// Confirm dialog
function confirm(message) {
    return window.confirm(message);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Truncate text
function truncate(text, length = 100) {
    if (!text) return '';
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

// Get status badge HTML
function getStatusBadge(status) {
    const badges = {
        'new': '<span class="badge badge-new">New</span>',
        'in_progress': '<span class="badge badge-in-progress">In Progress</span>',
        'resolved': '<span class="badge badge-resolved">Resolved</span>',
        'ignored': '<span class="badge badge-ignored">Ignored</span>'
    };
    return badges[status] || status;
}

// Create pagination HTML
function createPagination(currentPage, totalPages, onPageChange) {
    if (totalPages <= 1) return '';
    
    let html = '<div class="flex justify-center items-center space-x-2 mt-6">';
    
    // Previous button
    if (currentPage > 1) {
        html += `<button onclick="${onPageChange}(${currentPage - 1})" 
                class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                Previous
            </button>`;
    }
    
    // Page numbers
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const activeClass = i === currentPage ? 'bg-blue-600' : 'bg-gray-200 text-gray-700';
        html += `<button onclick="${onPageChange}(${i})" 
                class="px-4 py-2 ${activeClass} text-white rounded hover:bg-blue-600">
                ${i}
            </button>`;
    }
    
    // Next button
    if (currentPage < totalPages) {
        html += `<button onclick="${onPageChange}(${currentPage + 1})" 
                class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                Next
            </button>`;
    }
    
    html += '</div>';
    return html;
}

// Initialize user info in navbar
function initializeNavbar() {
    const user = getCurrentUser();
    if (user) {
        const userNameEl = document.getElementById('userName');
        const userRoleEl = document.getElementById('userRole');
        
        if (userNameEl) userNameEl.textContent = user.name || 'Dr. Shivnath Ghosh';
        if (userRoleEl) userRoleEl.textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
    } else {
        const userNameEl = document.getElementById('userName');
        const userRoleEl = document.getElementById('userRole');
        
        if (userNameEl) userNameEl.textContent = 'Dr. Shivnath Ghosh';
        if (userRoleEl) userRoleEl.textContent = 'Admin';
    }
}

// Validate email
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show modal
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
    }
}

// Hide modal
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Download CSV
function downloadCSV(csvContent, filename) {
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Set active nav link
function setActiveNavLink() {
    const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
    const navLinks = document.querySelectorAll('.sidebar-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage || href === `./${currentPage}`) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Initialize page
function initializePage() {
    if (!checkAuth()) return;
    initializeNavbar();
    setActiveNavLink();
}

// Call on page load
document.addEventListener('DOMContentLoaded', () => {
    initializePage();
});
