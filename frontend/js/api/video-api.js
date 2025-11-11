/**
 * Video API
 * Xử lý các API liên quan đến video
 */

const VideoAPI = {
    /**
     * Get danh sách videos
     */
    async getVideos(page = 1, perPage = 10) {
        try {
            const token = Storage.getToken();
            
            const response = await fetch(
                `${CONFIG.buildUrl(CONFIG.ENDPOINTS.VIDEOS)}?page=${page}&per_page=${perPage}`,
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
            console.error('Get videos error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    },
    
    /**
     * Get video detail
     */
    async getVideo(videoId) {
        try {
            const token = Storage.getToken();
            
            const response = await fetch(
                CONFIG.buildUrl(CONFIG.ENDPOINTS.VIDEO_DETAIL, { id: videoId }),
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
            console.error('Get video error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    },
    
    /**
     * Delete video
     */
    async deleteVideo(videoId) {
        try {
            const token = Storage.getToken();
            
            const response = await fetch(
                CONFIG.buildUrl(CONFIG.ENDPOINTS.VIDEO_DELETE, { id: videoId }),
                {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, message: data.message };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Delete video error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    },
    
    /**
     * Get video status
     */
    async getVideoStatus(videoId) {
        try {
            const token = Storage.getToken();
            
            const response = await fetch(
                CONFIG.buildUrl(CONFIG.ENDPOINTS.VIDEO_STATUS, { id: videoId }),
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
            console.error('Get video status error:', error);
            return { success: false, message: CONFIG.MESSAGES.ERROR.NETWORK };
        }
    }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VideoAPI;
}