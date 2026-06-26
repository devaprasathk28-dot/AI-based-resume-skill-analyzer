// Theme Toggle Logic
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (!themeToggleBtn) return;
    
    if (theme === 'dark') {
        themeToggleBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>
            </svg>
        `;
    } else {
        themeToggleBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
            </svg>
        `;
    }
}

// Drag & Drop File Upload Handler
function initDragAndDrop() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const resumeTextarea = document.getElementById('resume_text');
    const fileInfo = document.getElementById('file-info');
    const fileNameSpan = document.getElementById('file-name');

    if (!dropzone || !fileInput || !resumeTextarea) return;

    // Trigger click on file input when dropzone is clicked
    dropzone.addEventListener('click', () => fileInput.click());

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight dropzone on drag cover
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
    });

    // Handle dropped files
    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) handleFile(files[0]);
    });

    // Handle selected files
    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length) handleFile(fileInput.files[0]);
    });

    // Extract text from file
    async function handleFile(file) {
        fileNameSpan.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        fileInfo.style.display = 'inline-flex';
        
        const fileType = file.type;
        const extension = file.name.split('.').pop().toLowerCase();

        if (extension === 'pdf') {
            const reader = new FileReader();
            reader.onload = async function() {
                try {
                    const typedarray = new Uint8Array(this.result);
                    resumeTextarea.value = "Extracting text from PDF, please wait...";
                    const text = await extractTextFromPDF(typedarray);
                    resumeTextarea.value = text.trim() || "No readable text found in PDF.";
                } catch (err) {
                    console.error("PDF Parsing Error:", err);
                    resumeTextarea.value = "Failed to parse PDF file. Please paste your text manually.";
                }
            };
            reader.readAsArrayBuffer(file);
        } else if (extension === 'txt') {
            const reader = new FileReader();
            reader.onload = function(e) {
                resumeTextarea.value = e.target.result;
            };
            reader.readAsText(file);
        } else {
            alert("Supported formats are PDF and TXT. For other files, please copy & paste text directly.");
            fileInfo.style.display = 'none';
        }
    }
}

// Extract PDF text using PDF.js (CDN-loaded)
async function extractTextFromPDF(typedarray) {
    if (typeof pdfjsLib === 'undefined') {
        throw new Error('PDF.js is not loaded yet.');
    }
    
    // Set worker source
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
    
    const pdf = await pdfjsLib.getDocument({ data: typedarray }).promise;
    let text = "";
    
    for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map(item => item.str).join(" ");
        text += pageText + "\n";
    }
    return text;
}

// LocalStorage History Sync
function saveAnalysisToHistory(data) {
    let history = JSON.parse(localStorage.getItem('resume_analyzer_history')) || [];
    // Prevent duplicate entries by timestamp/name
    history.unshift(data); // Prepend to show latest first
    // Limit to latest 50 entries
    if (history.length > 50) history.pop();
    localStorage.setItem('resume_analyzer_history', JSON.stringify(history));
}

function loadHistoryTable() {
    const tableBody = document.getElementById('history-table-body');
    const emptyMsg = document.getElementById('history-empty-message');
    if (!tableBody) return;

    const history = JSON.parse(localStorage.getItem('resume_analyzer_history')) || [];
    
    if (history.length === 0) {
        if (emptyMsg) emptyMsg.style.display = 'block';
        tableBody.innerHTML = '';
        return;
    }

    if (emptyMsg) emptyMsg.style.display = 'none';
    
    tableBody.innerHTML = history.map((item, index) => {
        return `
            <tr>
                <td><strong>${escapeHtml(item.name)}</strong></td>
                <td>${escapeHtml(item.role)}</td>
                <td>${item.date}</td>
                <td>
                    <span class="pill pill-success" style="font-size: 0.85rem; padding: 4px 10px;">
                        ${item.score}%
                    </span>
                </td>
                <td style="text-align: right;">
                    <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.8rem; border-radius: 8px;" onclick="deleteHistoryItem(${index})">
                        Delete
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function deleteHistoryItem(index) {
    let history = JSON.parse(localStorage.getItem('resume_analyzer_history')) || [];
    history.splice(index, 1);
    localStorage.setItem('resume_analyzer_history', JSON.stringify(history));
    loadHistoryTable();
}

function clearAllHistory() {
    if (confirm("Are you sure you want to clear your local analysis logs?")) {
        localStorage.removeItem('resume_analyzer_history');
        loadHistoryTable();
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Interactive Score Simulator
function initInteractiveSimulator() {
    const checkBoxes = document.querySelectorAll('.sim-skill-check');
    const scoreText = document.getElementById('radial-score-text');
    const progressBar = document.getElementById('radial-progress-bar');
    
    if (!scoreText || !progressBar) return;
    
    const initialMatchedCount = parseInt(progressBar.getAttribute('data-matched-count') || 0);
    const totalSkillsCount = parseInt(progressBar.getAttribute('data-total-count') || 1);
    const circumference = 283; // 2 * PI * r (approx)

    function updateScoreDisplay() {
        let simulatedMatches = 0;
        checkBoxes.forEach(cb => {
            if (cb.checked) simulatedMatches++;
        });

        const totalMatched = initialMatchedCount + simulatedMatches;
        const currentPercentage = Math.round((totalMatched / totalSkillsCount) * 100);
        
        // Update circular bar dash offset
        const offset = circumference - (currentPercentage / 100) * circumference;
        progressBar.style.strokeDashoffset = offset;
        
        // Update center text percentage
        scoreText.textContent = `${currentPercentage}%`;
        
        // Dynamic color shifting for progress ring
        if (currentPercentage < 50) {
            progressBar.style.stroke = 'var(--danger)';
        } else if (currentPercentage < 75) {
            progressBar.style.stroke = 'var(--primary)';
        } else {
            progressBar.style.stroke = 'var(--success)';
        }
    }

    checkBoxes.forEach(cb => {
        cb.addEventListener('change', updateScoreDisplay);
    });

    // Run once on load to style correctly
    updateScoreDisplay();
}

// Initializations on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initDragAndDrop();
    initInteractiveSimulator();
    
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }
    
    // Analysis Method Switcher Toggle
    const methodRadios = document.querySelectorAll('input[name="analysis_method"]');
    const presetGroup = document.getElementById('preset-role-group');
    const customGroup = document.getElementById('custom-jd-group');
    const jobDescriptionTextarea = document.getElementById('job_description');

    if (methodRadios.length && presetGroup && customGroup) {
        methodRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.value === 'custom') {
                    presetGroup.style.display = 'none';
                    customGroup.style.display = 'block';
                    if (jobDescriptionTextarea) {
                        jobDescriptionTextarea.setAttribute('required', 'true');
                    }
                } else {
                    presetGroup.style.display = 'block';
                    customGroup.style.display = 'none';
                    if (jobDescriptionTextarea) {
                        jobDescriptionTextarea.removeAttribute('required');
                    }
                }
            });
        });
    }
    
    // If logs page, populate table
    if (document.getElementById('history-table-body')) {
        loadHistoryTable();
    }
});
