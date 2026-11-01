// AI Resume Maker - Interactive Frontend Engine (Optimized Studio UX)

const SAMPLE_JOB_DESCRIPTION = `Job Title: Senior Full-Stack Platform Engineer
Company: CloudScale Dynamics
Location: San Francisco, CA (Hybrid / Remote)

About the Role:
We are looking for an experienced Senior Full-Stack / Platform Engineer to lead the architecture of our core distributed telemetry and automation platform. In this role, you will design resilient microservices, scale real-time event pipelines processing millions of daily transactions, and build responsive frontend dashboards.

Key Responsibilities:
- Architect and maintain highly available backend APIs and asynchronous task processing pipelines using Python (FastAPI/Django), Go, and PostgreSQL.
- Build modern, accessible data visualization dashboards using React, TypeScript, and Tailwind CSS.
- Optimize high-throughput database queries, caching layers (Redis), and event streaming (Kafka/RabbitMQ).
- Drive cloud infrastructure automation via AWS (ECS, Lambda, S3, RDS), Docker, Kubernetes, and Terraform.
- Champion engineering best practices, CI/CD pipeline automation (GitHub Actions), and system observability.

Requirements:
- 5+ years of software engineering experience building scalable cloud-native web applications.
- Strong proficiency in Python, TypeScript/JavaScript, and relational databases (PostgreSQL/MySQL).
- Hands-on experience with cloud infrastructure (AWS/GCP), containerization (Docker/Kubernetes), and microservices.
- Solid track record of measuring and improving system latency, resilience, and developer productivity.
- Excellent communication skills and passion for mentoring junior/mid-level engineers.`;

const state = {
    currentTab: 'jd', // 'jd', 'profile', 'settings', 'history'
    rightTab: 'preview', // 'preview', 'editor', 'ats', 'letter'
    theme: 'modern',
    paperSize: 'A4',
    zoom: 0.88,
    sidebarCollapsed: false,
    provider: 'gemini',
    apiKey: '',
    model: 'gemini-2.5-flash',
    ollamaUrl: 'http://localhost:11434',
    currentMarkdown: '',
    masterProfile: '',
    atsAnalysis: null,
    currentFilename: null,
    currentCoverLetter: '',
    currentLetterFilename: null,
    isLoading: false,
};

// DOM Elements
const elements = {
    // Header & Sidebar Controls
    sidebarToggleBtn: document.getElementById('sidebar-toggle-btn'),
    appSidebar: document.getElementById('app-sidebar'),
    activeFilenameDisplay: document.getElementById('active-filename-display'),
    currentProviderName: document.getElementById('current-provider-name'),
    quickSettingsPill: document.getElementById('quick-settings-pill'),
    atsBadge: document.getElementById('ats-badge'),
    atsBadgeText: document.getElementById('ats-badge-text'),

    // Left Tabs
    tabJdBtn: document.getElementById('tab-jd-btn'),
    tabProfileBtn: document.getElementById('tab-profile-btn'),
    tabSettingsBtn: document.getElementById('tab-settings-btn'),
    tabHistoryBtn: document.getElementById('tab-history-btn'),
    paneJd: document.getElementById('pane-jd'),
    paneProfile: document.getElementById('pane-profile'),
    paneSettings: document.getElementById('pane-settings'),
    paneHistory: document.getElementById('pane-history'),

    // Right Tabs
    tabPreviewBtn: document.getElementById('tab-preview-btn'),
    tabEditorBtn: document.getElementById('tab-editor-btn'),
    tabAtsBtn: document.getElementById('tab-ats-btn'),
    tabLetterBtn: document.getElementById('tab-letter-btn'),
    panePreview: document.getElementById('pane-preview'),
    paneEditor: document.getElementById('pane-editor'),
    paneAts: document.getElementById('pane-ats'),
    paneLetter: document.getElementById('pane-letter'),

    // JD Form
    jdText: document.getElementById('jd-text'),
    sampleJdBtn: document.getElementById('sample-jd-btn'),
    clearJdBtn: document.getElementById('clear-jd-btn'),
    targetRole: document.getElementById('target-role'),
    targetCompany: document.getElementById('target-company'),
    toneSelect: document.getElementById('tone-select'),
    lengthSelect: document.getElementById('length-select'),
    tailorBtn: document.getElementById('tailor-btn'),
    tailorLoader: document.getElementById('tailor-loader'),
    coverLetterBtn: document.getElementById('cover-letter-btn'),
    letterLoader: document.getElementById('letter-loader'),

    // Cover Letter Actions & Sheet
    letterSheet: document.getElementById('letter-sheet'),
    copyLetterBtn: document.getElementById('copy-letter-btn'),
    downloadLetterBtn: document.getElementById('download-letter-btn'),
    printLetterBtn: document.getElementById('print-letter-btn'),

    // Profile Form
    profileUploadInput: document.getElementById('profile-upload-input'),
    profileUploadBtn: document.getElementById('profile-upload-btn'),
    profileUploadBox: document.getElementById('profile-upload-box'),
    profileFormatAiCheckbox: document.getElementById('profile-format-ai'),
    profileEditor: document.getElementById('profile-editor'),
    saveProfileBtn: document.getElementById('save-profile-btn'),
    profileUploadStatus: document.getElementById('profile-upload-status'),

    // Settings
    providerSelect: document.getElementById('provider-select'),
    apiKeyInput: document.getElementById('api-key-input'),
    modelInput: document.getElementById('model-input'),
    ollamaUrlInput: document.getElementById('ollama-url-input'),
    ollamaGroup: document.getElementById('ollama-group'),
    testLlmBtn: document.getElementById('test-llm-btn'),
    testLlmStatus: document.getElementById('test-llm-status'),

    // History
    historyList: document.getElementById('history-list'),
    refreshHistoryBtn: document.getElementById('refresh-history-btn'),

    // Zoom Controls
    zoomInBtn: document.getElementById('zoom-in-btn'),
    zoomOutBtn: document.getElementById('zoom-out-btn'),
    zoomFitBtn: document.getElementById('zoom-fit-btn'),
    zoomLabel: document.getElementById('zoom-label'),

    // Preview & Output
    resumeSheet: document.getElementById('resume-sheet'),
    markdownEditor: document.getElementById('markdown-editor'),
    themeSelect: document.getElementById('theme-select'),
    paperSelect: document.getElementById('paper-select'),
    pageFitBadge: document.getElementById('page-fit-badge'),
    pageFitIcon: document.getElementById('page-fit-icon'),
    pageFitText: document.getElementById('page-fit-text'),
    downloadMdBtn: document.getElementById('download-md-btn'),
    printPdfBtn: document.getElementById('print-pdf-btn'),
    downloadPdfBtn: document.getElementById('download-pdf-btn'),
    copyMdBtn: document.getElementById('copy-md-btn'),
    saveEditsBtn: document.getElementById('save-edits-btn'),

    // ATS Match Panel
    atsScoreNum: document.getElementById('ats-score-num'),
    atsScoreCircle: document.getElementById('ats-score-circle'),
    atsSummaryText: document.getElementById('ats-summary-text'),
    matchedKeywordsList: document.getElementById('matched-keywords-list'),
    missingKeywordsList: document.getElementById('missing-keywords-list'),
    interviewTipsList: document.getElementById('interview-tips-list'),

    // Notifications Toast
    toast: document.getElementById('toast'),
    toastMessage: document.getElementById('toast-message'),
};

