/**
 * Video List Page JavaScript - FIXED VERSION
 * Thêm auto-refresh cho video đang xử lý
 */

let currentPage = 1;
let totalPages = 1;
let deleteVideoId = null;
let refreshInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    if (!AuthAPI.isAuthenticated()) {
        window.location.href = '../auth/login.html';
        return;
    }
    
    initVideoList();
});

// Clear interval khi rời trang
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

/**
 * Initialize video list page
 */
function initVideoList() {
    loadVideos();
    
    // Filters
    document.getElementById('statusFilter').addEventListener('change', () => {
        currentPage = 1;
        loadVideos();
    });
    
    document.getElementById('sortFilter').addEventListener('change', () => {
        currentPage = 1;
        loadVideos();
    });
    
    // Pagination
    document.getElementById('prevBtn').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadVideos();
        }
    });
    
    document.getElementById('nextBtn').addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            loadVideos();
        }
    });
}

/**
 * Load videos
 */
async function loadVideos() {
    const container = document.getElementById('videosContainer');
    const pagination = document.getElementById('pagination');
    
    container.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Đang tải...</p></div>';
    
    try {
        const result = await VideoAPI.getVideos(currentPage, 10);
        
        if (!result.success) {
            throw new Error(result.message);
        }
        
        const videos = result.data.items;
        totalPages = result.data.pagination.total_pages;
        
        if (videos.length === 0) {
            container.innerHTML = `
                <div class="empty-state-large">
                    <div class="empty-icon">🎬</div>
                    <h3>Chưa có video nào</h3>
                    <p>Hãy upload video đầu tiên để bắt đầu học ngoại ngữ với AI</p>
                    <a href="upload.html" class="btn btn-primary">Upload ngay</a>
                </div>
            `;
            pagination.style.display = 'none';
            
            // Clear refresh interval
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
            return;
        }
        
        // Render videos
        container.innerHTML = videos.map(video => renderVideoItem(video)).join('');
        
        // Show pagination
        if (totalPages > 1) {
            pagination.style.display = 'flex';
            document.getElementById('currentPage').textContent = currentPage;
            document.getElementById('totalPages').textContent = totalPages;
            document.getElementById('prevBtn').disabled = currentPage === 1;
            document.getElementById('nextBtn').disabled = currentPage === totalPages;
        } else {
            pagination.style.display = 'none';
        }
        
        // ✅ FIX: Auto-refresh nếu có video đang xử lý
        const hasProcessingVideos = videos.some(v => v.status === 'processing' || v.status === 'pending');
        
        if (hasProcessingVideos) {
            // Bắt đầu auto-refresh mỗi 5 giây
            if (!refreshInterval) {
                console.log('🔄 Starting auto-refresh for processing videos...');
                refreshInterval = setInterval(() => {
                    console.log('🔄 Auto-refreshing video list...');
                    loadVideos();
                }, 5000); // 5 giây
            }
        } else {
            // Dừng auto-refresh nếu không còn video nào đang xử lý
            if (refreshInterval) {
                console.log('✅ All videos processed. Stopping auto-refresh.');
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
        }
        
    } catch (error) {
        console.error('Load videos error:', error);
        container.innerHTML = `
            <div class="error-state">
                <p>Không thể tải danh sách video. Vui lòng thử lại.</p>
                <button class="btn btn-primary" onclick="loadVideos()">Thử lại</button>
            </div>
        `;
    }
}

/**
 * Render video item
 */
function renderVideoItem(video) {
    const statusClass = video.status;
    const statusText = getStatusText(video.status);
    
    return `
        <div class="video-item" data-video-id="${video.video_id}">
            <div class="video-thumbnail-large">
                🎬
            </div>
            
            <div class="video-details">
                <div class="video-header">
                    <div>
                        <h3 class="video-title-large">${escapeHtml(video.title)}</h3>
                        <span class="video-status ${statusClass}">${statusText}</span>
                    </div>
                    
                    <div class="video-actions">
                        ${video.status === 'completed' ? 
                            `<a href="player.html?id=${video.video_id}" class="btn btn-primary btn-icon" title="Xem video">▶</a>` : 
                            ''}
                        ${video.status === 'pending' || video.status === 'failed' ? 
                            `<button class="btn btn-primary btn-icon" onclick="processVideo(${video.video_id})" title="Xử lý video">⚡</button>` : 
                            ''}
                        <button class="btn btn-outline btn-icon" onclick="showDeleteModal(${video.video_id})" title="Xóa">🗑️</button>
                    </div>
                </div>
                
                <div class="video-meta-list">
                    <span class="video-meta-item">📅 ${formatDate(video.upload_date)}</span>
                    ${video.duration ? `<span class="video-meta-item">⏱️ ${formatDuration(video.duration)}</span>` : ''}
                    ${video.language_detected ? `<span class="video-meta-item">🌐 ${video.language_detected.toUpperCase()}</span>` : ''}
                </div>
                
                ${video.status === 'processing' ? `
                    <div class="video-progress">
                        <div class="progress-label">
                            <span>Đang xử lý video...</span>
                            <span>⏳</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 50%; animation: pulse 2s infinite;"></div>
                        </div>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

/**
 * Get status text
 */
function getStatusText(status) {
    const statusMap = {
        'pending': 'Chờ xử lý',
        'processing': 'Đang xử lý',
        'completed': 'Hoàn thành',
        'failed': 'Thất bại'
    };
    return statusMap[status] || status;
}

/**
 * Process video
 */
async function processVideo(videoId) {
    // Prevent default action
    event.preventDefault();
    event.stopPropagation();
    
    if (!confirm('Bắt đầu xử lý video? Quá trình có thể mất 2-5 phút.')) {
        return;
    }
    
    showLoading('Đang bắt đầu xử lý video...');
    
    try {
        const token = Storage.getToken();
        const url = `${CONFIG.API_BASE_URL}/process/video/${videoId}`;
        
        console.log('Processing video at:', url);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        hideLoading();
        
        console.log('Process response:', data);
        
        if (response.ok && data.success) {
            showNotification('Đã bắt đầu xử lý video. Vui lòng chờ vài phút.', 'success');
            
            // Reload list ngay lập tức
            loadVideos();
        } else {
            showNotification(data.message || 'Lỗi khi xử lý video', 'error');
        }
        
    } catch (error) {
        hideLoading();
        console.error('Process video error:', error);
        showNotification('Lỗi khi xử lý video: ' + error.message, 'error');
    }
}

/**
 * Show delete modal
 */
function showDeleteModal(videoId) {
    deleteVideoId = videoId;
    document.getElementById('deleteModal').classList.add('show');
    
    document.getElementById('confirmDeleteBtn').onclick = confirmDelete;
}

/**
 * Close delete modal
 */
function closeDeleteModal() {
    deleteVideoId = null;
    document.getElementById('deleteModal').classList.remove('show');
}

/**
 * Confirm delete
 */
async function confirmDelete() {
    if (!deleteVideoId) return;
    
    closeDeleteModal();
    showLoading('Đang xóa video...');
    
    try {
        const result = await VideoAPI.deleteVideo(deleteVideoId);
        
        hideLoading();
        
        if (result.success) {
            showNotification('Đã xóa video thành công', 'success');
            loadVideos(); // Reload list
        } else {
            showNotification(result.message || 'Lỗi khi xóa video', 'error');
        }
        
    } catch (error) {
        hideLoading();
        console.error('Delete video error:', error);
        showNotification('Lỗi khi xóa video', 'error');
    }
}

// CSS animation for pulse
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
`;
document.head.appendChild(style);