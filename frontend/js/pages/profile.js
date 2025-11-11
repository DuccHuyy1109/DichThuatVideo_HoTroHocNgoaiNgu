/**
 * Profile Page JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    if (!AuthAPI.isAuthenticated()) {
        window.location.href = '../auth/login.html';
        return;
    }
    
    initProfilePage();
});

/**
 * Initialize profile page
 */
async function initProfilePage() {
    await loadUserProfile();
    await loadAccountStats();
    
    // Profile form submit
    document.getElementById('profileForm').addEventListener('submit', handleProfileUpdate);
    
    // Password form submit
    document.getElementById('passwordForm').addEventListener('submit', handlePasswordChange);
}

/**
 * Load user profile
 */
async function loadUserProfile() {
    try {
        const result = await UserAPI.getProfile();
        
        if (result.success) {
            const user = result.data.user;
            
            // Update form fields
            document.getElementById('username').value = user.username;
            document.getElementById('email').value = user.email;
            document.getElementById('fullName').value = user.full_name || '';
            document.getElementById('joinDate').value = formatDate(user.created_at);
            document.getElementById('lastLogin').textContent = formatDate(user.last_login);
            
            // Update avatar initials
            const initials = getInitials(user.full_name || user.username);
            document.getElementById('avatarInitials').textContent = initials;
        }
        
    } catch (error) {
        console.error('Load profile error:', error);
        showMessage('Không thể tải thông tin profile', 'error');
    }
}

/**
 * Load account statistics
 */
async function loadAccountStats() {
    try {
        // Get videos count
        const videosResult = await VideoAPI.getVideos(1, 1);
        if (videosResult.success) {
            document.getElementById('totalVideos').textContent = 
                videosResult.data.pagination.total_items;
        }
        
        // Get vocabulary count
        const token = Storage.getToken();
        const vocabResponse = await fetch(
            CONFIG.buildUrl(CONFIG.ENDPOINTS.VOCABULARY_SAVED),
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        
        if (vocabResponse.ok) {
            const vocabData = await vocabResponse.json();
            document.getElementById('totalVocab').textContent = 
                vocabData.data.pagination.total_items || 0;
        }
        
        // Quiz count - placeholder
        document.getElementById('totalQuiz').textContent = '0';
        
    } catch (error) {
        console.error('Load stats error:', error);
    }
}

/**
 * Handle profile update
 */
async function handleProfileUpdate(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const fullName = document.getElementById('fullName').value.trim();
    
    if (!email) {
        showMessage('Email không được để trống', 'error');
        return;
    }
    
    showLoading('Đang cập nhật...');
    
    try {
        const result = await UserAPI.updateProfile({
            email: email,
            full_name: fullName
        });
        
        hideLoading();
        
        if (result.success) {
            showMessage('Cập nhật thông tin thành công!', 'success');
            
            // Update avatar
            const initials = getInitials(fullName || email);
            document.getElementById('avatarInitials').textContent = initials;
        } else {
            showMessage(result.message || 'Cập nhật thất bại', 'error');
        }
        
    } catch (error) {
        hideLoading();
        console.error('Update profile error:', error);
        showMessage('Lỗi khi cập nhật thông tin', 'error');
    }
}

/**
 * Handle password change
 */
async function handlePasswordChange(e) {
    e.preventDefault();
    
    const oldPassword = document.getElementById('oldPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validate
    if (newPassword.length < 6) {
        showMessage('Mật khẩu mới phải có ít nhất 6 ký tự', 'error');
        return;
    }
    
    if (!/[a-zA-Z]/.test(newPassword) || !/[0-9]/.test(newPassword)) {
        showMessage('Mật khẩu phải chứa cả chữ và số', 'error');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showMessage('Mật khẩu xác nhận không khớp', 'error');
        return;
    }
    
    showLoading('Đang đổi mật khẩu...');
    
    try {
        const result = await UserAPI.changePassword(oldPassword, newPassword);
        
        hideLoading();
        
        if (result.success) {
            showMessage('Đổi mật khẩu thành công!', 'success');
            
            // Reset form
            document.getElementById('passwordForm').reset();
        } else {
            showMessage(result.message || 'Đổi mật khẩu thất bại', 'error');
        }
        
    } catch (error) {
        hideLoading();
        console.error('Change password error:', error);
        showMessage('Lỗi khi đổi mật khẩu', 'error');
    }
}

/**
 * Confirm delete account
 */
function confirmDeleteAccount() {
    const confirmation = prompt('Nhập "XOA TAI KHOAN" để xác nhận xóa tài khoản (không thể hoàn tác):');
    
    if (confirmation === 'XOA TAI KHOAN') {
        deleteAccount();
    } else if (confirmation !== null) {
        alert('Xác nhận không đúng. Hủy xóa tài khoản.');
    }
}

/**
 * Delete account
 */
async function deleteAccount() {
    showLoading('Đang xóa tài khoản...');
    
    try {
        // TODO: Implement delete account API
        // For now, just logout
        
        hideLoading();
        alert('Chức năng xóa tài khoản chưa được triển khai');
        
    } catch (error) {
        hideLoading();
        console.error('Delete account error:', error);
        showMessage('Lỗi khi xóa tài khoản', 'error');
    }
}

/**
 * Get initials from name
 */
function getInitials(name) {
    return name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .substring(0, 2);
}

/**
 * Show message
 */
function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
    
    // Scroll to message
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Auto hide after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
}