// Initialize Application
async function init() {
    loadSettingsFromStorage();
    setupEventListeners();
    applyZoom();
    await fetchSystemConfig();
    await loadMasterProfile();
    await loadResumeHistory();
    renderMarkdownPreview();
    autoFitZoom();
}

// Settings Persistence
function loadSettingsFromStorage() {
    const saved = localStorage.getItem('resume_tailor_settings');
    if (saved) {
        try {
            const data = JSON.parse(saved);
            state.provider = data.provider || 'gemini';
            state.apiKey = data.apiKey || '';
            state.model = data.model || 'gemini-2.5-flash';
            state.ollamaUrl = data.ollamaUrl || 'http://localhost:11434';
            state.theme = data.theme || 'modern';
            state.paperSize = data.paperSize || 'A4';
            state.zoom = data.zoom || 0.88;
        } catch (e) {
            console.error('Error loading settings', e);
        }
    }
    syncSettingsUI();
}

function saveSettingsToStorage() {
    localStorage.setItem('resume_tailor_settings', JSON.stringify({
        provider: state.provider,
        apiKey: state.apiKey,
        model: state.model,
        ollamaUrl: state.ollamaUrl,
        theme: state.theme,
        paperSize: state.paperSize,
        zoom: state.zoom,
    }));
}

function syncSettingsUI() {
    if (elements.providerSelect) elements.providerSelect.value = state.provider;
    if (elements.apiKeyInput) elements.apiKeyInput.value = state.apiKey;
    if (elements.modelInput) elements.modelInput.value = state.model;
    if (elements.ollamaUrlInput) elements.ollamaUrlInput.value = state.ollamaUrl;
    if (elements.themeSelect) elements.themeSelect.value = state.theme;
    if (elements.paperSelect) elements.paperSelect.value = state.paperSize;
    if (elements.currentProviderName) elements.currentProviderName.textContent = state.provider;

    if (elements.ollamaGroup) {
        elements.ollamaGroup.classList.toggle('hidden', state.provider !== 'ollama');
    }
}

// Fetch Initial Config & Environment
async function fetchSystemConfig() {
    try {
        const res = await fetch('/api/config');
        if (res.ok) {
            const data = await res.json();
            if (!state.apiKey && data.detected_keys && data.detected_keys[state.provider]) {
                elements.apiKeyInput.placeholder = "(Found in system environment variables)";
            }
        }
    } catch (e) {
        console.warn('Could not fetch system config', e);
    }
}

