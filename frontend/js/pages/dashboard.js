/**
 * Dashboard Page JavaScript
 */

document.addEventListener('DOMContentLoaded', async function() {
    // Check authentication với verify token
    const isAuth = await checkAuthentication();
    
    if (!isAuth) {
        window.location.href = '../auth/login.html';
        return;
    }
    
    await initDashboard();
});

/**
 * Check authentication
 */
async function checkAuthentication() {
    const token = Storage.getToken();
    
    if (!token) {
        return false;
    }
    
    // Verify token với server
    const result = await AuthAPI.verifyToken();
    
    if (!result.success) {
        // Token không hợp lệ, xóa và redirect
        Storage.logout();
        return false;
    }
    
    return true;
}

/**
 * Initialize dashboard
 */
async function initDashboard() {
    // Load user info
    await loadUserInfo();
    
    // Load statistics
    await loadStatistics();
    
    // Load recent videos
    await loadRecentVideos();
    
    // Load learning progress
    await loadLearningProgress();
    
    // Init event listeners
    initEventListeners();
}

/**
 * Load user info
 */
async function loadUserInfo() {
    try {
        const user = Storage.getUser();
        
        if (user) {
            // Display user name
            document.getElementById('userName').textContent = user.full_name || user.username;
            
            // Display user initials
            const initials = getInitials(user.full_name || user.username);
            document.getElementById('userInitials').textContent = initials;
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

/**
 * Load statistics
 */
async function loadStatistics() {
    try {
        const token = Storage.getToken();
        
        // Get videos count
        const videosResponse = await fetch(
            CONFIG.buildUrl(CONFIG.ENDPOINTS.VIDEOS),
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        
        if (videosResponse.ok) {
            const videosData = await videosResponse.json();
            document.getElementById('totalVideos').textContent = 
                videosData.data.pagination.total_items || 0;
        }
        
        // Get vocabulary count
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
        
        // TODO: Get quiz accuracy and study time from API
        document.getElementById('quizAccuracy').textContent = '0%';
        document.getElementById('studyTime').textContent = '0h';
        
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

/**
 * Load recent videos
 */
async function loadRecentVideos() {
    const container = document.getElementById('recentVideos');
    
    try {
        const token = Storage.getToken();
        
        const response = await fetch(
            CONFIG.buildUrl(CONFIG.ENDPOINTS.VIDEOS) + '?per_page=6',
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        
        if (!response.ok) {
            throw new Error('Failed to load videos');
        }
        
        const data = await response.json();
        const videos = data.data.items;
        
        if (videos.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>Chưa có video nào. Hãy upload video đầu tiên!</p>
                    <a href="../video/upload.html" class="btn btn-primary">Upload ngay</a>
                </div>
            `;
            return;
        }
        
        container.innerHTML = videos.map(video => `
            <div class="video-card">
                <div class="video-thumbnail">
                    🎬
                </div>
                <div class="video-info">
                    <h3 class="video-title">${escapeHtml(video.title)}</h3>
                    <div class="video-meta">
                        <span>${formatDate(video.upload_date)}</span>
                        <span>${formatDuration(video.duration || 0)}</span>
                    </div>
                    <span class="video-status ${video.status}">${getStatusText(video.status)}</span>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading videos:', error);
        container.innerHTML = `
            <div class="error-state">
                <p>Không thể tải video. Vui lòng thử lại.</p>
            </div>
        `;
    }
}

/**
 * Load learning progress
 */
async function loadLearningProgress() {
    const container = document.getElementById('progressList');
    
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
        
        if (!response.ok) {
            throw new Error('Failed to load progress');
        }
        
        const data = await response.json();
        const progress = data.data.progress;
        
        if (progress.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>Chưa có tiến trình học tập</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = progress.map(item => `
            <div class="progress-item">
                <div class="progress-header">
                    <h4>${escapeHtml(item.video_title)}</h4>
                    <span>${item.completion_percentage}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${item.completion_percentage}%"></div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading progress:', error);
    }
}

/**
 * Initialize event listeners
 */
function initEventListeners() {
    // User menu dropdown
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    
    userMenuBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        userDropdown.classList.toggle('show');
    });
    
    document.addEventListener('click', function() {
        userDropdown.classList.remove('show');
    });
    
    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    logoutBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        
        await AuthAPI.logout();
        window.location.href = '../auth/login.html';
    });
    
    // Search
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce(function() {
        const query = this.value.trim();
        if (query) {
            searchVideos(query);
        } else {
            loadRecentVideos();
        }
    }, 500));
}

/**
 * Search videos
 */
async function searchVideos(query) {
    // TODO: Implement search functionality
    console.log('Searching for:', query);
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
 * Get status text in Vietnamese
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
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}