// ==================== Load Languages ====================
async function loadLanguages() {
    try {
        const response = await fetch('/api/language-groups');
        const data = await response.json();
        const langSelect = elements.langSelect;
        if (langSelect) {
            langSelect.innerHTML = '';
            for (const [groupName, languages] of Object.entries(data.groups)) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = groupName;
                for (const lang of languages) {
                    const option = document.createElement('option');
                    option.value = lang.code;
                    option.textContent = lang.name;
                    if (lang.code === 'en') option.selected = true;
                    optgroup.appendChild(option);
                }
                langSelect.appendChild(optgroup);
            }
            console.log('Loaded ' + data.total_count + ' languages');
        }
    } catch (error) {
        console.error('Failed to load languages:', error);
    }
}

// ==================== Load Languages ====================
async function loadLanguages() {
    try {
        const response = await fetch('/api/language-groups');
        const data = await response.json();
        const langSelect = elements.langSelect;
        if (langSelect) {
            langSelect.innerHTML = '';
            for (const [groupName, languages] of Object.entries(data.groups)) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = groupName;
                for (const lang of languages) {
                    const option = document.createElement('option');
                    option.value = lang.code;
                    option.textContent = lang.name;
                    if (lang.code === 'en') option.selected = true;
                    optgroup.appendChild(option);
                }
                langSelect.appendChild(optgroup);
            }
            console.log('Loaded ' + data.total_count + ' languages');
        }
    } catch (error) {
        console.error('Failed to load languages:', error);
    }
}

// ==================== Load Languages ====================
async function loadLanguages() {
    try {
        const response = await fetch('/api/language-groups');
        const data = await response.json();
        
        // Populate the language select with optgroups
        const langSelect = elements.langSelect;
        if (langSelect) {
            langSelect.innerHTML = '';
            
            for (const [groupName, languages] of Object.entries(data.groups)) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = groupName;
                
                for (const lang of languages) {
                    const option = document.createElement('option');
                    option.value = lang.code;
                    option.textContent = lang.name;
                    if (lang.code === 'en') option.selected = true;
                    optgroup.appendChild(option);
                }
                
                langSelect.appendChild(optgroup);
            }
            
            console.log('Loaded ' + data.total_count + ' languages');
        }
    } catch (error) {
        console.error('Failed to load languages:', error);
    }
}
/**
 * PaddleOCR Studio - Frontend Application
 * Handles image upload, OCR processing, and model management
 */

// ==================== State ====================
const state = {
    currentImage: null,
    originalImage: null,
    ocrResults: null,
    structureResults: null,
    vlResults: null,
    structureImage: null,
    vlImage: null,
    models: [],
    isProcessing: false
};

// ==================== DOM Elements ====================
const elements = {
    // Tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),

    // Upload
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    imagePreview: document.getElementById('image-preview'),
    previewCanvas: document.getElementById('preview-canvas'),
    imageInfo: document.getElementById('image-info'),
    clearBtn: document.getElementById('clear-btn'),
    controlsSection: document.getElementById('controls-section'),

    // Controls
    brightness: document.getElementById('brightness'),
    contrast: document.getElementById('contrast'),
    saturation: document.getElementById('saturation'),
    sharpness: document.getElementById('sharpness'),
    brightnessValue: document.getElementById('brightness-value'),
    contrastValue: document.getElementById('contrast-value'),
    saturationValue: document.getElementById('saturation-value'),
    sharpnessValue: document.getElementById('sharpness-value'),
    resetAdjustments: document.getElementById('reset-adjustments'),

    // OCR
    langSelect: document.getElementById('lang-select'),
    versionSelect: document.getElementById('version-select'),
    ocrBtn: document.getElementById('ocr-btn'),
    ocrProgress: document.getElementById('ocr-progress'),

    // Results
    resultsEmpty: document.getElementById('results-empty'),
    resultsData: document.getElementById('results-data'),
    resultTabs: document.querySelectorAll('.result-tab'),
    textOutput: document.getElementById('text-output'),
    boxesList: document.getElementById('boxes-list'),
    jsonOutput: document.getElementById('json-output'),
    copyBtn: document.getElementById('copy-btn'),
    downloadBtn: document.getElementById('download-btn'),

    // Models
    modelsGrid: document.getElementById('models-grid'),
    installedCount: document.getElementById('installed-count'),
    diskUsage: document.getElementById('disk-usage'),
    filterBtns: document.querySelectorAll('.filter-btn'),

    // Toast
    toastContainer: document.getElementById('toast-container')
};