// Zoom Management
function setZoom(val) {
    state.zoom = Math.min(1.5, Math.max(0.45, parseFloat(val.toFixed(2))));
    applyZoom();
    saveSettingsToStorage();
}

function applyZoom() {
    document.documentElement.style.setProperty('--preview-zoom', state.zoom);
    if (elements.zoomLabel) {
        elements.zoomLabel.textContent = `${Math.round(state.zoom * 100)}%`;
    }
}

function autoFitZoom() {
    const wrapper = elements.panePreview;
    if (!wrapper) return;
    const availableWidth = wrapper.clientWidth - 48;
    // Standard A4 width in px at 96dpi is ~794px
    const targetWidth = state.paperSize === 'Letter' ? 816 : 794;
    if (availableWidth > 0 && targetWidth > 0) {
        const fitScale = Math.min(1.15, Math.max(0.5, availableWidth / targetWidth));
        setZoom(fitScale);
    }
}

// Sidebar Toggle
function toggleSidebar() {
    state.sidebarCollapsed = !state.sidebarCollapsed;
    const sidebar = elements.appSidebar;
    if (!sidebar) return;

    if (state.sidebarCollapsed) {
        sidebar.classList.add('!w-0', '!min-w-0', '!overflow-hidden', '!border-none', '!p-0', '!opacity-0');
    } else {
        sidebar.classList.remove('!w-0', '!min-w-0', '!overflow-hidden', '!border-none', '!p-0', '!opacity-0');
    }

    setTimeout(() => {
        autoFitZoom();
    }, 320);
}

// Event Listeners Setup
function setupEventListeners() {
    // Sidebar Toggle
    if (elements.sidebarToggleBtn) {
        elements.sidebarToggleBtn.addEventListener('click', toggleSidebar);
    }

    // Quick Settings Pill
    if (elements.quickSettingsPill) {
        elements.quickSettingsPill.addEventListener('click', () => {
            if (state.sidebarCollapsed) toggleSidebar();
            switchLeftTab('settings');
        });
    }

    // Left Tab Switches
    elements.tabJdBtn.addEventListener('click', () => switchLeftTab('jd'));
    elements.tabProfileBtn.addEventListener('click', () => switchLeftTab('profile'));
    elements.tabSettingsBtn.addEventListener('click', () => switchLeftTab('settings'));
    elements.tabHistoryBtn.addEventListener('click', () => switchLeftTab('history'));

    // Right Tab Switches
    elements.tabPreviewBtn.addEventListener('click', () => switchRightTab('preview'));
    elements.tabEditorBtn.addEventListener('click', () => switchRightTab('editor'));
    elements.tabAtsBtn.addEventListener('click', () => switchRightTab('ats'));
    if (elements.tabLetterBtn) elements.tabLetterBtn.addEventListener('click', () => switchRightTab('letter'));

    // Zoom Controls
    if (elements.zoomInBtn) elements.zoomInBtn.addEventListener('click', () => setZoom(state.zoom + 0.08));
    if (elements.zoomOutBtn) elements.zoomOutBtn.addEventListener('click', () => setZoom(state.zoom - 0.08));
    if (elements.zoomFitBtn) elements.zoomFitBtn.addEventListener('click', autoFitZoom);

    // Theme & Paper Size
    elements.themeSelect.addEventListener('change', (e) => {
        state.theme = e.target.value;
        saveSettingsToStorage();
        updateSheetStyles();
    });
    elements.paperSelect.addEventListener('change', (e) => {
        state.paperSize = e.target.value;
        saveSettingsToStorage();
        updateSheetStyles();
        autoFitZoom();
    });

    // Sample JD & Clear Buttons
    if (elements.sampleJdBtn) {
        elements.sampleJdBtn.addEventListener('click', () => {
            elements.jdText.value = SAMPLE_JOB_DESCRIPTION;
            elements.targetRole.value = "Senior Full-Stack Platform Engineer";
            elements.targetCompany.value = "CloudScale Dynamics";
            showToast("Sample Job Description loaded!");
        });
    }
    if (elements.clearJdBtn) {
        elements.clearJdBtn.addEventListener('click', () => {
            elements.jdText.value = '';
            elements.targetRole.value = '';
            elements.targetCompany.value = '';
        });
    }

    // Provider change
    elements.providerSelect.addEventListener('change', (e) => {
        state.provider = e.target.value;
        if (state.provider === 'gemini') state.model = 'gemini-2.5-flash';
        else if (state.provider === 'openai') state.model = 'gpt-4o-mini';
        else if (state.provider === 'anthropic') state.model = 'claude-3-5-sonnet-20241022';
        else if (state.provider === 'ollama') state.model = 'llama3.2';
        elements.modelInput.value = state.model;
        syncSettingsUI();
        saveSettingsToStorage();
    });

    elements.apiKeyInput.addEventListener('input', (e) => {
        state.apiKey = e.target.value.trim();
        saveSettingsToStorage();
    });

    elements.modelInput.addEventListener('input', (e) => {
        state.model = e.target.value.trim();
        saveSettingsToStorage();
    });

    elements.ollamaUrlInput.addEventListener('input', (e) => {
        state.ollamaUrl = e.target.value.trim();
        saveSettingsToStorage();
    });

    // Test Connection
    elements.testLlmBtn.addEventListener('click', handleTestConnection);

    // Profile Save
    elements.saveProfileBtn.addEventListener('click', handleSaveProfile);

    // Profile Upload (Browse & Drag/Drop)
    elements.profileUploadBtn.addEventListener('click', () => elements.profileUploadInput.click());
    elements.profileUploadInput.addEventListener('change', handleFileUpload);
    setupDragAndDrop();

    // Live Editor Sync
    elements.markdownEditor.addEventListener('input', (e) => {
        state.currentMarkdown = e.target.value;
        renderMarkdownPreview();
    });

    elements.saveEditsBtn.addEventListener('click', handleSaveEdits);

    // Tailor Resume Button
    elements.tailorBtn.addEventListener('click', handleTailorResume);

    // Cover Letter Buttons
    if (elements.coverLetterBtn) elements.coverLetterBtn.addEventListener('click', handleGenerateCoverLetter);
    if (elements.copyLetterBtn) elements.copyLetterBtn.addEventListener('click', handleCopyLetter);
    if (elements.downloadLetterBtn) elements.downloadLetterBtn.addEventListener('click', handleDownloadLetter);
    if (elements.printLetterBtn) elements.printLetterBtn.addEventListener('click', handlePrintLetter);

    // Export Handlers
    elements.downloadMdBtn.addEventListener('click', handleDownloadMarkdown);
    elements.downloadPdfBtn.addEventListener('click', handleDirectPdfDownload);
    elements.printPdfBtn.addEventListener('click', handlePrintPdf);
    elements.copyMdBtn.addEventListener('click', handleCopyMarkdown);
    elements.refreshHistoryBtn.addEventListener('click', loadResumeHistory);

    // Window Resize -> auto fit zoom
    window.addEventListener('resize', () => {
        if (state.rightTab === 'preview' || state.rightTab === 'letter') {
            autoFitZoom();
        }
    });

    // Global Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
        // Ctrl+B: Toggle Sidebar
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
            e.preventDefault();
            toggleSidebar();
        }
        // Ctrl+Enter: Tailor Resume (when JD text area is focused or general)
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            handleTailorResume();
        }
    });
}

