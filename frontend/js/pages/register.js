/**
 * Register Page JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Kiểm tra đã đăng nhập chưa
    if (AuthAPI.isAuthenticated()) {
        window.location.href = '../dashboard/index.html';
        return;
    }
    
    initRegisterForm();
});

/**
 * Khởi tạo register form
 */
function initRegisterForm() {
    const form = document.getElementById('registerForm');
    const messageDiv = document.getElementById('message');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Lấy dữ liệu form
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const fullName = document.getElementById('full_name').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        const agreeTerms = document.getElementById('agree_terms').checked;
        
        // Validate
        if (!username || !email || !password || !confirmPassword) {
            showMessage('Vui lòng điền đầy đủ thông tin bắt buộc', 'error');
            return;
        }
        
        if (username.length < 3 || username.length > 50) {
            showMessage('Tên đăng nhập phải từ 3-50 ký tự', 'error');
            return;
        }
        
        if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
            showMessage('Tên đăng nhập chỉ chứa chữ, số, dấu _ và -', 'error');
            return;
        }
        
        if (password.length < 6) {
            showMessage('Mật khẩu phải có ít nhất 6 ký tự', 'error');
            return;
        }
        
        if (!/[a-zA-Z]/.test(password) || !/[0-9]/.test(password)) {
            showMessage('Mật khẩu phải chứa cả chữ và số', 'error');
            return;
        }
        
        if (password !== confirmPassword) {
            showMessage('Mật khẩu xác nhận không khớp', 'error');
            return;
        }
        
        if (!agreeTerms) {
            showMessage('Vui lòng đồng ý với điều khoản sử dụng', 'error');
            return;
        }
        
        // Show loading
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        // Gọi API
        const result = await AuthAPI.register({
            username: username,
            email: email,
            password: password,
            full_name: fullName || null
        });
        
        // Hide loading
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        
        if (result.success) {
            showMessage(CONFIG.MESSAGES.SUCCESS.REGISTER, 'success');
            
            // Redirect sau 1.5 giây
            setTimeout(() => {
                window.location.href = '../dashboard/index.html';
            }, 1500);
        } else {
            showMessage(result.message || 'Đăng ký thất bại', 'error');
        }
    });
    
    // Real-time validation
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    
    confirmPasswordInput.addEventListener('input', function() {
        if (this.value && this.value !== passwordInput.value) {
            this.setCustomValidity('Mật khẩu không khớp');
        } else {
            this.setCustomValidity('');
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