// ==================== Tab Navigation ====================
function initTabs() {
    elements.tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            // Update buttons
            elements.tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update content
            elements.tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-tab`) {
                    content.classList.add('active');
                }
            });

            // Load models when switching to models tab
            if (tabId === 'models') {
                loadModels();
            }
        });
    });
}

// ==================== Image Upload ====================
function initUpload() {
    const dropZone = elements.dropZone;
    const fileInput = elements.fileInput;

    // Browse link click
    dropZone.querySelector('.browse-link').addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    dropZone.addEventListener('click', () => fileInput.click());

    // Drag & drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Clear button
    elements.clearBtn.addEventListener('click', clearImage);
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showToast('Please upload an image file', 'error');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        loadImage(e.target.result, file.name);
    };
    reader.readAsDataURL(file);
}

function loadImage(dataUrl, filename = 'image') {
    const img = new Image();
    img.onload = () => {
        state.originalImage = dataUrl;
        state.currentImage = dataUrl;

        // Show preview
        elements.dropZone.style.display = 'none';
        elements.imagePreview.style.display = 'block';
        elements.controlsSection.style.display = 'block';

        // Draw to canvas
        drawImageToCanvas(img);

        // Update info
        elements.imageInfo.textContent = `${filename} â€¢ ${img.width} Ã— ${img.height}`;

        // Enable buttons
        elements.clearBtn.disabled = false;
        elements.ocrBtn.disabled = false;

        // Reset adjustments
        resetAdjustments();
    };
    img.src = dataUrl;
}

function drawImageToCanvas(img, boxes = null) {
    const canvas = elements.previewCanvas;
    const ctx = canvas.getContext('2d');

    // Set canvas size to match container while maintaining aspect ratio
    const container = elements.imagePreview;
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight - 40; // Account for info bar

    const scale = Math.min(containerWidth / img.width, containerHeight / img.height);
    canvas.width = img.width * scale;
    canvas.height = img.height * scale;

    // Apply CSS filters based on adjustments
    const brightness = elements.brightness.value / 100;
    const contrast = elements.contrast.value / 100;
    const saturation = elements.saturation.value / 100;

    ctx.filter = `brightness(${brightness}) contrast(${contrast}) saturate(${saturation})`;
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    ctx.filter = 'none';

    // Draw bounding boxes if available
    if (boxes && boxes.length > 0) {
        ctx.strokeStyle = '#6366f1';
        ctx.lineWidth = 2;
        ctx.font = '12px Inter, sans-serif';
        ctx.fillStyle = 'rgba(99, 102, 241, 0.8)';

        boxes.forEach((box, index) => {
            if (box.points && box.points.length >= 4) {
                const points = box.points.map(p => [
                    p[0] * scale,
                    p[1] * scale
                ]);

                ctx.beginPath();
                ctx.moveTo(points[0][0], points[0][1]);
                for (let i = 1; i < points.length; i++) {
                    ctx.lineTo(points[i][0], points[i][1]);
                }
                ctx.closePath();
                ctx.stroke();
            }
        });
    }
}

function clearImage() {
    state.originalImage = null;
    state.currentImage = null;
    state.ocrResults = null;

    elements.dropZone.style.display = 'flex';
    elements.imagePreview.style.display = 'none';
    elements.controlsSection.style.display = 'none';

    elements.clearBtn.disabled = true;
    elements.ocrBtn.disabled = true;
    elements.copyBtn.disabled = true;
    elements.downloadBtn.disabled = true;

    elements.resultsEmpty.style.display = 'flex';
    elements.resultsData.style.display = 'none';

    elements.fileInput.value = '';
    resetAdjustments();
}

// ==================== Image Adjustments ====================
function initAdjustments() {
    const controls = [
        { input: elements.brightness, display: elements.brightnessValue },
        { input: elements.contrast, display: elements.contrastValue },
        { input: elements.saturation, display: elements.saturationValue },
        { input: elements.sharpness, display: elements.sharpnessValue }
    ];

    controls.forEach(({ input, display }) => {
        input.addEventListener('input', () => {
            display.textContent = `${input.value}%`;
            updatePreview();
        });
    });

    elements.resetAdjustments.addEventListener('click', resetAdjustments);
}

function resetAdjustments() {
    elements.brightness.value = 100;
    elements.contrast.value = 100;
    elements.saturation.value = 100;
    elements.sharpness.value = 100;

    elements.brightnessValue.textContent = '100%';
    elements.contrastValue.textContent = '100%';
    elements.saturationValue.textContent = '100%';
    elements.sharpnessValue.textContent = '100%';

    updatePreview();
}

function updatePreview() {
    if (!state.originalImage) return;

    const img = new Image();
    img.onload = () => {
        drawImageToCanvas(img, state.ocrResults?.boxes);
    };
    img.src = state.originalImage;
}

// ==================== OCR Processing ====================
function initOCR() {
    elements.ocrBtn.addEventListener('click', runOCR);
}

async function runOCR() {
    if (!state.currentImage || state.isProcessing) return;

    state.isProcessing = true;
    elements.ocrBtn.disabled = true;
    elements.ocrProgress.style.display = 'flex';

    try {
        const formData = new FormData();

        // Convert base64 to blob
        const response = await fetch(state.originalImage);
        const blob = await response.blob();
        formData.append('file', blob, 'image.png');

        // Add parameters
        formData.append('lang', elements.langSelect.value);
        formData.append('version', elements.versionSelect.value);
        formData.append('brightness', elements.brightness.value / 100);
        formData.append('contrast', elements.contrast.value / 100);
        formData.append('saturation', elements.saturation.value / 100);
        formData.append('sharpness', elements.sharpness.value / 100);

        const result = await fetch('/api/ocr', {
            method: 'POST',
            body: formData
        });

        if (!result.ok) {
            const error = await result.json();
            throw new Error(error.error || 'OCR failed');
        }

        const data = await result.json();
        displayResults(data);

        showToast('OCR completed successfully', 'success');

    } catch (error) {
        console.error('OCR error:', error);
        showToast(error.message || 'OCR failed', 'error');
    } finally {
        state.isProcessing = false;
        elements.ocrBtn.disabled = false;
        elements.ocrProgress.style.display = 'none';
    }
}

function displayResults(data) {
    state.ocrResults = data;

    // Update preview with boxes
    if (state.originalImage) {
        const img = new Image();
        img.onload = () => {
            drawImageToCanvas(img, data.boxes);
        };
        img.src = state.originalImage;
    }

    // Show results
    elements.resultsEmpty.style.display = 'none';
    elements.resultsData.style.display = 'flex';

    // Text output
    elements.textOutput.textContent = data.full_text || 'No text detected';

    // Boxes list
    elements.boxesList.innerHTML = data.boxes.map((box, i) => `
        <div class="box-item">
            <div class="box-text">${box.text || 'N/A'}</div>
            <div class="box-confidence">Confidence: ${(box.confidence * 100).toFixed(1)}%</div>
        </div>
    `).join('');

    // JSON output
    elements.jsonOutput.textContent = JSON.stringify(data, null, 2);

    // Enable buttons
    elements.copyBtn.disabled = false;
    elements.downloadBtn.disabled = false;
}

// ==================== Result Tabs ====================
function initResultTabs() {
    elements.resultTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const resultType = tab.dataset.result;

            elements.resultTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            document.querySelectorAll('.result-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${resultType}-result`).classList.add('active');
        });
    });

    // Copy button
    elements.copyBtn.addEventListener('click', () => {
        if (state.ocrResults) {
            navigator.clipboard.writeText(state.ocrResults.full_text)
                .then(() => showToast('Text copied to clipboard', 'success'))
                .catch(() => showToast('Failed to copy text', 'error'));
        }
    });

    // Download button
    elements.downloadBtn.addEventListener('click', () => {
        if (state.ocrResults) {
            const blob = new Blob([JSON.stringify(state.ocrResults, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'ocr-results.json';
            a.click();
            URL.revokeObjectURL(url);
            showToast('JSON downloaded', 'success');
        }
    });
}

// ==================== Model Management ====================
function initModels() {
    elements.filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            elements.filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterModels(btn.dataset.filter);
        });
    });
}

