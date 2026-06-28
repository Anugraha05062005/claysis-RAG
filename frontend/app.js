document.addEventListener("DOMContentLoaded", () => {
    // API base URL configuration (empty means same domain)
    const API_BASE = "";

    // DOM Elements
    const seedUrlInput = document.getElementById("seed-url");
    const crawlDepthInput = document.getElementById("crawl-depth");
    const depthValText = document.getElementById("depth-val");
    const crawlForm = document.getElementById("crawl-form");
    const crawlSubmitBtn = document.getElementById("crawl-submit-btn");
    const crawlStatus = document.getElementById("crawl-status");

    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const uploadProgressList = document.getElementById("upload-progress-list");

    const sourcesList = document.getElementById("sources-list");
    const clearDbBtn = document.getElementById("clear-db-btn");
    const sourceFilterSelect = document.getElementById("source-filter");

    const chatMessages = document.getElementById("chat-messages-container");
    const chatForm = document.getElementById("chat-form");
    const queryInput = document.getElementById("query-input");
    const searchModeSelect = document.getElementById("search-mode");
    const querySubmitBtn = document.getElementById("query-submit-btn");

    const toggleSettingsBtn = document.getElementById("toggle-settings-btn");
    const settingsOverlay = document.getElementById("settings-overlay");
    const closeSettingsBtn = document.getElementById("close-settings-btn");
    const settingsForm = document.getElementById("settings-form");
    const settingsGroqKey = document.getElementById("settings-groq-key");
    const settingsOllamaModel = document.getElementById("settings-ollama-model");
    const settingsGroqModel = document.getElementById("settings-groq-model");
    const diagOllamaModel = document.getElementById("diag-ollama-model");
    
    const ollamaStatusDot = document.getElementById("ollama-status-dot");
    const ollamaStatusText = document.getElementById("ollama-status-text");

    // Dynamic slider label
    crawlDepthInput.addEventListener("input", (e) => {
        depthValText.textContent = e.target.value;
    });

    // 1. Fetch current settings and test connection
    async function initSystem() {
        try {
            const resp = await fetch(`${API_BASE}/api/settings`);
            if (resp.ok) {
                const data = await resp.json();
                if (data.groq_api_key_masked) {
                    settingsGroqKey.placeholder = "Saved: " + data.groq_api_key_masked;
                }
                settingsOllamaModel.value = data.ollama_model;
                settingsGroqModel.value = data.groq_model;
                diagOllamaModel.textContent = data.ollama_model;
            }
            
            // Check Ollama status
            checkOllamaConnection();
            
            // Load sources list
            loadSources();
        } catch (err) {
            console.error("System init failed:", err);
            setOllamaStatus(false, "Offline");
        }
    }

    async function checkOllamaConnection() {
        try {
            // Standard Ollama connection test via local server endpoint (or a proxy call)
            // We can just verify if the local system endpoint is reachable by the browser, 
            // but since it runs locally, we can make a direct fetch to the local port (with CORS allowed).
            // If that fails, we can assume it's not running.
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), 2000);
            
            const resp = await fetch("http://localhost:11434/", { 
                method: "GET", 
                signal: controller.signal 
            });
            clearTimeout(id);
            if (resp.ok) {
                setOllamaStatus(true, "Ollama Active");
            } else {
                setOllamaStatus(false, "Ollama Error", true);
            }
        } catch (err) {
            setOllamaStatus(false, "Ollama Offline", true);
        }
    }

    function setOllamaStatus(active, text, isWarning = false) {
        ollamaStatusDot.className = "indicator-dot";
        if (active) {
            ollamaStatusDot.classList.add("active");
            ollamaStatusText.textContent = text;
        } else {
            if (isWarning) {
                ollamaStatusDot.classList.add("warning");
            }
            ollamaStatusText.textContent = text;
        }
    }

    // 2. Settings Modal Events
    toggleSettingsBtn.addEventListener("click", () => settingsOverlay.classList.remove("hidden"));
    closeSettingsBtn.addEventListener("click", () => settingsOverlay.classList.add("hidden"));
    settingsOverlay.addEventListener("click", (e) => {
        if (e.target === settingsOverlay) settingsOverlay.classList.add("hidden");
    });

    settingsForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = {
            groq_api_key: settingsGroqKey.value || null,
            ollama_model: settingsOllamaModel.value,
            groq_model: settingsGroqModel.value
        };

        try {
            const resp = await fetch(`${API_BASE}/api/settings`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (resp.ok) {
                alert("Settings updated successfully!");
                settingsOverlay.classList.add("hidden");
                settingsGroqKey.value = ""; // clear field input
                initSystem();
            } else {
                alert("Failed to save settings.");
            }
        } catch (err) {
            alert("Error saving settings: " + err);
        }
    });

    // 3. Web Ingestion (Crawl) Events
    crawlForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const seedUrl = seedUrlInput.value.strip ? seedUrlInput.value.strip() : seedUrlInput.value.trim();
        const depth = parseInt(crawlDepthInput.value, 10);

        if (!seedUrl) return;

        // UI Feedback
        crawlSubmitBtn.disabled = true;
        crawlSubmitBtn.innerHTML = '<i class="fa-solid fa-spider spinner-icon"></i> Crawling site...';
        crawlStatus.className = "status-msg info";
        crawlStatus.textContent = "Recursive crawling in progress. This may take a minute depending on depth...";
        crawlStatus.classList.remove("hidden");

        try {
            const resp = await fetch(`${API_BASE}/api/crawl`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: seedUrl, depth: depth })
            });

            const data = await resp.json();
            if (resp.ok && data.status === "success") {
                crawlStatus.className = "status-msg success";
                crawlStatus.textContent = `Completed: Indexed ${data.indexed_pages} pages (${data.new_chunks} chunks). Latency: ${data.latency_ms}ms`;
                seedUrlInput.value = "";
                loadSources();
            } else {
                crawlStatus.className = "status-msg error";
                crawlStatus.textContent = `Warning: ${data.message || "Crawl completed but no contents could be indexed."}`;
            }
        } catch (err) {
            crawlStatus.className = "status-msg error";
            crawlStatus.textContent = "Error: Failed to connect to backend crawling pipeline.";
        } finally {
            crawlSubmitBtn.disabled = false;
            crawlSubmitBtn.innerHTML = '<i class="fa-solid fa-spider"></i> Start Web Crawling';
        }
    });

    // 4. File Upload Ingest (Drag & Drop)
    dropZone.addEventListener("click", () => fileInput.click());
    
    // Prevent default behaviors for Drag & Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFilesUpload(files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFilesUpload(e.target.files);
    });

    function handleFilesUpload(files) {
        if (!files.length) return;
        Array.from(files).forEach(file => {
            uploadSingleFile(file);
        });
    }

    async function uploadSingleFile(file) {
        // Create progress UI item
        const progressId = "progress-" + Math.random().toString(36).substring(2, 9);
        const progressHTML = `
            <div class="progress-item" id="${progressId}">
                <div class="progress-info">
                    <span class="file-name">${file.name}</span>
                    <span class="progress-percent" id="${progressId}-percent">0%</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="${progressId}-bar"></div>
                </div>
            </div>
        `;
        uploadProgressList.insertAdjacentHTML("afterbegin", progressHTML);

        const formData = new FormData();
        formData.append("file", file);

        const xhr = new XMLHttpRequest();
        xhr.open("POST", `${API_BASE}/api/upload`, true);

        // Track progress
        xhr.upload.addEventListener("progress", (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                document.getElementById(`${progressId}-percent`).textContent = percent + "%";
                document.getElementById(`${progressId}-bar`).style.width = percent + "%";
            }
        });

        xhr.onload = function() {
            const item = document.getElementById(progressId);
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                if (data.status === "success") {
                    item.style.borderColor = "var(--color-success)";
                    document.getElementById(`${progressId}-percent`).innerHTML = `<i class="fa-solid fa-check" style="color: var(--color-success)"></i> Indexed`;
                } else {
                    item.style.borderColor = "var(--color-warning)";
                    document.getElementById(`${progressId}-percent`).innerHTML = `<i class="fa-solid fa-circle-exclamation" style="color: var(--color-warning)"></i> Already Indexed`;
                }
                loadSources();
            } else {
                item.style.borderColor = "var(--color-danger)";
                document.getElementById(`${progressId}-percent`).innerHTML = `<i class="fa-solid fa-xmark" style="color: var(--color-danger)"></i> Error`;
            }
            // Auto fadeout after 5s
            setTimeout(() => {
                item.remove();
            }, 6000);
        };

        xhr.onerror = function() {
            const item = document.getElementById(progressId);
            item.style.borderColor = "var(--color-danger)";
            document.getElementById(`${progressId}-percent`).innerHTML = `<i class="fa-solid fa-xmark" style="color: var(--color-danger)"></i> Failed`;
        };

        xhr.send(formData);
    }

    // 5. Load Sources Register
    async function loadSources() {
        try {
            const resp = await fetch(`${API_BASE}/api/sources`);
            if (resp.ok) {
                const data = await resp.json();
                
                // Clear active
                sourcesList.innerHTML = "";
                
                // Backup option select values
                const currentFilter = sourceFilterSelect.value;
                sourceFilterSelect.innerHTML = '<option value="">All Ingested Sources</option>';

                if (data.length === 0) {
                    sourcesList.innerHTML = '<div class="empty-sources-msg">No sources ingested yet.</div>';
                    return;
                }

                data.forEach(source => {
                    // Map icon based on document/media format type
                    let icon = "fa-file-lines";
                    if (source.type === "pdf") icon = "fa-file-pdf";
                    else if (source.type === "docx") icon = "fa-file-word";
                    else if (source.type === "pptx") icon = "fa-file-powerpoint";
                    else if (source.type === "csv") icon = "fa-file-excel";
                    else if (source.type === "web") icon = "fa-globe";
                    else if (source.type === "image") icon = "fa-file-image";
                    else if (source.type === "audio") icon = "fa-file-audio";
                    else if (source.type === "video") icon = "fa-file-video";
                    else if (source.type === "sqlite") icon = "fa-database";
                    else if (source.type === "email") icon = "fa-envelope";

                    const itemHTML = `
                        <div class="source-item">
                            <i class="fa-solid ${icon} source-type-icon"></i>
                            <div class="source-details">
                                <p title="${source.name}">${source.name}</p>
                                <span>Type: ${source.type.toUpperCase()}</span>
                            </div>
                            <div class="source-badge">${source.chunks} chunks</div>
                        </div>
                    `;
                    sourcesList.insertAdjacentHTML("beforeend", itemHTML);

                    // Add to dropdown filters
                    const opt = document.createElement("option");
                    opt.value = source.name;
                    opt.textContent = `${source.name} (${source.type.toUpperCase()})`;
                    sourceFilterSelect.appendChild(opt);
                });

                // Restore previous filter if still available
                if (Array.from(sourceFilterSelect.options).some(o => o.value === currentFilter)) {
                    sourceFilterSelect.value = currentFilter;
                }
            }
        } catch (err) {
            console.error("Failed to load database sources list:", err);
        }
    }

    // 6. Reset Knowledge Base
    clearDbBtn.addEventListener("click", async () => {
        if (!confirm("Are you sure you want to completely clear the knowledge base and remove all indexed sources? This cannot be undone.")) return;
        
        try {
            const resp = await fetch(`${API_BASE}/api/clear`, { method: "POST" });
            if (resp.ok) {
                alert("Knowledge base has been completely reset.");
                loadSources();
                appendBotMessage("Knowledge base database has been reset. All indices and files cleared.");
            } else {
                alert("Failed to reset database.");
            }
        } catch (err) {
            alert("Error clearing database: " + err);
        }
    });

    // 7. Chat Query Submission
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const question = queryInput.value.trim();
        const mode = searchModeSelect.value;
        const sourceFilter = sourceFilterSelect.value;

        if (!question) return;

        // Add User Message Bubble
        appendUserMessage(question);
        queryInput.value = "";
        
        // Disable UI during search
        querySubmitBtn.disabled = true;
        queryInput.disabled = true;

        // Add Loading bubble
        const loadingId = appendLoadingMessage();

        try {
            const resp = await fetch(`${API_BASE}/api/query`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question: question,
                    source: sourceFilter || null,
                    mode: mode
                })
            });

            if (resp.ok) {
                const data = await resp.json();
                // Remove loading bubble
                removeMessageBubble(loadingId);
                
                // Add Bot answer bubble
                appendBotAnswerMessage(data);
            } else {
                removeMessageBubble(loadingId);
                appendBotMessage("Error: Failed to fetch response from API. Make sure the server backend is running.");
            }
        } catch (err) {
            removeMessageBubble(loadingId);
            appendBotMessage("Connection Error: Could not connect to RAG server. Verify server execution.");
        } finally {
            querySubmitBtn.disabled = false;
            queryInput.disabled = false;
            queryInput.focus();
        }
    });

    // Message Render Helpers
    function appendUserMessage(text) {
        const bubbleHTML = `
            <div class="user-message message-block">
                <div class="message-avatar">
                    <i class="fa-solid fa-user"></i>
                </div>
                <div class="message-content-wrapper">
                    <div class="message-text">${escapeHTML(text)}</div>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML("beforeend", bubbleHTML);
        scrollToBottom();
    }

    function appendBotMessage(text) {
        const bubbleHTML = `
            <div class="bot-message message-block">
                <div class="message-avatar">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="message-content-wrapper">
                    <div class="message-text">${text}</div>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML("beforeend", bubbleHTML);
        scrollToBottom();
    }

    function appendLoadingMessage() {
        const id = "loading-" + Math.random().toString(36).substring(2, 9);
        const bubbleHTML = `
            <div class="bot-message message-block" id="${id}">
                <div class="message-avatar">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="message-content-wrapper">
                    <div class="message-text">
                        <i class="fa-solid fa-ellipsis fa-bounce" style="color: var(--color-primary)"></i> Thinking...
                    </div>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML("beforeend", bubbleHTML);
        scrollToBottom();
        return id;
    }

    function removeMessageBubble(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function appendBotAnswerMessage(data) {
        // Parse basic markdown formatting inside the answer (like **, * lists, line breaks)
        const parsedAnswer = parseSimpleMarkdown(data.answer);
        
        let sourcesHTML = "";
        if (data.sources && data.sources.length > 0) {
            sourcesHTML = `
                <div class="message-sources">
                    <div class="sources-title">
                        <i class="fa-solid fa-quote-left"></i> Source References (${data.sources.length})
                    </div>
                    <div class="sources-cards-grid">
            `;
            
            data.sources.forEach((src, idx) => {
                // Map icon based on document/media format type
                let icon = "fa-file-lines";
                if (src.type === "pdf") icon = "fa-file-pdf";
                else if (src.type === "docx") icon = "fa-file-word";
                else if (src.type === "pptx") icon = "fa-file-powerpoint";
                else if (src.type === "csv") icon = "fa-file-excel";
                else if (src.type === "web") icon = "fa-globe";
                else if (src.type === "image") icon = "fa-file-image";
                else if (src.type === "audio") icon = "fa-file-audio";
                else if (src.type === "video") icon = "fa-file-video";
                else if (src.type === "sqlite") icon = "fa-database";
                else if (src.type === "email") icon = "fa-envelope";

                const tsBadge = src.timestamp ? `<span class="ref-timestamp"><i class="fa-solid fa-clock"></i> ${src.timestamp}</span>` : "";
                
                const cardId = `ref-card-${Math.random().toString(36).substring(2, 9)}`;
                
                sourcesHTML += `
                    <div class="source-ref-card" onclick="toggleSourceSnippet('${cardId}')">
                        <div class="ref-card-header">
                            <i class="fa-solid ${icon} ref-type-icon"></i>
                            <span class="ref-card-title" title="${src.reference}">${src.reference}</span>
                            ${tsBadge}
                        </div>
                        <div class="ref-snippet">${escapeHTML(src.text)}</div>
                    </div>
                    <div class="source-snippet-expanded" id="${cardId}">
                        <strong>Snippet Reference [${src.heading || 'Section'}]:</strong>
                        <p style="margin-top: 6px; white-space: pre-wrap;">${escapeHTML(src.text)}</p>
                    </div>
                `;
            });
            
            sourcesHTML += `
                    </div>
                </div>
            `;
        }

        const modelIcon = data.llm_provider === "ollama" ? "fa-cube" : "fa-cloud-bolt";
        const modelLabel = data.llm_provider === "ollama" ? "Local Ollama" : "Groq Fallback";

        const bubbleHTML = `
            <div class="bot-message message-block animate-fade">
                <div class="message-avatar">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="message-content-wrapper">
                    <div class="message-text">${parsedAnswer}</div>
                    ${sourcesHTML}
                    <div class="message-footer">
                        <span class="provider-badge"><i class="fa-solid ${modelIcon}"></i> ${modelLabel}</span>
                        <span>Latency: ${data.latency_ms} ms</span>
                    </div>
                </div>
            </div>
        `;
        
        chatMessages.insertAdjacentHTML("beforeend", bubbleHTML);
        scrollToBottom();
    }

    // Helper: toggle visibility of raw chunk text
    window.toggleSourceSnippet = function(id) {
        const el = document.getElementById(id);
        if (el) {
            if (el.style.display === "block") {
                el.style.display = "none";
            } else {
                el.style.display = "block";
            }
        }
    };

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHTML(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function parseSimpleMarkdown(text) {
        if (!text) return "";
        let html = escapeHTML(text);
        
        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        
        // Unordered lists
        html = html.replace(/^\*\s+(.*?)$/gm, "<li>$1</li>");
        // wrap lists
        html = html.replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>");
        
        // Ordered lists
        html = html.replace(/^\d+\.\s+(.*?)$/gm, "<li>$1</li>");
        
        // Code fragments
        html = html.replace(/`(.*?)`/g, "<code>$1</code>");
        
        // Linebreaks
        html = html.replace(/\n/g, "<br>");
        
        return html;
    }

    // Run system initiation
    initSystem();
});