// Tabs Logic
function switchLeftTab(tab) {
    state.currentTab = tab;
    const tabs = ['jd', 'profile', 'settings', 'history'];
    tabs.forEach(t => {
        const btn = document.getElementById(`tab-${t}-btn`);
        const pane = document.getElementById(`pane-${t}`);
        if (!btn || !pane) return;
        if (t === tab) {
            btn.className = "flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2 text-xs font-semibold rounded-md text-blue-700 bg-white shadow-xs border border-slate-200/60 transition-all";
            pane.classList.remove('hidden');
        } else {
            btn.className = "flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2 text-xs font-medium rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-all";
            pane.classList.add('hidden');
        }
    });
}

function switchRightTab(tab) {
    state.rightTab = tab;
    const tabs = ['preview', 'editor', 'ats', 'letter'];
    tabs.forEach(t => {
        const btn = document.getElementById(`tab-${t}-btn`);
        const pane = document.getElementById(`pane-${t}`);
        if (!btn || !pane) return;
        if (t === tab) {
            btn.className = "flex items-center gap-1.5 py-1 px-2.5 text-xs font-semibold text-blue-700 bg-white shadow-xs rounded-md transition-all";
            pane.classList.remove('hidden');
        } else {
            btn.className = "flex items-center gap-1.5 py-1 px-2.5 text-xs font-medium text-slate-600 hover:text-slate-900 rounded-md transition-all";
            pane.classList.add('hidden');
        }
    });

    if (tab === 'editor') {
        elements.markdownEditor.value = state.currentMarkdown;
    } else if (tab === 'preview') {
        renderMarkdownPreview();
        autoFitZoom();
    } else if (tab === 'letter') {
        renderCoverLetter();
        autoFitZoom();
    }
}

// Load & Save Master Profile
async function loadMasterProfile() {
    try {
        const res = await fetch('/api/profile');
        if (res.ok) {
            const data = await res.json();
            state.masterProfile = data.content;
            elements.profileEditor.value = data.content;
            if (!state.currentMarkdown) {
                state.currentMarkdown = data.content;
                elements.markdownEditor.value = data.content;
            }
        }
    } catch (e) {
        console.error('Failed to load master profile', e);
    }
}