async function loadModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();

        state.models = data.models;

        // Update stats
        const installedCount = state.models.filter(m => m.installed).length;
        elements.installedCount.textContent = installedCount;
        elements.diskUsage.textContent = `${data.disk_usage_mb} MB`;

        renderModels(state.models);

    } catch (error) {
        console.error('Failed to load models:', error);
        elements.modelsGrid.innerHTML = `
            <div class="loading-models">
                <span style="color: var(--error);">Failed to load models</span>
            </div>
        `;
    }
}

function filterModels(filter) {
    let filtered = state.models;

    if (filter === 'installed') {
        filtered = state.models.filter(m => m.installed);
    } else if (filter !== 'all') {
        filtered = state.models.filter(m => m.type === filter);
    }

    renderModels(filtered);
}

function renderModels(models) {
    if (models.length === 0) {
        elements.modelsGrid.innerHTML = `
            <div class="loading-models">
                <span>No models found</span>
            </div>
        `;
        return;
    }

    elements.modelsGrid.innerHTML = models.map(model => `
        <div class="model-card ${model.installed ? 'installed' : ''}" data-model-id="${model.id}">
            <div class="model-card-header">
                <h3>${model.name}</h3>
                <span class="model-badge ${model.type}">${model.type}</span>
            </div>
            <div class="model-card-meta">
                <span>v${model.version}</span>
                <span>${model.size_mb} MB</span>
                ${model.language ? `<span>${model.language}</span>` : ''}
            </div>
            <div class="model-card-actions">
                ${model.installed ? `
                    <button class="btn btn-success btn-sm" disabled>
                        âœ“ Installed
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteModel('${model.id}')">
                        Delete
                    </button>
                ` : `
                    <button class="btn btn-primary btn-sm" onclick="downloadModel('${model.id}')">
                        Download
                    </button>
                `}
            </div>
        </div>
    `).join('');
}

