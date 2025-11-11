/**
 * Auth API
 * Xử lý các API liên quan đến authentication
 */

const AuthAPI = {
    /**
     * Đăng ký người dùng mới
     */
    async register(userData) {
        try {
            const response = await fetch(CONFIG.buildUrl(CONFIG.ENDPOINTS.REGISTER), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });
            
            const data = await response.json();
            
            console.log('Register response:', data); // Debug log
            
            if (response.ok && data.success) {
                // Lưu token và user data
                if (data.data.access_token) {
                    Storage.setToken(data.data.access_token);
                    console.log('Token saved:', data.data.access_token); // Debug log
                }
                if (data.data.user) {
                    Storage.setUser(data.data.user);
                    console.log('User saved:', data.data.user); // Debug log
                }
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Register error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    },
    
    /**
     * Đăng nhập
     */
    async login(credentials) {
        try {
            console.log('Login attempt with:', credentials); // Debug log
            
            const response = await fetch(CONFIG.buildUrl(CONFIG.ENDPOINTS.LOGIN), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(credentials)
            });
            
            const data = await response.json();
            
            console.log('Login response:', data); // Debug log
            console.log('Response status:', response.status); // Debug log
            
            if (response.ok && data.success) {
                // Lưu token và user data
                if (data.data && data.data.access_token) {
                    Storage.setToken(data.data.access_token);
                    console.log('✅ Token saved:', data.data.access_token.substring(0, 20) + '...'); // Debug log
                } else {
                    console.error('❌ No access_token in response'); // Debug log
                }
                
                if (data.data && data.data.user) {
                    Storage.setUser(data.data.user);
                    console.log('✅ User saved:', data.data.user); // Debug log
                } else {
                    console.error('❌ No user in response'); // Debug log
                }
                
                // Verify token was saved
                const savedToken = Storage.getToken();
                console.log('Verified saved token:', savedToken ? 'YES' : 'NO');
                
                return { success: true, data: data.data };
            } else {
                console.error('Login failed:', data.message);
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    },
    
    /**
     * Đăng xuất
     */
    async logout() {
        try {
            const token = Storage.getToken();
            
            if (token) {
                await fetch(CONFIG.buildUrl(CONFIG.ENDPOINTS.LOGOUT), {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
            }
            
            // Xóa data local
            Storage.logout();
            
            return { success: true };
        } catch (error) {
            console.error('Logout error:', error);
            // Vẫn xóa data local dù API lỗi
            Storage.logout();
            return { success: true };
        }
    },
    
    /**
     * Xác thực token
     */
    async verifyToken() {
        try {
            const token = Storage.getToken();
            
            console.log('Verifying token:', token ? 'EXISTS' : 'NONE'); // Debug log
            
            if (!token) {
                return { success: false, message: 'No token found' };
            }
            
            const response = await fetch(CONFIG.buildUrl(CONFIG.ENDPOINTS.VERIFY), {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            console.log('Verify response:', response.status, data); // Debug log
            
            if (response.ok && data.success) {
                // Cập nhật user data
                if (data.data.user) {
                    Storage.setUser(data.data.user);
                }
                return { success: true, data: data.data };
            } else {
                // Token không hợp lệ, xóa
                console.log('Token invalid, clearing storage');
                Storage.logout();
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Verify token error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    },
    
    /**
     * Lấy thông tin user hiện tại
     */
    async getCurrentUser() {
        try {
            const token = Storage.getToken();
            
            if (!token) {
                return { success: false, message: 'Not logged in' };
            }
            
            const response = await fetch(CONFIG.buildUrl(CONFIG.ENDPOINTS.ME), {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                if (data.data.user) {
                    Storage.setUser(data.data.user);
                }
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Get current user error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    },
    
    /**
     * Kiểm tra đã đăng nhập chưa
     */
    isAuthenticated() {
        const hasToken = Storage.isLoggedIn();
        console.log('isAuthenticated check:', hasToken); // Debug log
        return hasToken;
    }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthAPI;
}