/**
 * Vocabulary Page JavaScript
 */

let currentPage = 1;
let totalPages = 1;
let currentVocabId = null;

document.addEventListener('DOMContentLoaded', function() {
    if (!AuthAPI.isAuthenticated()) {
        window.location.href = '../auth/login.html';
        return;
    }
    
    initVocabularyPage();
});

/**
 * Initialize vocabulary page
 */
function initVocabularyPage() {
    loadVocabulary();
    
    // Search
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce(() => {
        currentPage = 1;
        loadVocabulary();
    }, 500));
    
    // Filter
    document.getElementById('statusFilter').addEventListener('change', () => {
        currentPage = 1;
        loadVocabulary();
    });
    
    // Pagination
    document.getElementById('prevBtn').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadVocabulary();
        }
    });
    
    document.getElementById('nextBtn').addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            loadVocabulary();
        }
    });
}

/**
 * Load vocabulary
 */
async function loadVocabulary() {
    const container = document.getElementById('vocabularyGrid');
    const pagination = document.getElementById('pagination');
    
    container.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Đang tải...</p></div>';
    
    try {
        const token = Storage.getToken();
        const status = document.getElementById('statusFilter').value;
        const search = document.getElementById('searchInput').value;
        
        let url = `${CONFIG.buildUrl(CONFIG.ENDPOINTS.VOCABULARY_SAVED)}?page=${currentPage}&per_page=12`;
        if (status) url += `&learned_status=${status}`;
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load vocabulary');
        
        const data = await response.json();
        
        if (!data.success) throw new Error(data.message);
        
        const vocabularies = data.data.items;
        totalPages = data.data.pagination.total_pages;
        
        // Update stats
        document.getElementById('totalWords').textContent = data.data.pagination.total_items;
        
        // Render vocabulary
        if (vocabularies.length === 0) {
            container.innerHTML = `
                <div class="empty-state-vocab">
                    <div class="empty-icon-large">📚</div>
                    <h3>Chưa có từ vựng nào</h3>
                    <p>Hãy xem video và lưu từ vựng để bắt đầu học</p>
                    <a href="../video/list.html" class="btn btn-primary">Xem video</a>
                </div>
            `;
            pagination.style.display = 'none';
            return;
        }
        
        container.innerHTML = vocabularies.map(vocab => renderVocabCard(vocab)).join('');
        
        // Pagination
        if (totalPages > 1) {
            pagination.style.display = 'flex';
            document.getElementById('currentPage').textContent = currentPage;
            document.getElementById('totalPages').textContent = totalPages;
            document.getElementById('prevBtn').disabled = currentPage === 1;
            document.getElementById('nextBtn').disabled = currentPage === totalPages;
        } else {
            pagination.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Load vocabulary error:', error);
        container.innerHTML = `
            <div class="error-state">
                <p>Không thể tải từ vựng. Vui lòng thử lại.</p>
                <button class="btn btn-primary" onclick="loadVocabulary()">Thử lại</button>
            </div>
        `;
    }
}

/**
 * Render vocabulary card
 */
function renderVocabCard(vocab) {
    return `
        <div class="vocab-card" onclick="showVocabDetail(${vocab.vocab_id}, ${vocab.user_vocab_id})">
            <div class="vocab-card-header">
                <h3 class="vocab-word-large">${escapeHtml(vocab.word)}</h3>
                <span class="vocab-status-badge ${vocab.learned_status}">${getStatusText(vocab.learned_status)}</span>
            </div>
            
            ${vocab.pronunciation ? `<div class="vocab-pronunciation">[${escapeHtml(vocab.pronunciation)}]</div>` : ''}
            
            <div class="vocab-translation-large">${escapeHtml(vocab.translation)}</div>
            
            ${vocab.example_sentence ? `
                <div class="vocab-example">
                    <div class="example-en">${escapeHtml(vocab.example_sentence)}</div>
                    ${vocab.example_translation ? `<div class="example-vi">${escapeHtml(vocab.example_translation)}</div>` : ''}
                </div>
            ` : ''}
            
            <div class="vocab-meta">
                ${vocab.part_of_speech ? `<span>📖 ${vocab.part_of_speech}</span>` : ''}
                ${vocab.difficulty_level ? `<span>📊 ${vocab.difficulty_level}</span>` : ''}
                <span>📅 ${formatDate(vocab.saved_date)}</span>
            </div>
        </div>
    `;
}

/**
 * Get status text
 */
function getStatusText(status) {
    const map = {
        'learning': 'Đang học',
        'learned': 'Đã học',
        'mastered': 'Đã thuộc'
    };
    return map[status] || status;
}

/**
 * Show vocabulary detail
 */
async function showVocabDetail(vocabId, userVocabId) {
    currentVocabId = userVocabId;
    
    try {
        const token = Storage.getToken();
        
        // Get vocab details (cần API endpoint)
        // Tạm thời dùng data từ card
        const vocabCards = document.querySelectorAll('.vocab-card');
        let vocabData = null;
        
        // Show modal
        const modal = document.getElementById('vocabModal');
        modal.classList.add('show');
        
        // TODO: Load full vocab details from API
        // For now, populate with basic info
        
    } catch (error) {
        console.error('Show vocab detail error:', error);
        showNotification('Không thể tải chi tiết từ vựng', 'error');
    }
}

/**
 * Close modal
 */
function closeModal() {
    document.getElementById('vocabModal').classList.remove('show');
    currentVocabId = null;
}

/**
 * Speak word
 */
function speakWord() {
    const word = document.getElementById('modalWord').textContent;
    
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'en-US';
        speechSynthesis.speak(utterance);
    } else {
        showNotification('Trình duyệt không hỗ trợ text-to-speech', 'error');
    }
}

/**
 * Update vocabulary status
 */
async function updateVocabStatus() {
    if (!currentVocabId) return;
    
    const newStatus = document.getElementById('statusSelect').value;
    
    try {
        const token = Storage.getToken();
        
        const response = await fetch(
            CONFIG.buildUrl(`/vocabulary/${currentVocabId}/status`),
            {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    learned_status: newStatus
                })
            }
        );
        
        if (!response.ok) throw new Error('Failed to update');
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Đã cập nhật trạng thái', 'success');
            closeModal();
            loadVocabulary(); // Reload
        }
        
    } catch (error) {
        console.error('Update status error:', error);
        showNotification('Lỗi khi cập nhật trạng thái', 'error');
    }
}

/**
 * Remove vocabulary
 */
async function removeVocab() {
    if (!currentVocabId) return;
    
    if (!confirm('Bạn có chắc muốn xóa từ vựng này?')) return;
    
    try {
        const token = Storage.getToken();
        
        const response = await fetch(
            CONFIG.buildUrl(CONFIG.ENDPOINTS.VOCABULARY_DELETE, { id: currentVocabId }),
            {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        
        if (!response.ok) throw new Error('Failed to delete');
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Đã xóa từ vựng', 'success');
            closeModal();
            loadVocabulary(); // Reload
        }
        
    } catch (error) {
        console.error('Remove vocab error:', error);
        showNotification('Lỗi khi xóa từ vựng', 'error');
    }
}