async function downloadModel(modelId) {
    const card = document.querySelector(`[data-model-id="${modelId}"]`);
    const actionsDiv = card.querySelector('.model-card-actions');

    actionsDiv.innerHTML = `
        <div class="ocr-progress" style="display: flex;">
            <div class="spinner"></div>
            <span>Downloading...</span>
        </div>
    `;

    try {
        const response = await fetch(`/api/models/${modelId}/download`, {
            method: 'POST'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Download failed');
        }

        showToast(`Model ${modelId} downloaded successfully`, 'success');
        loadModels(); // Refresh list

    } catch (error) {
        console.error('Download error:', error);
        showToast(error.message || 'Download failed', 'error');
        loadModels(); // Refresh to restore buttons
    }
}

async function deleteModel(modelId) {
    if (!confirm(`Are you sure you want to delete ${modelId}?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/models/${modelId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Delete failed');
        }

        showToast(`Model ${modelId} deleted`, 'success');
        loadModels(); // Refresh list

    } catch (error) {
        console.error('Delete error:', error);
        showToast(error.message || 'Delete failed', 'error');
    }
}

// Make functions available globally for onclick handlers
window.downloadModel = downloadModel;
window.deleteModel = deleteModel;

// ==================== Toast Notifications ====================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== Initialize ====================
document.addEventListener('DOMContentLoaded', () => {
    loadLanguages();
    loadLanguages();
    initTabs();
    initUpload();
    initAdjustments();
    initOCR();
    initResultTabs();
    initModels();
    initStructure();
    initVL();

    console.log('PaddleOCR Studio initialized');
});

// ==================== Structure Mode ====================
function initStructure() {
    const dropZone = document.getElementById('structure-drop-zone');
    const fileInput = document.getElementById('structure-file-input');
    const clearBtn = document.getElementById('structure-clear-btn');
    const structureBtn = document.getElementById('structure-btn');

    if (!dropZone || !fileInput) return;

    // Browse link click
    const browseLink = dropZone.querySelector('.browse-link');
    if (browseLink) {
        browseLink.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    dropZone.addEventListener('click', () => fileInput.click());

    // Drag & drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleStructureFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleStructureFile(e.target.files[0]);
        }
    });

    if (clearBtn) {
        clearBtn.addEventListener('click', clearStructure);
    }

    if (structureBtn) {
        structureBtn.addEventListener('click', runStructure);
    }

    // Structure result tabs
    document.querySelectorAll('[data-structure-result]').forEach(tab => {
        tab.addEventListener('click', () => {
            const resultType = tab.dataset.structureResult;

            document.querySelectorAll('[data-structure-result]').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            document.querySelectorAll('#structure-results .result-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${resultType}-result`)?.classList.add('active');
        });
    });
}