async function handleSaveProfile() {
    const content = elements.profileEditor.value;
    try {
        const res = await fetch('/api/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        if (res.ok) {
            state.masterProfile = content;
            showToast("Master profile saved successfully!");
        } else {
            showToast("Failed to save master profile", true);
        }
    } catch (e) {
        showToast("Error saving profile: " + e.message, true);
    }
}

// File Upload for Profile
function setupDragAndDrop() {
    const box = elements.profileUploadBox;
    if (!box) return;
    ['dragenter', 'dragover'].forEach(name => {
        box.addEventListener(name, (e) => {
            e.preventDefault();
            box.classList.add('border-blue-500', 'bg-blue-50/50');
        });
    });
    ['dragleave', 'drop'].forEach(name => {
        box.addEventListener(name, (e) => {
            e.preventDefault();
            box.classList.remove('border-blue-500', 'bg-blue-50/50');
        });
    });
    box.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    });
}

function handleFileUpload(e) {
    if (e.target.files.length > 0) {
        uploadFile(e.target.files[0]);
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('format_with_ai', elements.profileFormatAiCheckbox.checked);
    if (state.provider) formData.append('provider', state.provider);
    if (state.apiKey) formData.append('api_key', state.apiKey);
    if (state.model) formData.append('model', state.model);
    if (state.ollamaUrl) formData.append('base_url', state.ollamaUrl);

    elements.profileUploadStatus.innerHTML = `
        <div class="flex items-center gap-1.5 text-blue-600 font-medium text-xs mt-2">
            <svg class="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
            Extracting career history from ${file.name}...
        </div>
    `;

    try {
        const res = await fetch('/api/upload-resume', {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();
        if (res.ok && data.success) {
            state.masterProfile = data.content;
            elements.profileEditor.value = data.content;
            elements.profileUploadStatus.innerHTML = `
                <div class="text-emerald-600 font-medium text-xs mt-2">
                    ✓ Parsed ${file.name}! ${data.ai_formatted ? 'Structured with AI.' : 'Extracted raw content.'}
                </div>
            `;
            showToast("Resume parsed and saved to Master Profile!");
        } else {
            elements.profileUploadStatus.innerHTML = `
                <div class="text-rose-600 font-medium text-xs mt-2">
                    ✕ Failed: ${data.detail || 'Upload error'}
                </div>
            `;
        }
    } catch (e) {
        elements.profileUploadStatus.innerHTML = `
            <div class="text-rose-600 font-medium text-xs mt-2">
                ✕ Upload error: ${e.message}
            </div>
        `;
    }
}

// Test Connection
async function handleTestConnection() {
    elements.testLlmStatus.innerHTML = `
        <div class="text-blue-600 text-xs flex items-center justify-center gap-1.5">
            <svg class="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
            Testing connection to ${state.provider}...
        </div>
    `;

    try {
        const res = await fetch('/api/test-llm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                provider: state.provider,
                api_key: state.apiKey,
                model: state.model,
                base_url: state.ollamaUrl
            })
        });
        const data = await res.json();
        if (data.success) {
            elements.testLlmStatus.innerHTML = `
                <span class="text-emerald-600 font-semibold text-xs">✓ ${data.message}</span>
            `;
            showToast("LLM Connection Verified!");
        } else {
            elements.testLlmStatus.innerHTML = `
                <span class="text-rose-600 font-medium text-xs">✕ ${data.error || 'Connection failed'}</span>
            `;
        }
    } catch (e) {
        elements.testLlmStatus.innerHTML = `
            <span class="text-rose-600 font-medium text-xs">✕ ${e.message}</span>
        `;
    }
}

// Tailor Resume Action
async function handleTailorResume() {
    const jd = elements.jdText.value.trim();
    if (!jd) {
        showToast("Please paste a Job Description first!", true);
        elements.jdText.focus();
        return;
    }

    state.isLoading = true;
    elements.tailorBtn.disabled = true;
    elements.tailorBtn.classList.add('opacity-70', 'cursor-not-allowed');
    elements.tailorLoader.classList.remove('hidden');

    const payload = {
        job_description: jd,
        target_role: elements.targetRole.value.trim(),
        target_company: elements.targetCompany.value.trim(),
        tone: elements.toneSelect.value,
        length_style: elements.lengthSelect.value,
        provider: state.provider,
        api_key: state.apiKey,
        model: state.model,
        base_url: state.ollamaUrl,
        theme: state.theme,
        paper_size: state.paperSize,
    };

    try {
        const res = await fetch('/api/tailor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok && data.success) {
            state.currentMarkdown = data.resume_markdown;
            state.atsAnalysis = data.ats_analysis;
            state.currentFilename = data.filename;
            elements.markdownEditor.value = data.resume_markdown;

            if (elements.activeFilenameDisplay) {
                elements.activeFilenameDisplay.textContent = data.filename;
            }

            renderMarkdownPreview();
            renderAtsAnalysis();
            switchRightTab('preview');
            loadResumeHistory();
            showToast("Resume tailored and saved!");
        } else {
            showToast(`Tailoring error: ${data.detail || 'Unknown error'}`, true);
        }
    } catch (e) {
        showToast(`Request failed: ${e.message}`, true);
    } finally {
        state.isLoading = false;
        elements.tailorBtn.disabled = false;
        elements.tailorBtn.classList.remove('opacity-70', 'cursor-not-allowed');
        elements.tailorLoader.classList.add('hidden');
    }
}

