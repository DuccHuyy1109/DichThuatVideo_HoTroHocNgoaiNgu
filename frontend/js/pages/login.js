/**
 * Login Page JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // XÓA localStorage cũ để tránh autofill bug
    Storage.logout();
    
    // Kiểm tra đã đăng nhập chưa
    checkAuthAndRedirect();
    initLoginForm();
});

/**
 * Kiểm tra auth và redirect nếu đã đăng nhập
 */
async function checkAuthAndRedirect() {
    const token = Storage.getToken();
    
    if (token) {
        // Verify token với server
        const result = await AuthAPI.verifyToken();
        
        if (result.success) {
            // Token hợp lệ, redirect
            window.location.href = '../dashboard/index.html';
        } else {
            // Token không hợp lệ, xóa và cho phép login
            Storage.logout();
        }
    }
}

/**
 * Khởi tạo login form
 */
function initLoginForm() {
    const form = document.getElementById('loginForm');
    const messageDiv = document.getElementById('message');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Lấy dữ liệu form
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        
        // Validate
        if (!username || !password) {
            showMessage('Vui lòng điền đầy đủ thông tin', 'error');
            return;
        }
        
        // Show loading
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        // Gọi API
        const result = await AuthAPI.login({
            username: username,
            password: password
        });
        
        // Hide loading
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        
        if (result.success) {
            showMessage(CONFIG.MESSAGES.SUCCESS.LOGIN, 'success');
            
            // Redirect sau 500ms
            setTimeout(() => {
                window.location.href = '../dashboard/index.html';
            }, 500);
        } else {
            showMessage(result.message || 'Đăng nhập thất bại', 'error');
        }
    });
}

/**
 * Hiển thị message
 */
function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
    
    // Scroll to message
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Tự động ẩn sau 5 giây nếu là success
    if (type === 'success') {
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
}