function handleStructureFile(file) {
    if (!file.type.startsWith('image/')) {
        showToast('Please upload an image file', 'error');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        loadStructureImage(e.target.result, file.name);
    };
    reader.readAsDataURL(file);
}

function loadStructureImage(dataUrl, filename = 'document') {
    const img = new Image();
    img.onload = () => {
        state.structureImage = dataUrl;

        const dropZone = document.getElementById('structure-drop-zone');
        const preview = document.getElementById('structure-preview');
        const canvas = document.getElementById('structure-canvas');
        const info = document.getElementById('structure-info');
        const legend = document.getElementById('layout-legend');
        const clearBtn = document.getElementById('structure-clear-btn');
        const structureBtn = document.getElementById('structure-btn');

        if (dropZone) dropZone.style.display = 'none';
        if (preview) preview.style.display = 'block';
        if (legend) legend.style.display = 'block';

        // Draw to canvas
        if (canvas) {
            const ctx = canvas.getContext('2d');
            const container = preview;
            const containerWidth = container.clientWidth;
            const containerHeight = container.clientHeight - 40;

            const scale = Math.min(containerWidth / img.width, containerHeight / img.height);
            canvas.width = img.width * scale;
            canvas.height = img.height * scale;

            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        }

        if (info) info.textContent = `${filename} â€¢ ${img.width} Ã— ${img.height}`;
        if (clearBtn) clearBtn.disabled = false;
        if (structureBtn) structureBtn.disabled = false;
    };
    img.src = dataUrl;
}

function clearStructure() {
    state.structureImage = null;
    state.structureResults = null;

    const dropZone = document.getElementById('structure-drop-zone');
    const preview = document.getElementById('structure-preview');
    const legend = document.getElementById('layout-legend');
    const fileInput = document.getElementById('structure-file-input');
    const clearBtn = document.getElementById('structure-clear-btn');
    const structureBtn = document.getElementById('structure-btn');
    const resultsEmpty = document.getElementById('structure-results-empty');
    const results = document.getElementById('structure-results');

    if (dropZone) dropZone.style.display = 'flex';
    if (preview) preview.style.display = 'none';
    if (legend) legend.style.display = 'none';
    if (fileInput) fileInput.value = '';
    if (clearBtn) clearBtn.disabled = true;
    if (structureBtn) structureBtn.disabled = true;
    if (resultsEmpty) resultsEmpty.style.display = 'flex';
    if (results) results.style.display = 'none';
}