// Render Markdown to Preview Sheet
function renderMarkdownPreview() {
    if (!elements.resumeSheet) return;
    
    updateSheetStyles();

    const md = state.currentMarkdown || state.masterProfile || "# Your Name\n\nPaste a job description on the left and click **Tailor Resume**.";
    
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
        elements.resumeSheet.innerHTML = marked.parse(md);
    } else {
        elements.resumeSheet.innerText = md;
    }

    setTimeout(checkPageFit, 60);
}

function updateSheetStyles() {
    if (elements.resumeSheet) {
        elements.resumeSheet.className = `resume-sheet theme-${state.theme} ${state.paperSize === 'Letter' ? 'letter-size' : ''} select-text`;
    }
    if (elements.letterSheet) {
        elements.letterSheet.className = `cover-letter-sheet theme-${state.theme} ${state.paperSize === 'Letter' ? 'letter-size' : ''} select-text`;
    }
    setTimeout(checkPageFit, 60);
}

// Check if content fits in 1 Page (A4 ~1123px, Letter ~1056px at 96 DPI)
function checkPageFit() {
    if (!elements.resumeSheet || !elements.pageFitBadge) return;
    
    const maxHeight = state.paperSize === 'Letter' ? 1056 : 1123;
    const currentHeight = elements.resumeSheet.scrollHeight;
    
    // Remove existing guide line if any
    const existingGuide = elements.resumeSheet.querySelector('.page-limit-guide');
    if (existingGuide) existingGuide.remove();

    if (currentHeight <= maxHeight + 10) {
        elements.pageFitBadge.className = "hidden sm:flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 transition-colors";
        if (elements.pageFitIcon) elements.pageFitIcon.textContent = "✓";
        if (elements.pageFitText) elements.pageFitText.textContent = "1 Page Fit";
    } else {
        const overflowMm = Math.round(((currentHeight - maxHeight) / 96) * 25.4);
        elements.pageFitBadge.className = "hidden sm:flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 transition-colors";
        if (elements.pageFitIcon) elements.pageFitIcon.textContent = "⚠️";
        if (elements.pageFitText) elements.pageFitText.textContent = `Spills to Page 2 (+${overflowMm}mm)`;

        // Inject visual boundary guide
        const guide = document.createElement('div');
        guide.className = 'page-limit-guide';
        elements.resumeSheet.appendChild(guide);
    }
}

// Render ATS Match Analysis
function renderAtsAnalysis() {
    const analysis = state.atsAnalysis;
    if (!analysis) {
        if (elements.atsBadge) elements.atsBadge.classList.add('hidden');
        return;
    }

    const score = analysis.match_score || 0;
    if (elements.atsBadge) {
        elements.atsBadge.classList.remove('hidden');
        if (elements.atsBadgeText) elements.atsBadgeText.textContent = `${score}% Match`;
    }
    
    if (elements.atsScoreNum) {
        elements.atsScoreNum.textContent = `${score}%`;
    }

    if (elements.atsScoreCircle) {
        const circumference = 2 * Math.PI * 40; // r=40
        const offset = circumference - (score / 100) * circumference;
        elements.atsScoreCircle.style.strokeDasharray = `${circumference} ${circumference}`;
        elements.atsScoreCircle.style.strokeDashoffset = offset;
        
        if (score >= 80) elements.atsScoreCircle.setAttribute('stroke', '#10b981'); // emerald
        else if (score >= 60) elements.atsScoreCircle.setAttribute('stroke', '#f59e0b'); // amber
        else elements.atsScoreCircle.setAttribute('stroke', '#ef4444'); // rose
    }

    if (elements.atsSummaryText) {
        elements.atsSummaryText.textContent = analysis.tailoring_summary || "Resume optimized for target job keywords and impact.";
    }

    // Matched Keywords
    if (elements.matchedKeywordsList) {
        elements.matchedKeywordsList.innerHTML = '';
        const matched = analysis.matched_keywords || [];
        if (matched.length === 0) {
            elements.matchedKeywordsList.innerHTML = `<span class="text-xs text-slate-400">None detected</span>`;
        } else {
            matched.forEach(kw => {
                const span = document.createElement('span');
                span.className = "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200";
                span.textContent = kw;
                elements.matchedKeywordsList.appendChild(span);
            });
        }
    }

    // Missing Keywords
    if (elements.missingKeywordsList) {
        elements.missingKeywordsList.innerHTML = '';
        const missing = analysis.missing_keywords || [];
        if (missing.length === 0) {
            elements.missingKeywordsList.innerHTML = `<span class="text-xs text-emerald-600 font-medium">Great match! No major skill gaps detected.</span>`;
        } else {
            missing.forEach(kw => {
                const span = document.createElement('span');
                span.className = "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200";
                span.textContent = kw;
                elements.missingKeywordsList.appendChild(span);
            });
        }
    }

    // Interview Tips
    if (elements.interviewTipsList) {
        elements.interviewTipsList.innerHTML = '';
        const tips = analysis.interview_tips || [];
        if (tips.length === 0) {
            elements.interviewTipsList.innerHTML = `<li class="text-xs text-slate-400">Review metrics mentioned in your bullet points.</li>`;
        } else {
            tips.forEach(tip => {
                const li = document.createElement('li');
                li.className = "text-xs text-slate-700 leading-relaxed mb-1";
                li.textContent = tip;
                elements.interviewTipsList.appendChild(li);
            });
        }
    }
}

