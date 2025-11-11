/**
 * Progress Page JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    if (!AuthAPI.isAuthenticated()) {
        window.location.href = '../auth/login.html';
        return;
    }
    
    initProgressPage();
});

/**
 * Initialize progress page
 */
async function initProgressPage() {
    await loadOverviewStats();
    await loadVideoProgress();
    // Chart would need a library like Chart.js
    // initActivityChart();
}

/**
 * Load overview statistics
 */
async function loadOverviewStats() {
    try {
        const result = await UserAPI.getProgress();
        
        if (result.success) {
            const progress = result.data.progress;
            
            // Calculate stats
            const totalVideos = progress.length;
            const totalTime = calculateTotalTime(progress);
            
            document.getElementById('totalVideos').textContent = totalVideos;
            document.getElementById('totalTime').textContent = formatTotalTime(totalTime);
            
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
            
            // Quiz score - placeholder
            document.getElementById('quizScore').textContent = '0%';
        }
        
    } catch (error) {
        console.error('Load stats error:', error);
    }
}

/**
 * Load video progress
 */
async function loadVideoProgress() {
    const container = document.getElementById('videoProgressList');
    
    try {
        const result = await UserAPI.getProgress();
        
        if (!result.success) {
            throw new Error(result.message);
        }
        
        const progress = result.data.progress;
        
        if (progress.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>Chưa có tiến trình học tập nào</p>
                    <a href="../video/list.html" class="btn btn-primary">Xem video</a>
                </div>
            `;
            return;
        }
        
        container.innerHTML = progress.map(item => renderProgressItem(item)).join('');
        
    } catch (error) {
        console.error('Load progress error:', error);
        container.innerHTML = `
            <div class="error-state">
                <p>Không thể tải tiến trình. Vui lòng thử lại.</p>
                <button class="btn btn-primary" onclick="loadVideoProgress()">Thử lại</button>
            </div>
        `;
    }
}

/**
 * Render progress item
 */
function renderProgressItem(item) {
    const percentage = Math.round(item.completion_percentage || 0);
    const watchTime = formatDuration(item.watch_duration || 0);
    
    return `
        <div class="progress-item-detailed">
            <div class="progress-item-header">
                <h3 class="progress-video-title">${escapeHtml(item.video_title)}</h3>
                <span class="progress-percentage">${percentage}%</span>
            </div>
            
            <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: ${percentage}%"></div>
            </div>
            
            <div class="progress-meta-row">
                <span>⏱️ Đã xem: ${watchTime}</span>
                <span>🔄 Xem ${item.watch_count || 1} lần</span>
                <span>📅 ${formatDate(item.last_watched)}</span>
            </div>
        </div>
    `;
}

/**
 * Calculate total watch time
 */
function calculateTotalTime(progress) {
    return progress.reduce((total, item) => total + (item.watch_duration || 0), 0);
}

/**
 * Format total time to hours and minutes
 */
function formatTotalTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
}

/**
 * Initialize activity chart (requires Chart.js library)
 */
function initActivityChart() {
    // This would require Chart.js library
    // Example implementation:
    /*
    const ctx = document.getElementById('activityChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Minutes Watched',
                data: [30, 45, 20, 60, 40, 50, 35],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
    */
}