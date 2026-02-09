/**
 * AI CINEMATIC VIDEO EDITOR PRO
 * Frontend Application Logic
 */

// ============================================
// CONFIGURATION
// ============================================

const CONFIG = {
    API_BASE_URL: '',
    WS_URL: window.location.origin,
    MAX_FILE_SIZE: 2 * 1024 * 1024 * 1024, // 2GB
    ALLOWED_TYPES: ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm', 'video/x-matroska']
};

// ============================================
// STATE MANAGEMENT
// ============================================

const state = {
    sessionId: null,
    currentPhase: 'upload',
    videoUploaded: false,
    promptRefined: false,
    promptApproved: false,
    questionsAnswered: false,
    narrativeAnalyzed: false,
    scenePlanned: false,
    answers: {},
    webhookConfig: {
        webhook_url: '',
        enabled: false,
        events: {}
    }
};

// ============================================
// DOM ELEMENTS
// ============================================

const elements = {
    // Session
    sessionId: document.getElementById('sessionId'),
    
    // Upload
    uploadZone: document.getElementById('uploadZone'),
    fileInput: document.getElementById('fileInput'),
    uploadProgress: document.getElementById('uploadProgress'),
    progressFill: document.getElementById('progressFill'),
    progressText: document.getElementById('progressText'),
    uploadedFile: document.getElementById('uploadedFile'),
    uploadedFilename: document.getElementById('uploadedFilename'),
    
    // Phase 1
    originalPrompt: document.getElementById('originalPrompt'),
    refinePromptBtn: document.getElementById('refinePromptBtn'),
    refinementResult: document.getElementById('refinementResult'),
    displayOriginal: document.getElementById('displayOriginal'),
    displayImproved: document.getElementById('displayImproved'),
    issuesList: document.getElementById('issuesList'),
    improvementsList: document.getElementById('improvementsList'),
    approvePromptBtn: document.getElementById('approvePromptBtn'),
    revisePromptBtn: document.getElementById('revisePromptBtn'),
    revisionArea: document.getElementById('revisionArea'),
    revisionFeedback: document.getElementById('revisionFeedback'),
    submitRevisionBtn: document.getElementById('submitRevisionBtn'),
    
    // Phase 2
    questionsContainer: document.getElementById('questionsContainer'),
    submitAnswersBtn: document.getElementById('submitAnswersBtn'),
    answeredCount: document.getElementById('answeredCount'),
    totalQuestions: document.getElementById('totalQuestions'),
    
    // Phase 3
    narrativeProcessing: document.getElementById('narrativeProcessing'),
    narrativeSummary: document.getElementById('narrativeSummary'),
    narrativeArc: document.getElementById('narrativeArc'),
    dominantTone: document.getElementById('dominantTone'),
    pacingInfo: document.getElementById('pacingInfo'),
    continueToPlanningBtn: document.getElementById('continueToPlanningBtn'),
    
    // Phase 4
    scenePlanningProcessing: document.getElementById('scenePlanningProcessing'),
    scenePlan: document.getElementById('scenePlan'),
    planTitle: document.getElementById('planTitle'),
    planTheme: document.getElementById('planTheme'),
    planFormat: document.getElementById('planFormat'),
    planStyle: document.getElementById('planStyle'),
    scenesTimeline: document.getElementById('scenesTimeline'),
    executePlanBtn: document.getElementById('executePlanBtn'),
    exportPlanBtn: document.getElementById('exportPlanBtn'),
    
    // Execution
    executionProgress: document.getElementById('executionProgress'),
    executionComplete: document.getElementById('executionComplete'),
    downloadBtn: document.getElementById('downloadBtn'),
    
    // Webhook
    webhookUrl: document.getElementById('webhookUrl'),
    webhookEnabled: document.getElementById('webhookEnabled'),
    eventCheckboxes: document.getElementById('eventCheckboxes'),
    testWebhookBtn: document.getElementById('testWebhookBtn'),
    saveWebhookBtn: document.getElementById('saveWebhookBtn'),
    
    // Chat
    chatMessages: document.getElementById('chatMessages'),
    chatInput: document.getElementById('chatInput'),
    chatSendBtn: document.getElementById('chatSendBtn'),
    
    // Toast
    toastContainer: document.getElementById('toastContainer')
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

function generateSessionId() {
    return 'sess_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
}

function showToast(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        info: 'ℹ️',
        success: '✅',
        error: '❌',
        warning: '⚠️'
    };
    
    toast.innerHTML = `
        <span>${icons[type] || 'ℹ️'}</span>
        <span>${message}</span>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function addChatMessage(text, sender = 'system') {
    const message = document.createElement('div');
    message.className = `message ${sender}`;
    message.innerHTML = `<p>${text}</p>`;
    elements.chatMessages.appendChild(message);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function updatePhaseIndicator(phase) {
    state.currentPhase = phase;
    
    document.querySelectorAll('.phase-step').forEach(step => {
        step.classList.remove('active', 'completed');
        
        const stepPhase = step.dataset.phase;
        const phases = ['upload', 'phase1', 'phase2', 'phase3', 'phase4', 'execute'];
        const currentIndex = phases.indexOf(phase);
        const stepIndex = phases.indexOf(stepPhase);
        
        if (stepIndex < currentIndex) {
            step.classList.add('completed');
        } else if (stepPhase === phase) {
            step.classList.add('active');
        }
    });
    
    // Show/hide sections
    const sections = {
        'upload': 'uploadSection',
        'phase1': 'phase1Section',
        'phase2': 'phase2Section',
        'phase3': 'phase3Section',
        'phase4': 'phase4Section',
        'execute': 'executeSection'
    };
    
    Object.entries(sections).forEach(([phaseName, sectionId]) => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.hidden = phaseName !== phase;
        }
    });
}

function formatTimestamp(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// ============================================
// API FUNCTIONS
// ============================================

async function apiCall(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

// ============================================
// UPLOAD HANDLERS
// ============================================

function initUploadHandlers() {
    // File input change
    elements.fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    elements.uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.add('dragover');
    });
    
    elements.uploadZone.addEventListener('dragleave', () => {
        elements.uploadZone.classList.remove('dragover');
    });
    
    elements.uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    });
    
    // Click to browse
    elements.uploadZone.addEventListener('click', (e) => {
        if (e.target !== elements.fileInput) {
            elements.fileInput.click();
        }
    });
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

async function uploadFile(file) {
    // Validate file
    if (!CONFIG.ALLOWED_TYPES.includes(file.type)) {
        showToast('Invalid file type. Please upload MP4, MOV, AVI, or WebM.', 'error');
        return;
    }
    
    if (file.size > CONFIG.MAX_FILE_SIZE) {
        showToast('File too large. Maximum size is 2GB.', 'error');
        return;
    }
    
    // Initialize session
    if (!state.sessionId) {
        state.sessionId = generateSessionId();
        elements.sessionId.textContent = state.sessionId;
    }
    
    // Show progress
    elements.uploadZone.querySelector('.upload-content').hidden = true;
    elements.uploadProgress.hidden = false;
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', state.sessionId);
    
    // Upload with progress
    try {
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                elements.progressFill.style.width = percentComplete + '%';
                elements.progressText.textContent = `Uploading... ${Math.round(percentComplete)}%`;
            }
        });
        
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                
                state.videoUploaded = true;
                elements.uploadedFilename.textContent = response.filename;
                elements.uploadedFile.hidden = false;
                
                showToast('Video uploaded successfully!', 'success');
                addChatMessage(`Video "${response.filename}" uploaded. Ready to begin editing.`, 'assistant');
                
                updatePhaseIndicator('phase1');
            } else {
                showToast('Upload failed. Please try again.', 'error');
                resetUpload();
            }
        });
        
        xhr.addEventListener('error', () => {
            showToast('Upload error. Please check your connection.', 'error');
            resetUpload();
        });
        
        xhr.open('POST', `${CONFIG.API_BASE_URL}/api/upload`);
        xhr.send(formData);
        
    } catch (error) {
        showToast('Upload failed: ' + error.message, 'error');
        resetUpload();
    }
}

function resetUpload() {
    elements.uploadZone.querySelector('.upload-content').hidden = false;
    elements.uploadProgress.hidden = true;
    elements.progressFill.style.width = '0%';
    elements.fileInput.value = '';
}

// ============================================
// PHASE 1: PROMPT REFINEMENT
// ============================================

function initPhase1Handlers() {
    elements.refinePromptBtn.addEventListener('click', refinePrompt);
    elements.approvePromptBtn.addEventListener('click', () => approvePrompt(true));
    elements.revisePromptBtn.addEventListener('click', showRevisionArea);
    elements.submitRevisionBtn.addEventListener('click', submitRevision);
}

async function refinePrompt() {
    const prompt = elements.originalPrompt.value.trim();
    
    if (!prompt) {
        showToast('Please enter a prompt first.', 'warning');
        return;
    }
    
    elements.refinePromptBtn.disabled = true;
    elements.refinePromptBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refining...';
    
    try {
        const response = await apiCall('/api/phase1/refine', {
            method: 'POST',
            body: JSON.stringify({
                session_id: state.sessionId,
                original_prompt: prompt
            })
        });
        
        displayRefinementResult(response.result);
        state.promptRefined = true;
        
        addChatMessage('Prompt refined! Please review the improvements.', 'assistant');
        
    } catch (error) {
        console.error('Refinement error:', error);
    } finally {
        elements.refinePromptBtn.disabled = false;
        elements.refinePromptBtn.innerHTML = '<i class="fas fa-sparkles"></i> Refine Prompt';
    }
}

function displayRefinementResult(result) {
    elements.displayOriginal.textContent = result.original_prompt;
    elements.displayImproved.textContent = result.improved_prompt;
    
    // Issues
    elements.issuesList.innerHTML = result.issues_detected
        .map(issue => `<li>${issue}</li>`)
        .join('');
    
    // Improvements
    elements.improvementsList.innerHTML = result.improvements_made
        .map(imp => `<li>${imp}</li>`)
        .join('');
    
    elements.refinementResult.hidden = false;
}

async function approvePrompt(approved) {
    try {
        const response = await apiCall('/api/phase1/approve', {
            method: 'POST',
            body: JSON.stringify({
                session_id: state.sessionId,
                approved: approved
            })
        });
        
        if (approved) {
            state.promptApproved = true;
            showToast('Prompt approved! Moving to Phase 2.', 'success');
            addChatMessage('Great! Now let\'s gather some details about your project.', 'assistant');
            updatePhaseIndicator('phase2');
            loadQuestions();
        }
        
    } catch (error) {
        console.error('Approval error:', error);
    }
}

function showRevisionArea() {
    elements.revisionArea.hidden = false;
    elements.revisionFeedback.focus();
}

async function submitRevision() {
    const feedback = elements.revisionFeedback.value.trim();
    
    if (!feedback) {
        showToast('Please provide feedback for the revision.', 'warning');
        return;
    }
    
    elements.submitRevisionBtn.disabled = true;
    elements.submitRevisionBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Revising...';
    
    try {
        const response = await apiCall('/api/phase1/approve', {
            method: 'POST',
            body: JSON.stringify({
                session_id: state.sessionId,
                approved: false,
                feedback: feedback
            })
        });
        
        displayRefinementResult(response.result);
        elements.revisionArea.hidden = false;
        elements.revisionFeedback.value = '';
        
        showToast('New revision generated!', 'success');
        
    } catch (error) {
        console.error('Revision error:', error);
    } finally {
        elements.submitRevisionBtn.disabled = false;
        elements.submitRevisionBtn.innerHTML = '<i class="fas fa-redo"></i> Submit Revision';
    }
}

// ============================================
// PHASE 2: INTELLIGENT QUESTIONING
// ============================================

async function loadQuestions() {
    try {
        const response = await apiCall('/api/phase2/questions', {
            method: 'POST',
            body: JSON.stringify({
                session_id: state.sessionId
            })
        });
        
        displayQuestions(response.questions);
        
        elements.totalQuestions.textContent = response.total_questions;
        updateAnsweredCount();
        
    } catch (error) {
        console.error('Load questions error:', error);
    }
}

function displayQuestions(questions) {
    elements.questionsContainer.innerHTML = '';
    
    questions.forEach((q, index) => {
        const card = document.createElement('div');
        card.className = 'question-card';
        card.dataset.questionId = q.id;
        
        let optionsHtml = '';
        
        if (q.type === 'single_choice' && q.options) {
            optionsHtml = q.options.map((opt, i) => `
                <label class="option-label">
                    <input type="radio" name="${q.id}" value="${opt}" 
                           onchange="handleAnswer('${q.id}', '${opt}')">
                    <span>${opt}</span>
                </label>
            `).join('');
        } else if (q.type === 'multiple_choice' && q.options) {
            optionsHtml = q.options.map((opt, i) => `
                <label class="option-label">
                    <input type="checkbox" name="${q.id}" value="${opt}"
                           onchange="handleMultipleAnswer('${q.id}', '${opt}', this.checked)">
                    <span>${opt}</span>
                </label>
            `).join('');
        } else if (q.type === 'text') {
            optionsHtml = `
                <textarea class="prompt-textarea" rows="2" 
                    onchange="handleAnswer('${q.id}', this.value)"
                    placeholder="Enter your answer..."></textarea>
            `;
        }
        
        card.innerHTML = `
            <div class="question-header">
                <div class="question-category">${q.category}</div>
                <div class="question-text">${q.question}</div>
                ${q.help_text ? `<div class="question-help">${q.help_text}</div>` : ''}
            </div>
            <div class="question-options">
                ${optionsHtml}
            </div>
        `;
        
        elements.questionsContainer.appendChild(card);
    });
}

function handleAnswer(questionId, value) {
    state.answers[questionId] = value;
    updateAnsweredCount();
    checkCanProceed();
}

function handleMultipleAnswer(questionId, value, checked) {
    if (!state.answers[questionId]) {
        state.answers[questionId] = [];
    }
    
    if (checked) {
        state.answers[questionId].push(value);
    } else {
        state.answers[questionId] = state.answers[questionId].filter(v => v !== value);
    }
    
    updateAnsweredCount();
    checkCanProceed();
}

function updateAnsweredCount() {
    const count = Object.keys(state.answers).length;
    elements.answeredCount.textContent = count;
}

function checkCanProceed() {
    const total = parseInt(elements.totalQuestions.textContent);
    const answered = parseInt(elements.answeredCount.textContent);
    
    elements.submitAnswersBtn.disabled = answered < total * 0.8; // 80% threshold
}

function initPhase2Handlers() {
    elements.submitAnswersBtn.addEventListener('click', submitAnswers);
}

async function submitAnswers() {
    // Submit all answers
    for (const [questionId, answer] of Object.entries(state.answers)) {
        try {
            await apiCall('/api/phase2/answer', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: state.sessionId,
                    question_id: questionId,
                    answer: answer
                })
            });
        } catch (error) {
            console.error(`Error submitting answer for ${questionId}:`, error);
        }
    }
    
    state.questionsAnswered = true;
    showToast('Answers submitted! Analyzing narrative...', 'success');
    addChatMessage('Perfect! Now I\'ll analyze the narrative structure.', 'assistant');
    
    updatePhaseIndicator('phase3');
    startNarrativeAnalysis();
}

// ============================================
// PHASE 3: NARRATIVE REASONING
// ============================================

async function startNarrativeAnalysis() {
    elements.narrativeProcessing.hidden = false;
    elements.narrativeSummary.hidden = true;
    
    try {
        const response = await apiCall('/api/phase3/analyze', {
            method: 'POST',
            body: JSON.stringify({
                session_id: state.sessionId
            })
        });
        
        displayNarrativeSummary(response.narrative_summary);
        
        state.narrativeAnalyzed = true;
        
    } catch (error) {
        console.error('Narrative analysis error:', error);
        showToast('Narrative analysis failed. Please try again.', 'error');
    }
}

function displayNarrativeSummary(summary) {
    elements.narrativeProcessing.hidden = true;
    elements.narrativeSummary.hidden = false;
    
    elements.narrativeArc.textContent = summary.arc || 'Documentary-style narrative';
    elements.dominantTone.textContent = summary.tone || 'Neutral';
    elements.pacingInfo.textContent = 'Medium-paced with emotional beats';
}

function initPhase3Handlers() {
    elements.continueToPlanningBtn.addEventListener('click', () => {
        updatePhaseIndicator('phase4');
        startScenePlanning();
    });
}

// ============================================
// PHASE 4: SCENE PLANNING
// ============================================

async function startScenePlanning() {
    elements.scenePlanningProcessing.hidden = false;
    elements.scenePlan.hidden = true;
    
    try {
        const response = await apiCall('/api/phase4/plan', {
            method: 'POST',
            body: JSON.stringify({
                session_id: state.sessionId
            })
        });
        
        displayScenePlan(response.scene_plan);
        
        state.scenePlanned = true;
        addChatMessage('Scene plan complete! Review the cinematic sequence below.', 'assistant');
        
    } catch (error) {
        console.error('Scene planning error:', error);
        showToast('Scene planning failed. Please try again.', 'error');
    }
}

function displayScenePlan(plan) {
    elements.scenePlanningProcessing.hidden = true;
    elements.scenePlan.hidden = false;
    
    // Header
    elements.planTitle.textContent = plan.title;
    elements.planTheme.textContent = plan.theme;
    elements.planFormat.textContent = plan.format;
    elements.planStyle.textContent = plan.style;
    
    // Scenes timeline
    elements.scenesTimeline.innerHTML = plan.scenes.map(scene => `
        <div class="scene-card">
            <div class="scene-number">${scene.scene_id}</div>
            <div class="scene-content">
                <h4>${scene.goal}</h4>
                <div class="scene-meta">
                    <span><i class="fas fa-eye"></i> ${scene.visual.substring(0, 50)}...</span>
                    <span><i class="fas fa-volume-up"></i> ${scene.audio}</span>
                    ${scene.voice_over_text ? '<span><i class="fas fa-microphone"></i> VO</span>' : ''}
                </div>
                <div class="scene-description">
                    ${scene.visual}
                </div>
            </div>
            <div class="scene-timestamp">
                ${scene.start} - ${scene.end}
            </div>
        </div>
    `).join('');
    
    // Store plan for export
    state.currentPlan = plan;
}

function initPhase4Handlers() {
    elements.executePlanBtn.addEventListener('click', executePlan);
    elements.exportPlanBtn.addEventListener('click', exportPlan);
}

async function executePlan() {
    updatePhaseIndicator('execute');
    
    showToast('Starting video execution...', 'info');
    addChatMessage('Beginning video edit execution. This may take several minutes.', 'assistant');
    
    // Simulate execution steps
    const steps = [
        { id: 'progressCut', name: 'Video Cuts', delay: 2000 },
        { id: 'progressVoice', name: 'Voice-Over', delay: 3000 },
        { id: 'progressSubtitles', name: 'Subtitles', delay: 2000 },
        { id: 'progressRender', name: 'Final Render', delay: 5000 }
    ];
    
    for (const step of steps) {
        const el = document.getElementById(step.id);
        el.classList.add('processing');
        el.querySelector('.status').textContent = 'Processing...';
        
        await new Promise(r => setTimeout(r, step.delay));
        
        el.classList.remove('processing');
        el.classList.add('complete');
        el.querySelector('.status').textContent = 'Complete';
    }
    
    elements.executionProgress.hidden = true;
    elements.executionComplete.hidden = false;
    
    showToast('Video edit complete!', 'success');
    addChatMessage('Your cinematic edit is ready! Click download to get your video.', 'assistant');
}

function exportPlan() {
    if (!state.currentPlan) {
        showToast('No plan to export.', 'warning');
        return;
    }
    
    const dataStr = JSON.stringify(state.currentPlan, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `scene-plan-${state.sessionId}.json`;
    link.click();
    
    showToast('Scene plan exported!', 'success');
}

// ============================================
// WEBHOOK CONFIGURATION
// ============================================

const WEBHOOK_EVENTS = [
    'VIDEO_UPLOAD_STARTED', 'VIDEO_UPLOAD_COMPLETED',
    'AUDIO_TRANSCRIPTION_STARTED', 'AUDIO_TRANSCRIPTION_COMPLETED',
    'VISUAL_ANALYSIS_STARTED', 'VISUAL_ANALYSIS_COMPLETED',
    'PROMPT_REFINEMENT_STARTED', 'PROMPT_REFINEMENT_IMPROVED', 'PROMPT_REFINEMENT_APPROVED',
    'INTELLIGENT_QUESTIONING_STARTED', 'INTELLIGENT_QUESTIONING_COMPLETED',
    'NARRATIVE_REASONING_STARTED', 'NARRATIVE_REASONING_COMPLETED',
    'SCENE_PLANNING_STARTED', 'SCENE_PLANNING_COMPLETED',
    'VIDEO_CUT_CREATION', 'VOICE_OVER_GENERATION', 'SUBTITLE_GENERATION',
    'FINAL_RENDER_STARTED', 'FINAL_RENDER_COMPLETED',
    'ERROR', 'WARNING'
];

function initWebhookHandlers() {
    // Generate event checkboxes
    elements.eventCheckboxes.innerHTML = '<h4>Notify on Events:</h4>' + 
        WEBHOOK_EVENTS.map(event => `
            <label class="event-checkbox">
                <input type="checkbox" value="${event}" checked>
                <span>${event.replace(/_/g, ' ').toLowerCase()}</span>
            </label>
        `).join('');
    
    // Test webhook
    elements.testWebhookBtn.addEventListener('click', testWebhook);
    
    // Save configuration
    elements.saveWebhookBtn.addEventListener('click', saveWebhookConfig);
}

async function testWebhook() {
    const url = elements.webhookUrl.value.trim();
    
    if (!url) {
        showToast('Please enter a webhook URL first.', 'warning');
        return;
    }
    
    if (!url.startsWith('https://discord.com/api/webhooks/')) {
        showToast('Invalid Discord webhook URL format.', 'error');
        return;
    }
    
    elements.testWebhookBtn.disabled = true;
    elements.testWebhookBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    try {
        // Send test notification
        const response = await apiCall('/api/webhook/config', {
            method: 'POST',
            body: JSON.stringify({
                session_id: state.sessionId || generateSessionId(),
                webhook_config: {
                    webhook_url: url,
                    enabled: true,
                    events: { 'WEBHOOK_TEST': true }
                }
            })
        });
        
        showToast('Test notification sent! Check Discord.', 'success');
        
    } catch (error) {
        showToast('Test failed. Check your webhook URL.', 'error');
    } finally {
        elements.testWebhookBtn.disabled = false;
        elements.testWebhookBtn.textContent = 'Test';
    }
}

async function saveWebhookConfig() {
    const url = elements.webhookUrl.value.trim();
    const enabled = elements.webhookEnabled.checked;
    
    // Collect enabled events
    const events = {};
    elements.eventCheckboxes.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        events[cb.value] = cb.checked;
    });
    
    state.webhookConfig = {
        webhook_url: url,
        enabled: enabled,
        events: events
    };
    
    try {
        const response = await apiCall('/api/webhook/config', {
            method: 'POST',
            body: JSON.stringify({
                session_id: state.sessionId || generateSessionId(),
                webhook_config: state.webhookConfig
            })
        });
        
        showToast('Webhook configuration saved!', 'success');
        
    } catch (error) {
        console.error('Save webhook error:', error);
    }
}

// ============================================
// CHAT HANDLERS
// ============================================

function initChatHandlers() {
    elements.chatSendBtn.addEventListener('click', sendChatMessage);
    elements.chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

function sendChatMessage() {
    const text = elements.chatInput.value.trim();
    if (!text) return;
    
    addChatMessage(text, 'user');
    elements.chatInput.value = '';
    
    // Simple response logic (in production, this would connect to backend)
    setTimeout(() => {
        const responses = [
            'I understand. Let me help you with that.',
            'Good point! I\'ll take that into consideration.',
            'Thanks for the clarification.',
            'I\'m processing your request...'
        ];
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        addChatMessage(randomResponse, 'assistant');
    }, 1000);
}

// ============================================
// WEBSOCKET (if needed for real-time updates)
// ============================================

function initWebSocket() {
    // Socket.io is loaded from CDN
    if (typeof io !== 'undefined') {
        const socket = io(CONFIG.WS_URL);
        
        socket.on('connect', () => {
            console.log('WebSocket connected');
            if (state.sessionId) {
                socket.emit('join_session', { session_id: state.sessionId });
            }
        });
        
        socket.on('upload_complete', (data) => {
            console.log('Upload complete:', data);
        });
        
        socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
        });
    }
}

// ============================================
// INITIALIZATION
// ============================================

function init() {
    // Initialize session
    state.sessionId = generateSessionId();
    elements.sessionId.textContent = state.sessionId;
    
    // Initialize all handlers
    initUploadHandlers();
    initPhase1Handlers();
    initPhase2Handlers();
    initPhase3Handlers();
    initPhase4Handlers();
    initWebhookHandlers();
    initChatHandlers();
    initWebSocket();
    
    // Welcome message
    addChatMessage('Welcome! I\'m your AI Cinematic Director. Upload a video to begin the editing process.', 'assistant');
    
    console.log('AI Cinematic Video Editor Pro initialized');
    console.log('Session ID:', state.sessionId);
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
