/**
 * Upload Page JavaScript
 */

let selectedFile = null;

document.addEventListener('DOMContentLoaded', async function() {
    // Check auth
    const isAuth = await checkAuthentication();
    
    if (!isAuth) {
        window.location.href = '../auth/login.html';
        return;
    }
    
    initUpload();
});

/**
 * Check authentication
 */
async function checkAuthentication() {
    const token = Storage.getToken();
    
    if (!token) {
        return false;
    }
    
    // Verify token
    const result = await AuthAPI.verifyToken();
    
    if (!result.success) {
        Storage.logout();
        return false;
    }
    
    return true;
}

/**
 * Initialize upload page
 */
function initUpload() {
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('videoFile');
    const uploadForm = document.getElementById('uploadForm');
    
    // File input change
    fileInput.addEventListener('change', function(e) {
        handleFileSelect(e.target.files[0]);
    });
    
    // Drag and drop
    uploadBox.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadBox.classList.add('drag-over');
    });
    
    uploadBox.addEventListener('dragleave', function() {
        uploadBox.classList.remove('drag-over');
    });
    
    uploadBox.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadBox.classList.remove('drag-over');
        
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFileSelect(file);
        }
    });
    
    // Form submit
    uploadForm.addEventListener('submit', handleUpload);
}

/**
 * Handle file selection
 */
function handleFileSelect(file) {
    // Validate file
    const validation = validateVideoFile(file);
    
    if (!validation.valid) {
        alert(validation.message);
        return;
    }
    
    selectedFile = file;
    
    // Show form
    document.getElementById('uploadBox').style.display = 'none';
    document.getElementById('uploadForm').style.display = 'block';
    
    // Display file info
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    
    // Auto fill title
    const titleInput = document.getElementById('videoTitle');
    if (!titleInput.value) {
        titleInput.value = file.name.replace(/\.[^/.]+$/, '');
    }
}

/**
 * Handle upload
 */
async function handleUpload(e) {
    e.preventDefault();
    
    if (!selectedFile) {
        alert('Vui lòng chọn file');
        return;
    }
    
    const title = document.getElementById('videoTitle').value.trim();
    const sourceLanguage = document.getElementById('sourceLanguage').value;
    const targetLanguage = document.getElementById('targetLanguage').value;
    
    if (!title) {
        alert('Vui lòng nhập tiêu đề');
        return;
    }
    
    // Disable submit button
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');
    
    // Show progress
    const progressContainer = document.getElementById('uploadProgress');
    progressContainer.style.display = 'block';
    
    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('title', title);
        
        const token = Storage.getToken();
        
        // Upload with progress
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                updateProgress(percent, 'Đang upload...');
            }
        });
        
        xhr.addEventListener('load', function() {
            if (xhr.status === 201) {
                const response = JSON.parse(xhr.responseText);
                
                // Show success
                showSuccess(response.data.video);
            } else {
                throw new Error('Upload failed');
            }
        });
        
        xhr.addEventListener('error', function() {
            throw new Error('Network error');
        });
        
        xhr.open('POST', CONFIG.buildUrl(CONFIG.ENDPOINTS.VIDEO_UPLOAD));
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        xhr.send(formData);
        
    } catch (error) {
        console.error('Upload error:', error);
        alert('Lỗi khi upload video. Vui lòng thử lại.');
        
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
        progressContainer.style.display = 'none';
    }
}

/**
 * Update progress
 */
function updateProgress(percent, status) {
    document.getElementById('progressFill').style.width = percent + '%';
    document.getElementById('progressPercent').textContent = percent + '%';
    document.getElementById('progressStatus').textContent = status;
}

/**
 * Show success message
 */
function showSuccess(video) {
    document.getElementById('uploadForm').style.display = 'none';
    document.getElementById('successMessage').style.display = 'block';
}

/**
 * Remove file
 */
function removeFile() {
    selectedFile = null;
    document.getElementById('uploadBox').style.display = 'block';
    document.getElementById('uploadForm').style.display = 'none';
    document.getElementById('videoFile').value = '';
}

/**
 * Reset form
 */
function resetForm() {
    removeFile();
    document.getElementById('uploadForm').reset();
}

/**
 * Upload another video
 */
function uploadAnother() {
    document.getElementById('successMessage').style.display = 'none';
    resetForm();
}