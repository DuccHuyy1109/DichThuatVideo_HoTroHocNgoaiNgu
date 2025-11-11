/**
 * User API
 * Xử lý các API liên quan đến user
 */

const UserAPI = {
    /**
     * Get profile
     */
    async getProfile() {
        try {
            const token = Storage.getToken();
            
            const response = await fetch(
                CONFIG.buildUrl(CONFIG.ENDPOINTS.USER_PROFILE),
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Get profile error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    },
    
    /**
     * Update profile
     */
    async updateProfile(profileData) {
        try {
            const token = Storage.getToken();
            
            const response = await fetch(
                CONFIG.buildUrl(CONFIG.ENDPOINTS.USER_PROFILE),
                {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(profileData)
                }
            );
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Update local storage
                if (data.data.user) {
                    Storage.setUser(data.data.user);
                }
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Update profile error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    },
    
    /**
     * Get learning progress
     */
    async getProgress() {
        try {
            const token = Storage.getToken();
            
            const response = await fetch(
                CONFIG.buildUrl(CONFIG.ENDPOINTS.USER_PROGRESS),
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Get progress error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    },
    
    /**
     * Update learning progress
     */
    async updateProgress(videoId, watchDuration, completionPercentage) {
        try {
            const token = Storage.getToken();
            
            const response = await fetch(
                CONFIG.buildUrl(CONFIG.ENDPOINTS.USER_PROGRESS),
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        video_id: videoId,
                        watch_duration: watchDuration,
                        completion_percentage: completionPercentage
                    })
                }
            );
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Update progress error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    },
    
    /**
     * Change password
     */
    async changePassword(oldPassword, newPassword) {
        try {
            const token = Storage.getToken();
            
            const response = await fetch(
                CONFIG.buildUrl(CONFIG.ENDPOINTS.CHANGE_PASSWORD),
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        old_password: oldPassword,
                        new_password: newPassword
                    })
                }
            );
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, message: data.message };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Change password error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserAPI;
}