async function runStructure() {
    if (!state.structureImage || state.isProcessing) return;

    state.isProcessing = true;
    const structureBtn = document.getElementById('structure-btn');
    const progress = document.getElementById('structure-progress');

    if (structureBtn) structureBtn.disabled = true;
    if (progress) progress.style.display = 'flex';

    try {
        const formData = new FormData();

        const response = await fetch(state.structureImage);
        const blob = await response.blob();
        formData.append('file', blob, 'document.png');

        const langSelect = document.getElementById('structure-lang-select');
        if (langSelect) {
            formData.append('lang', langSelect.value);
        }

        const result = await fetch('/api/structure', {
            method: 'POST',
            body: formData
        });

        if (!result.ok) {
            const error = await result.json();
            throw new Error(error.error || 'Structure parsing failed');
        }

        const data = await result.json();
        displayStructureResults(data);

        showToast('Document parsed successfully', 'success');

    } catch (error) {
        console.error('Structure error:', error);
        showToast(error.message || 'Structure parsing failed', 'error');
    } finally {
        state.isProcessing = false;
        if (structureBtn) structureBtn.disabled = false;
        if (progress) progress.style.display = 'none';
    }
}

function displayStructureResults(data) {
    state.structureResults = data;

    const resultsEmpty = document.getElementById('structure-results-empty');
    const results = document.getElementById('structure-results');
    const markdownOutput = document.getElementById('markdown-output');
    const tablesOutput = document.getElementById('tables-output');
    const formulasOutput = document.getElementById('formulas-output');
    const jsonOutput = document.getElementById('structure-json-output');
    const exportMdBtn = document.getElementById('export-md-btn');
    const exportJsonBtn = document.getElementById('export-json-btn');

    if (resultsEmpty) resultsEmpty.style.display = 'none';
    if (results) results.style.display = 'flex';

    // Markdown output
    if (markdownOutput) {
        markdownOutput.innerHTML = data.markdown ?
            `<pre style="white-space: pre-wrap;">${escapeHtml(data.markdown)}</pre>` :
            '<p>No markdown output</p>';
    }

    // Tables output
    if (tablesOutput) {
        if (data.tables && data.tables.length > 0) {
            tablesOutput.innerHTML = data.tables.map((table, i) => `
                <div class="table-item">
                    <h4>Table ${i + 1}</h4>
                    <div class="table-html">${table.html || 'No HTML'}</div>
                </div>
            `).join('');
        } else {
            tablesOutput.innerHTML = '<p>No tables detected</p>';
        }
    }

    // Formulas output
    if (formulasOutput) {
        if (data.formulas && data.formulas.length > 0) {
            formulasOutput.innerHTML = data.formulas.map((formula, i) => `
                <div class="formula-item">
                    <h4>Formula ${i + 1}</h4>
                    <code>${escapeHtml(formula.latex || 'No LaTeX')}</code>
                </div>
            `).join('');
        } else {
            formulasOutput.innerHTML = '<p>No formulas detected</p>';
        }
    }

    // JSON output
    if (jsonOutput) {
        jsonOutput.textContent = JSON.stringify(data, null, 2);
    }

    if (exportMdBtn) exportMdBtn.disabled = false;
    if (exportJsonBtn) exportJsonBtn.disabled = false;
}

// ==================== VL Mode ====================
function initVL() {
    const dropZone = document.getElementById('vl-drop-zone');
    const fileInput = document.getElementById('vl-file-input');
    const clearBtn = document.getElementById('vl-clear-btn');
    const vlBtn = document.getElementById('vl-btn');

    if (!dropZone || !fileInput) return;

    const browseLink = dropZone.querySelector('.browse-link');
    if (browseLink) {
        browseLink.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleVLFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleVLFile(e.target.files[0]);
        }
    });

    if (clearBtn) {
        clearBtn.addEventListener('click', clearVL);
    }

    if (vlBtn) {
        vlBtn.addEventListener('click', runVL);
    }

    // VL result tabs
    document.querySelectorAll('[data-vl-result]').forEach(tab => {
        tab.addEventListener('click', () => {
            const resultType = tab.dataset.vlResult;

            document.querySelectorAll('[data-vl-result]').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            document.querySelectorAll('#vl-results .result-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`vl-${resultType}-result`)?.classList.add('active');
        });
    });
}

function handleVLFile(file) {
    if (!file.type.startsWith('image/')) {
        showToast('Please upload an image file', 'error');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        loadVLImage(e.target.result, file.name);
    };
    reader.readAsDataURL(file);
}