// Cover Letter Handlers
async function handleGenerateCoverLetter() {
    const jd = elements.jdText.value.trim();
    if (!jd) {
        showToast("Please paste a Job Description first!", true);
        elements.jdText.focus();
        return;
    }

    if (elements.coverLetterBtn) {
        elements.coverLetterBtn.disabled = true;
        elements.coverLetterBtn.classList.add('opacity-70', 'cursor-not-allowed');
    }
    if (elements.letterLoader) elements.letterLoader.classList.remove('hidden');

    const payload = {
        job_description: jd,
        target_role: elements.targetRole.value.trim(),
        target_company: elements.targetCompany.value.trim(),
        tone: elements.toneSelect.value,
        provider: state.provider,
        api_key: state.apiKey,
        model: state.model,
        base_url: state.ollamaUrl,
    };

    try {
        const res = await fetch('/api/cover-letter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok && data.success) {
            state.currentCoverLetter = data.cover_letter_markdown;
            state.currentLetterFilename = data.filename;
            renderCoverLetter();
            switchRightTab('letter');
            showToast("Tailored cover letter created!");
        } else {
            showToast(`Cover letter error: ${data.detail || 'Unknown error'}`, true);
        }
    } catch (e) {
        showToast(`Request failed: ${e.message}`, true);
    } finally {
        if (elements.coverLetterBtn) {
            elements.coverLetterBtn.disabled = false;
            elements.coverLetterBtn.classList.remove('opacity-70', 'cursor-not-allowed');
        }
        if (elements.letterLoader) elements.letterLoader.classList.add('hidden');
    }
}

function renderCoverLetter() {
    if (!elements.letterSheet) return;
    if (!state.currentCoverLetter) {
        elements.letterSheet.innerHTML = `
            <div class="text-center py-16 text-slate-400">
                <svg class="w-10 h-10 mx-auto mb-2.5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                <p class="text-xs font-semibold text-slate-700">No Cover Letter Generated Yet</p>
                <p class="text-[11px] text-slate-400 mt-1 max-w-xs mx-auto">Click <strong>"Generate Matching Cover Letter"</strong> on the left to write an authentic, high-converting letter tailored specifically to this job posting.</p>
            </div>
        `;
        return;
    }

    elements.letterSheet.className = `cover-letter-sheet theme-${state.theme} ${state.paperSize === 'Letter' ? 'letter-size' : ''} select-text`;
    if (typeof marked !== 'undefined') {
        elements.letterSheet.innerHTML = marked.parse(state.currentCoverLetter);
    } else {
        elements.letterSheet.innerText = state.currentCoverLetter;
    }
}

function handleCopyLetter() {
    if (!state.currentCoverLetter) {
        showToast("No cover letter generated to copy!", true);
        return;
    }
    navigator.clipboard.writeText(state.currentCoverLetter).then(() => {
        showToast("Cover letter copied to clipboard!");
    }).catch(err => {
        showToast("Failed to copy: " + err, true);
    });
}

