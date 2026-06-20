/**
 * 马赛克去除工具 - 前端交互逻辑
 */

// 全局变量
let currentFileId = null;
let currentOutputFilename = null;

// DOM 元素
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const previewSection = document.getElementById('previewSection');
const originalImage = document.getElementById('originalImage');
const originalInfo = document.getElementById('originalInfo');
const processBtn = document.getElementById('processBtn');
const resetBtn = document.getElementById('resetBtn');
const resultBox = document.getElementById('resultBox');
const resultImage = document.getElementById('resultImage');
const resultInfo = document.getElementById('resultInfo');
const downloadBtn = document.getElementById('downloadBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');

// 初始化事件监听
document.addEventListener('DOMContentLoaded', () => {
    initUploadArea();
    initButtons();
    initClipboardPaste();
    initFormatSelector();
});

/**
 * 初始化上传区域
 */
function initUploadArea() {
    // 点击上传
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // 文件选择
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // 拖拽上传
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
}

/**
 * 初始化按钮
 */
function initButtons() {
    processBtn.addEventListener('click', startProcessing);
    resetBtn.addEventListener('click', resetUpload);
    downloadBtn.addEventListener('click', downloadResult);
}

/**
 * 初始化剪贴板粘贴支持
 */
function initClipboardPaste() {
    document.addEventListener('paste', (e) => {
        const items = e.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const file = items[i].getAsFile();
                if (file) {
                    handleFile(file);
                    break;
                }
            }
        }
    });
}

/**
 * 初始化输出格式选择
 */
function initFormatSelector() {
    const formatSelect = document.getElementById('formatSelect');
    const qualityGroup = document.getElementById('qualityGroup');
    const qualitySlider = document.getElementById('qualitySlider');
    const qualityValue = document.getElementById('qualityValue');

    // 格式切换时显示/隐藏质量滑块
    formatSelect.addEventListener('change', () => {
        const format = formatSelect.value;
        if (format === 'jpeg' || format === 'webp') {
            qualityGroup.style.display = 'block';
        } else {
            qualityGroup.style.display = 'none';
        }
    });

    // 质量滑块值更新
    qualitySlider.addEventListener('input', () => {
        qualityValue.textContent = qualitySlider.value;
    });
}

/**
 * 处理上传的文件
 */
async function handleFile(file) {
    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showError('不支持的文件格式，请上传 JPG, PNG, BMP 或 WebP 格式的图片');
        return;
    }

    // 验证文件大小 (50MB)
    if (file.size > 50 * 1024 * 1024) {
        showError('文件过大，最大支持 50MB');
        return;
    }

    try {
        // 上传文件
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!result.success) {
            showError(result.detail || '上传失败');
            return;
        }

        currentFileId = result.file_id;

        // 显示预览
        const reader = new FileReader();
        reader.onload = (e) => {
            originalImage.src = e.target.result;
            originalInfo.textContent = `${file.name} (${formatFileSize(file.size)})`;
            previewSection.style.display = 'block';
            previewSection.classList.add('fade-in');
            processBtn.disabled = false;
        };
        reader.readAsDataURL(file);

    } catch (error) {
        showError('上传失败: ' + error.message);
    }
}

/**
 * 开始处理图像
 */
async function startProcessing() {
    if (!currentFileId) {
        showError('请先上传图片');
        return;
    }

    // 获取处理选项
    const mode = document.querySelector('input[name="mode"]:checked').value;
    const faceEnhance = document.getElementById('faceEnhance').checked;
    const scale = parseInt(document.getElementById('scaleSelect').value);
    const outputFormat = document.getElementById('formatSelect').value;
    const jpegQuality = parseInt(document.getElementById('qualitySlider').value);

    // 显示进度
    showProgress('正在处理，请稍候...');

    // 禁用按钮
    processBtn.disabled = true;
    processBtn.querySelector('.btn-text').style.display = 'none';
    processBtn.querySelector('.btn-loading').style.display = 'inline-flex';

    try {
        // 模拟进度
        simulateProgress();

        // 发送处理请求
        const formData = new FormData();
        formData.append('file_id', currentFileId);
        formData.append('mode', mode);
        formData.append('face_enhance', faceEnhance);
        formData.append('scale', scale);
        formData.append('output_format', outputFormat);
        formData.append('jpeg_quality', jpegQuality);

        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        // 隐藏进度
        hideProgress();

        if (!result.success) {
            showError(result.detail || '处理失败');
            resetProcessButton();
            return;
        }

        // 显示结果
        currentOutputFilename = result.output_filename;
        showResult(result);

    } catch (error) {
        hideProgress();
        showError('处理失败: ' + error.message);
        resetProcessButton();
    }
}