function loadVLImage(dataUrl, filename = 'image') {
    const img = new Image();
    img.onload = () => {
        state.vlImage = dataUrl;

        const dropZone = document.getElementById('vl-drop-zone');
        const preview = document.getElementById('vl-preview');
        const canvas = document.getElementById('vl-canvas');
        const info = document.getElementById('vl-info');
        const clearBtn = document.getElementById('vl-clear-btn');
        const vlBtn = document.getElementById('vl-btn');

        if (dropZone) dropZone.style.display = 'none';
        if (preview) preview.style.display = 'block';

        if (canvas) {
            const ctx = canvas.getContext('2d');
            const container = preview;
            const containerWidth = container.clientWidth;
            const containerHeight = container.clientHeight - 40;

            const scale = Math.min(containerWidth / img.width, containerHeight / img.height);
            canvas.width = img.width * scale;
            canvas.height = img.height * scale;

            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        }

        if (info) info.textContent = `${filename} â€¢ ${img.width} Ã— ${img.height}`;
        if (clearBtn) clearBtn.disabled = false;
        if (vlBtn) vlBtn.disabled = false;
    };
    img.src = dataUrl;
}

function clearVL() {
    state.vlImage = null;
    state.vlResults = null;

    const dropZone = document.getElementById('vl-drop-zone');
    const preview = document.getElementById('vl-preview');
    const fileInput = document.getElementById('vl-file-input');
    const clearBtn = document.getElementById('vl-clear-btn');
    const vlBtn = document.getElementById('vl-btn');
    const resultsEmpty = document.getElementById('vl-results-empty');
    const results = document.getElementById('vl-results');

    if (dropZone) dropZone.style.display = 'flex';
    if (preview) preview.style.display = 'none';
    if (fileInput) fileInput.value = '';
    if (clearBtn) clearBtn.disabled = true;
    if (vlBtn) vlBtn.disabled = true;
    if (resultsEmpty) resultsEmpty.style.display = 'flex';
    if (results) results.style.display = 'none';
}

async function runVL() {
    if (!state.vlImage || state.isProcessing) return;

    state.isProcessing = true;
    const vlBtn = document.getElementById('vl-btn');
    const progress = document.getElementById('vl-progress');

    if (vlBtn) vlBtn.disabled = true;
    if (progress) progress.style.display = 'flex';

    try {
        const formData = new FormData();

        const response = await fetch(state.vlImage);
        const blob = await response.blob();
        formData.append('file', blob, 'image.png');

        const result = await fetch('/api/vl', {
            method: 'POST',
            body: formData
        });

        if (!result.ok) {
            const error = await result.json();
            throw new Error(error.error || 'VL parsing failed');
        }

        const data = await result.json();
        displayVLResults(data);

        showToast('VL parsing completed', 'success');

    } catch (error) {
        console.error('VL error:', error);
        showToast(error.message || 'VL parsing failed', 'error');
    } finally {
        state.isProcessing = false;
        if (vlBtn) vlBtn.disabled = false;
        if (progress) progress.style.display = 'none';
    }
}

function displayVLResults(data) {
    state.vlResults = data;

    const resultsEmpty = document.getElementById('vl-results-empty');
    const results = document.getElementById('vl-results');
    const textOutput = document.getElementById('vl-text-output');
    const markdownOutput = document.getElementById('vl-markdown-output');
    const jsonOutput = document.getElementById('vl-json-output');
    const exportBtn = document.getElementById('vl-export-btn');

    if (resultsEmpty) resultsEmpty.style.display = 'none';
    if (results) results.style.display = 'flex';

    if (textOutput) {
        textOutput.textContent = data.full_text || 'No text detected';
    }

    if (markdownOutput) {
        markdownOutput.innerHTML = data.markdown ?
            `<pre style="white-space: pre-wrap;">${escapeHtml(data.markdown)}</pre>` :
            '<p>No markdown output</p>';
    }

    if (jsonOutput) {
        jsonOutput.textContent = JSON.stringify(data, null, 2);
    }

    if (exportBtn) exportBtn.disabled = false;
}

// Utility function
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}