function handleDownloadLetter() {
    if (!state.currentCoverLetter) {
        showToast("No cover letter generated yet!", true);
        return;
    }
    const blob = new Blob([state.currentCoverLetter], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = state.currentLetterFilename || `Cover_Letter_${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("Cover letter downloaded!");
}

function handlePrintLetter() {
    if (!state.currentCoverLetter) {
        showToast("No cover letter generated to print!", true);
        return;
    }
    window.print();
}

// Save Manual Edits
async function handleSaveEdits() {
    const content = elements.markdownEditor.value;
    state.currentMarkdown = content;
    renderMarkdownPreview();

    try {
        const res = await fetch('/api/save-resume', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: state.currentFilename,
                content: content,
                target_role: elements.targetRole.value || "Custom"
            })
        });
        const data = await res.json();
        if (res.ok && data.success) {
            state.currentFilename = data.filename;
            if (elements.activeFilenameDisplay) {
                elements.activeFilenameDisplay.textContent = data.filename;
            }
            showToast("Resume edits saved to disk!");
            loadResumeHistory();
        } else {
            showToast("Failed to save edits", true);
        }
    } catch (e) {
        showToast("Error saving edits: " + e.message, true);
    }
}

// Resume History
async function loadResumeHistory() {
    try {
        const res = await fetch('/api/resumes');
        if (res.ok) {
            const data = await res.json();
            renderResumeHistory(data.resumes || []);
        }
    } catch (e) {
        console.error('Failed to load history', e);
    }
}

function renderResumeHistory(resumes) {
    if (!elements.historyList) return;
    elements.historyList.innerHTML = '';

    if (resumes.length === 0) {
        elements.historyList.innerHTML = `
            <div class="text-center py-6 text-slate-400 text-xs">
                No past resumes found.
            </div>
        `;
        return;
    }

    resumes.forEach(item => {
        const div = document.createElement('div');
        div.className = "p-2.5 rounded-lg border border-slate-200 hover:border-blue-400 bg-white hover:bg-blue-50/20 transition-all flex items-center justify-between group";
        
        const friendlyName = item.filename.replace('.md', '').replace(/_/g, ' ');
        div.innerHTML = `
            <div class="cursor-pointer flex-1 mr-2 overflow-hidden" onclick="loadHistoricalResume('${item.filename}')">
                <div class="text-xs font-semibold text-slate-800 group-hover:text-blue-600 truncate">${friendlyName}</div>
                <div class="text-[10px] text-slate-400 mt-0.5">${item.created_at}</div>
            </div>
            <div class="flex items-center gap-1">
                <a href="/api/download-md/${item.filename}" class="p-1 text-slate-400 hover:text-slate-700" title="Download .md">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                </a>
            </div>
        `;
        elements.historyList.appendChild(div);
    });
}

window.loadHistoricalResume = async function(filename) {
    try {
        const res = await fetch(`/api/resumes/${filename}`);
        if (res.ok) {
            const data = await res.json();
            state.currentMarkdown = data.content;
            state.currentFilename = filename;
            elements.markdownEditor.value = data.content;
            if (elements.activeFilenameDisplay) {
                elements.activeFilenameDisplay.textContent = filename;
            }
            renderMarkdownPreview();
            switchRightTab('preview');
            showToast(`Loaded ${filename}`);
        }
    } catch (e) {
        showToast("Error loading file: " + e.message, true);
    }
};

// Export Handlers
function handleDownloadMarkdown() {
    const md = state.currentMarkdown || elements.markdownEditor.value;
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = state.currentFilename || `Resume_${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("Markdown file downloaded!");
}

function handleCopyMarkdown() {
    const md = state.currentMarkdown || elements.markdownEditor.value;
    navigator.clipboard.writeText(md).then(() => {
        showToast("Markdown copied to clipboard!");
    }).catch(err => {
        showToast("Failed to copy: " + err, true);
    });
}

function handlePrintPdf() {
    window.print();
}

function handleDirectPdfDownload() {
    const element = elements.resumeSheet;
    if (!element) return;

    showToast("Generating high-resolution vector PDF...");

    if (typeof html2pdf !== 'undefined') {
        const opt = {
            margin: [10, 12, 10, 12],
            filename: (state.currentFilename ? state.currentFilename.replace('.md', '.pdf') : 'resume.pdf'),
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, letterRendering: true },
            jsPDF: { unit: 'mm', format: state.paperSize.toLowerCase(), orientation: 'portrait' }
        };

        html2pdf().set(opt).from(element).save().then(() => {
            showToast("PDF downloaded successfully!");
        }).catch((err) => {
            console.error('html2pdf error:', err);
            window.print();
        });
    } else {
        window.print();
    }
}

// Toast Notifications
let toastTimeout = null;
function showToast(message, isError = false) {
    if (!elements.toast || !elements.toastMessage) return;
    elements.toastMessage.textContent = message;
    
    if (isError) {
        elements.toast.className = "fixed bottom-5 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-4 py-2 rounded-full shadow-lg text-white text-xs font-medium bg-rose-600 transition-all duration-300 transform translate-y-0 opacity-100";
    } else {
        elements.toast.className = "fixed bottom-5 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-4 py-2 rounded-full shadow-lg text-white text-xs font-medium bg-slate-900 transition-all duration-300 transform translate-y-0 opacity-100";
    }

    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        elements.toast.className = "fixed bottom-5 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-4 py-2 rounded-full shadow-lg text-white text-xs font-medium bg-slate-900 transition-all duration-300 transform translate-y-12 opacity-0 pointer-events-none";
    }, 3000);
}

// Run on page load
document.addEventListener('DOMContentLoaded', init);
