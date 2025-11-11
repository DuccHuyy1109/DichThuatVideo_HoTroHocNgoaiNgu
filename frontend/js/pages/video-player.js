/**
 * Video Player Page JavaScript - COMPLETE VERSION
 * Hiển thị ĐẦY ĐỦ thông tin từ vựng: pronunciation, part_of_speech, example, etc.
 */

let currentVideoId = null;
let subtitles = [];
let currentSubtitleIndex = -1;
let vocabularies = []; // ✅ Store globally để dùng cho modal

document.addEventListener('DOMContentLoaded', async function() {
    const isAuth = await checkAuthentication();
    
    if (!isAuth) {
        window.location.href = '../auth/login.html';
        return;
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    currentVideoId = urlParams.get('id');
    
    console.log('🎬 Video ID from URL:', currentVideoId);
    
    if (!currentVideoId || currentVideoId === 'null' || currentVideoId === 'undefined') {
        console.error('❌ Invalid video ID');
        showNotification('Video ID không hợp lệ. Đang chuyển về danh sách...', 'error');
        setTimeout(() => {
            window.location.href = 'list.html';
        }, 2000);
        return;
    }
    
    initPlayer();
});

async function checkAuthentication() {
    const token = Storage.getToken();
    if (!token) return false;
    
    const result = await AuthAPI.verifyToken();
    if (!result.success) {
        Storage.logout();
        return false;
    }
    return true;
}

async function initPlayer() {
    await loadVideoData();
    initTabs();
    initPlayerControls();
    initVideoEvents();
}

async function loadVideoData() {
    try {
        console.log('📥 Loading video data for ID:', currentVideoId);
        
        const videoResult = await VideoAPI.getVideo(currentVideoId);
        
        if (!videoResult.success) {
            throw new Error(videoResult.message);
        }
        
        const video = videoResult.data.video;
        
        console.log('✅ Video loaded:', video);
        
        document.getElementById('videoTitle').textContent = video.title;
        document.getElementById('videoDuration').textContent = formatDuration(video.duration || 0);
        document.getElementById('videoLanguage').textContent = video.language_detected?.toUpperCase() || '--';
        
        await loadVideoSource();
        await loadSubtitles();
        await loadVocabulary();
        await loadQuiz();
        await loadTranscript();
        
    } catch (error) {
        console.error('❌ Load video data error:', error);
        showNotification('Không thể tải dữ liệu video', 'error');
    }
}

async function loadVideoSource() {
    try {
        const token = Storage.getToken();
        const videoPlayer = document.getElementById('videoPlayer');
        
        const videoUrl = `${CONFIG.API_BASE_URL}/videos/stream/${currentVideoId}`;
        
        console.log('🎬 Loading video from:', videoUrl);
        
        const response = await fetch(videoUrl, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Cannot load video');
        }
        
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        
        videoPlayer.src = blobUrl;
        
        console.log('✅ Video loaded successfully');
        
    } catch (error) {
        console.error('❌ Load video source error:', error);
        showNotification('Không thể tải video. Vui lòng thử lại.', 'error');
    }
}

async function loadSubtitles() {
    try {
        const token = Storage.getToken();
        
        const response = await fetch(
            `${CONFIG.API_BASE_URL}/subtitles/${currentVideoId}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        
        if (!response.ok) return;
        
        const data = await response.json();
        
        console.log('✅ Subtitles response:', data);
        
        if (data.success && data.data.subtitles.length > 0) {
            const subtitle = data.data.subtitles[0];
            subtitles = JSON.parse(subtitle.content);
            console.log('✅ Loaded subtitles:', subtitles.length);
        }
        
    } catch (error) {
        console.error('Load subtitles error:', error);
    }
}

/**
 * ✅ FIXED: Load và hiển thị ĐẦY ĐỦ thông tin từ vựng
 */
async function loadVocabulary() {
    const container = document.getElementById('vocabularyList');
    
    try {
        const token = Storage.getToken();
        
        const response = await fetch(
            `${CONFIG.API_BASE_URL}/vocabulary/${currentVideoId}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        
        console.log('📚 Vocabulary response status:', response.status);
        
        if (!response.ok) {
            container.innerHTML = '<div class="empty-state"><p>Chưa có từ vựng</p></div>';
            return;
        }
        
        const data = await response.json();
        
        console.log('📚 Vocabulary full response:', data);
        
        if (data.success && data.data && data.data.vocabularies && data.data.vocabularies.length > 0) {
            vocabularies = data.data.vocabularies; // ✅ Store globally
            
            console.log('✅ Found vocabs:', vocabularies.length);
            console.log('📖 First vocab sample:', vocabularies[0]);
            
            // ✅ FIXED: Render vocabulary card với ĐẦY ĐỦ thông tin (bao gồm example)
            container.innerHTML = vocabularies.map(vocab => `
                <div class="vocab-item" onclick="showVocabDetail(${vocab.vocab_id})">
                    <div class="vocab-word">${escapeHtml(vocab.word)}</div>
                    ${vocab.pronunciation ? `<div class="vocab-pronunciation">${escapeHtml(vocab.pronunciation)}</div>` : ''}
                    <div class="vocab-translation">${escapeHtml(vocab.translation)}</div>
                    ${vocab.part_of_speech ? `<div class="vocab-type">${escapeHtml(vocab.part_of_speech)}</div>` : ''}
                    ${vocab.example_sentence ? `
                        <div class="vocab-example">
                            <div class="example-text">${escapeHtml(vocab.example_sentence)}</div>
                            ${vocab.example_translation ? `<div class="example-trans">${escapeHtml(vocab.example_translation)}</div>` : ''}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        } else {
            console.warn('⚠️ No vocabulary to display');
            container.innerHTML = '<div class="empty-state"><p>Chưa có từ vựng</p></div>';
        }
        
    } catch (error) {
        console.error('❌ Load vocabulary error:', error);
        container.innerHTML = '<div class="error-state"><p>Lỗi tải từ vựng</p></div>';
    }
}

async function loadQuiz() {
    const container = document.getElementById('quizContainer');
    
    try {
        const token = Storage.getToken();
        
        const response = await fetch(
            `${CONFIG.API_BASE_URL}/quiz/${currentVideoId}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        
        console.log('❓ Quiz response status:', response.status);
        
        if (!response.ok) {
            container.innerHTML = '<div class="empty-state"><p>Chưa có quiz</p></div>';
            return;
        }
        
        const data = await response.json();
        
        console.log('❓ Quiz full response:', data);
        
        if (data.success && data.data && data.data.quizzes && data.data.quizzes.length > 0) {
            const quizzes = data.data.quizzes;
            
            console.log('✅ Found quizzes:', quizzes.length);
            
            container.innerHTML = quizzes.map((quiz, index) => renderQuizQuestion(quiz, index)).join('');
            
            document.querySelectorAll('.quiz-option').forEach(option => {
                option.addEventListener('click', handleQuizAnswer);
            });
        } else {
            console.warn('⚠️ No quiz to display');
            container.innerHTML = '<div class="empty-state"><p>Chưa có quiz</p></div>';
        }
        
    } catch (error) {
        console.error('❌ Load quiz error:', error);
        container.innerHTML = '<div class="error-state"><p>Lỗi tải quiz</p></div>';
    }
}

function renderQuizQuestion(quiz, index) {
    return `
        <div class="quiz-question" data-quiz-id="${quiz.quiz_id}">
            <div class="question-text">
                <strong>Câu ${index + 1}:</strong> ${escapeHtml(quiz.question)}
            </div>
            <div class="quiz-options">
                ${quiz.options.map((option, i) => `
                    <div class="quiz-option" data-quiz-id="${quiz.quiz_id}" data-option="${i}" data-correct="${quiz.correct_answer === i}">
                        ${String.fromCharCode(65 + i)}. ${escapeHtml(option)}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function handleQuizAnswer(event) {
    const option = event.currentTarget;
    const quizId = option.dataset.quizId;
    const isCorrect = option.dataset.correct === 'true';
    
    document.querySelectorAll(`[data-quiz-id="${quizId}"]`).forEach(opt => {
        opt.classList.remove('selected', 'correct', 'wrong');
    });
    
    option.classList.add('selected');
    
    if (isCorrect) {
        option.classList.add('correct');
        showNotification('Chính xác! 🎉', 'success');
    } else {
        option.classList.add('wrong');
        showNotification('Sai rồi! Thử lại nhé 😊', 'error');
        document.querySelector(`[data-quiz-id="${quizId}"][data-correct="true"]`).classList.add('correct');
    }
}

async function loadTranscript() {
    const container = document.getElementById('transcriptList');
    
    if (subtitles.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>Chưa có transcript</p></div>';
        return;
    }
    
    container.innerHTML = subtitles.map((seg, index) => `
        <div class="transcript-item" onclick="seekToTime(${seg.start})">
            <div class="transcript-time">${formatDuration(seg.start)}</div>
            <div class="transcript-text">${escapeHtml(seg.text)}</div>
            ${seg.translation ? `<div class="transcript-translation">${escapeHtml(seg.translation)}</div>` : ''}
        </div>
    `).join('');
}

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
}

function initPlayerControls() {
    const videoPlayer = document.getElementById('videoPlayer');
    
    document.getElementById('playbackRate').addEventListener('change', function() {
        videoPlayer.playbackRate = parseFloat(this.value);
    });
    
    document.getElementById('showOriginal').addEventListener('change', function() {
        document.getElementById('subtitleOriginal').style.display = this.checked ? 'block' : 'none';
    });
    
    document.getElementById('showTranslation').addEventListener('change', function() {
        document.getElementById('subtitleTranslation').style.display = this.checked ? 'block' : 'none';
    });
}

function initVideoEvents() {
    const videoPlayer = document.getElementById('videoPlayer');
    
    videoPlayer.addEventListener('timeupdate', function() {
        updateSubtitles(this.currentTime);
    });
}

function updateSubtitles(currentTime) {
    if (subtitles.length === 0) return;
    
    const index = subtitles.findIndex(seg => 
        currentTime >= seg.start && currentTime <= seg.end
    );
    
    if (index !== currentSubtitleIndex) {
        currentSubtitleIndex = index;
        
        if (index >= 0) {
            const seg = subtitles[index];
            document.getElementById('subtitleOriginal').textContent = seg.text || '';
            document.getElementById('subtitleTranslation').textContent = seg.translation || '';
        } else {
            document.getElementById('subtitleOriginal').textContent = '';
            document.getElementById('subtitleTranslation').textContent = '';
        }
    }
}

function seekToTime(time) {
    const videoPlayer = document.getElementById('videoPlayer');
    videoPlayer.currentTime = time;
    videoPlayer.play();
}

/**
 * ✅ FIXED: Show vocabulary detail với ĐẦY ĐỦ thông tin
 */
function showVocabDetail(vocabId) {
    console.log('📖 Opening vocab detail for ID:', vocabId);
    console.log('📖 Available vocabularies:', vocabularies.length);
    
    // Find vocabulary by ID
    const vocab = vocabularies.find(v => v.vocab_id === vocabId);
    
    if (!vocab) {
        console.error('❌ Vocabulary not found:', vocabId);
        showNotification('Không tìm thấy từ vựng', 'error');
        return;
    }
    
    console.log('✅ Found vocab:', vocab);
    
    const modal = document.getElementById('vocabModal');
    
    // Set word
    document.getElementById('vocabWord').textContent = vocab.word;
    
    // ✅ Build details HTML với TẤT CẢ thông tin
    let detailsHTML = `
        <div class="vocab-detail-item">
            <div class="vocab-detail-label">Nghĩa:</div>
            <div class="vocab-detail-value">${escapeHtml(vocab.translation)}</div>
        </div>
    `;
    
    // Pronunciation
    if (vocab.pronunciation) {
        detailsHTML += `
            <div class="vocab-detail-item">
                <div class="vocab-detail-label">Phát âm:</div>
                <div class="vocab-detail-value">${escapeHtml(vocab.pronunciation)}</div>
            </div>
        `;
    }
    
    // Part of speech
    if (vocab.part_of_speech) {
        detailsHTML += `
            <div class="vocab-detail-item">
                <div class="vocab-detail-label">Từ loại:</div>
                <div class="vocab-detail-value">${escapeHtml(vocab.part_of_speech)}</div>
            </div>
        `;
    }
    
    // Difficulty level
    if (vocab.difficulty_level) {
        detailsHTML += `
            <div class="vocab-detail-item">
                <div class="vocab-detail-label">Cấp độ:</div>
                <div class="vocab-detail-value">${escapeHtml(vocab.difficulty_level)}</div>
            </div>
        `;
    }
    
    // Example sentence
    if (vocab.example_sentence) {
        detailsHTML += `
            <div class="vocab-detail-item">
                <div class="vocab-detail-label">Ví dụ:</div>
                <div class="vocab-example-box">
                    <div class="example-en">${escapeHtml(vocab.example_sentence)}</div>
                    ${vocab.example_translation ? `<div class="example-vi">${escapeHtml(vocab.example_translation)}</div>` : ''}
                </div>
            </div>
        `;
    }
    
    document.getElementById('vocabDetails').innerHTML = detailsHTML;
    
    modal.classList.add('show');
}

function closeVocabModal() {
    document.getElementById('vocabModal').classList.remove('show');
}

async function downloadSubtitle() {
    try {
        const token = Storage.getToken();
        
        const response = await fetch(
            `${CONFIG.API_BASE_URL}/subtitles/${currentVideoId}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        
        if (!response.ok) {
            showNotification('Không thể tải phụ đề', 'error');
            return;
        }
        
        const data = await response.json();
        
        if (data.success && data.data.subtitles.length > 0) {
            const subtitle = data.data.subtitles[0];
            
            if (subtitle.file_path) {
                window.open(
                    `${CONFIG.API_BASE_URL}/subtitles/download/${subtitle.subtitle_id}`,
                    '_blank'
                );
            }
        }
        
    } catch (error) {
        console.error('Download subtitle error:', error);
        showNotification('Lỗi khi tải phụ đề', 'error');
    }
}