/**
 * 显示处理结果
 */
function showResult(result) {
    // 加载结果图片
    resultImage.src = `/api/download/${result.output_filename}`;

    // 构建结果信息
    let infoText = `原图: ${result.original_size} → 处理后: ${result.processed_size}`;

    // 添加处理时间
    if (result.processing_time_ms !== undefined) {
        infoText += ` | 耗时: ${formatTime(result.processing_time_ms)}`;
    }

    resultInfo.textContent = infoText;

    // 显示点击提示
    if (!document.querySelector('.click-hint')) {
        const hint = document.createElement('p');
        hint.className = 'click-hint';
        hint.textContent = '💡 点击图片可放大查看';
        resultInfo.parentNode.insertBefore(hint, resultInfo.nextSibling);
    }

    // 显示结果框
    resultBox.style.display = 'block';
    resultBox.classList.add('fade-in');

    // 重置按钮状态
    resetProcessButton();

    // 滚动到结果区域
    resultBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * 重置处理按钮
 */
function resetProcessButton() {
    processBtn.disabled = false;
    processBtn.querySelector('.btn-text').style.display = 'inline';
    processBtn.querySelector('.btn-loading').style.display = 'none';
}

/**
 * 下载处理结果
 */
function downloadResult() {
    if (!currentOutputFilename) {
        showError('没有可下载的结果');
        return;
    }

    const link = document.createElement('a');
    link.href = `/api/download/${currentOutputFilename}`;
    link.download = currentOutputFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * 重置上传
 */
function resetUpload() {
    currentFileId = null;
    currentOutputFilename = null;
    fileInput.value = '';
    previewSection.style.display = 'none';
    resultBox.style.display = 'none';
    processBtn.disabled = true;
    hideProgress();
}

/**
 * 显示进度
 */
function showProgress(text) {
    progressText.textContent = text;
    progressSection.style.display = 'block';
    progressSection.classList.add('fade-in');
    progressFill.style.width = '0%';
}

/**
 * 隐藏进度
 */
function hideProgress() {
    progressSection.style.display = 'none';
}

/**
 * 模拟进度
 */
function simulateProgress() {
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) {
            progress = 90;
            clearInterval(interval);
        }
        progressFill.style.width = progress + '%';
    }, 500);

    // 在请求完成后清除 interval
    window.addEventListener('load', () => clearInterval(interval));
}

/**
 * 显示错误信息
 */
function showError(message) {
    // 移除已有的错误提示
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }

    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;

    // 插入到合适的位置
    const container = document.querySelector('.main-content');
    container.appendChild(errorDiv);

    // 3秒后自动消失
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 格式化时间（毫秒转可读格式）
 */
function formatTime(ms) {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
}

// 图片放大模态框功能
const imageModal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const modalClose = document.getElementById('modalClose');

function openModal(src) {
    modalImage.src = src;
    imageModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    imageModal.style.display = 'none';
    document.body.style.overflow = '';
}

// 点击关闭按钮关闭模态框
modalClose.addEventListener('click', closeModal);

// 点击模态框背景关闭
imageModal.addEventListener('click', (e) => {
    if (e.target === imageModal) {
        closeModal();
    }
});

// ESC键关闭模态框
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && imageModal.style.display === 'flex') {
        closeModal();
    }
});

// 给图片添加点击放大功能
function initImageZoom() {
    const originalImg = document.getElementById('originalImage');
    const resultImg = document.getElementById('resultImage');

    originalImg.addEventListener('click', () => {
        if (originalImg.src) openModal(originalImg.src);
    });

    resultImg.addEventListener('click', () => {
        if (resultImg.src && !resultImg.src.includes('data:,')) {
            openModal(resultImg.src);
        }
    });
}

// 初始化图片放大功能
document.addEventListener('DOMContentLoaded', initImageZoom);
