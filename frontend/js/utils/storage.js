/**
 * Local Storage utilities
 */

const Storage = {
    /**
     * Lưu dữ liệu vào localStorage
     */
    set(key, value) {
        try {
            const serialized = JSON.stringify(value);
            localStorage.setItem(key, serialized);
            return true;
        } catch (error) {
            console.error('Error saving to localStorage:', error);
            return false;
        }
    },
    
    /**
     * Lấy dữ liệu từ localStorage
     */
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    },
    
    /**
     * Xóa dữ liệu khỏi localStorage
     */
    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Error removing from localStorage:', error);
            return false;
        }
    },
    
    /**
     * Xóa tất cả dữ liệu
     */
    clear() {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.error('Error clearing localStorage:', error);
            return false;
        }
    },
    
    /**
     * Kiểm tra key có tồn tại không
     */
    has(key) {
        return localStorage.getItem(key) !== null;
    },
    
    /**
     * Lưu access token
     */
    setToken(token) {
        return this.set(CONFIG.STORAGE_KEYS.ACCESS_TOKEN, token);
    },
    
    /**
     * Lấy access token
     */
    getToken() {
        return this.get(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
    },
    
    /**
     * Xóa access token
     */
    removeToken() {
        return this.remove(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
    },
    
    /**
     * Lưu user data
     */
    setUser(userData) {
        return this.set(CONFIG.STORAGE_KEYS.USER_DATA, userData);
    },
    
    /**
     * Lấy user data
     */
    getUser() {
        return this.get(CONFIG.STORAGE_KEYS.USER_DATA);
    },
    
    /**
     * Xóa user data
     */
    removeUser() {
        return this.remove(CONFIG.STORAGE_KEYS.USER_DATA);
    },
    
    /**
     * Kiểm tra user đã đăng nhập chưa
     */
    isLoggedIn() {
        return this.has(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
    },
    
    /**
     * Logout - xóa tất cả data liên quan đến user
     */
    logout() {
        this.removeToken();
        this.removeUser();
    }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Storage;
}