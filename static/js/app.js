/* WildGuard Report AI — app.js v2 */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Toast helper ── */
  const toastEl = document.getElementById('toast');
  function showToast(msg, duration = 3200) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    setTimeout(() => toastEl.classList.remove('show'), duration);
  }

  /* ── Progress bar ── */
  const progressBar = document.getElementById('progress-bar');
  function startProgress() {
    if (progressBar) progressBar.classList.add('active');
  }

  /* ── Upload / Drop Zone ── */
  const fileInput  = document.getElementById('file-input');
  const dropZone   = document.getElementById('drop-zone');
  const browseBtn  = document.getElementById('browse-btn');
  const uploadForm = document.getElementById('upload-form');

  if (dropZone && fileInput) {

    // Click on drop zone or browse button → open picker
    dropZone.addEventListener('click', (e) => {
      if (e.target !== browseBtn) fileInput.click();
    });
    if (browseBtn) browseBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      fileInput.click();
    });

    // Keyboard accessibility
    dropZone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        fileInput.click();
      }
    });

    // Drag events
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('drag-over');
    });

    ['dragleave', 'dragend'].forEach(type => {
      dropZone.addEventListener(type, () => dropZone.classList.remove('drag-over'));
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        const file = files[0];
        if (!file.name.toLowerCase().endsWith('.csv')) {
          showToast('⚠ Please upload a .csv file only.');
          return;
        }
        fileInput.files = files;
        submitWithProgress(uploadForm);
      }
    });

    // File picker change
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        if (!file.name.toLowerCase().endsWith('.csv')) {
          showToast('⚠ Please upload a .csv file only.');
          fileInput.value = '';
          return;
        }
        // Update drop zone label
        const label = dropZone.querySelector('.drop-title');
        if (label) label.textContent = `📄 ${file.name}`;
        submitWithProgress(uploadForm);
      }
    });
  }

  function submitWithProgress(form) {
    if (!form) return;
    startProgress();
    form.submit();
  }

  /* ── Demo data button ── */
  const demoBtn = document.getElementById('demo-btn');
  if (demoBtn) {
    demoBtn.addEventListener('click', (e) => {
      e.preventDefault();
      demoBtn.disabled = true;
      demoBtn.innerHTML = '<span class="spinner"></span> Loading demo…';
      startProgress();
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = '/use-demo';
      document.body.appendChild(form);
      form.submit();
    });
  }

  /* ── Prepare Report button (with loading state) ── */
  const prepareBtn = document.getElementById('prepare-report-btn');
  if (prepareBtn) {
    prepareBtn.addEventListener('click', () => {
      if (prepareBtn.dataset.submitted) return;
      prepareBtn.dataset.submitted = 'true';
      prepareBtn.disabled = true;
      prepareBtn.innerHTML = '<span class="spinner"></span> Calling AI model… please wait';
      startProgress();
      const form = document.getElementById('generate-form');
      if (form) form.submit();
    });
  }

  /* ── Analyse button loading state ── */
  const analyseBtn = document.getElementById('analyse-btn');
  if (analyseBtn) {
    analyseBtn.closest('form')?.addEventListener('submit', () => {
      analyseBtn.disabled = true;
      analyseBtn.innerHTML = '<span class="spinner"></span> Analysing…';
      startProgress();
    });
  }

  /* ── Export buttons — show toast on click ── */
  const pdfBtn = document.getElementById('btn-pdf');
  const txtBtn = document.getElementById('btn-txt');

  if (pdfBtn) pdfBtn.addEventListener('click', () => showToast('📄 Generating PDF…', 2500));
  if (txtBtn) txtBtn.addEventListener('click', () => showToast('📝 Preparing text file…', 2000));

  /* ── Animate bars on screen 2 ── */
  function animateBars() {
    const fills = document.querySelectorAll('.bar-fill');
    fills.forEach(el => {
      const pct = el.dataset.pct || el.dataset.width;
      const target = pct ? (pct + '%') : el.style.width;
      el.style.width = '0';
      setTimeout(() => { el.style.width = target; }, 80);
    });
  }
  animateBars();

  /* ── Validation result scroll ── */
  const validationOk = document.getElementById('validation-ok');
  if (validationOk) {
    setTimeout(() => validationOk.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 200);
    showToast('✓ CSV validated — ready to analyse!');
  }

});


/* ============================================================
   WILDGUARD ASSISTANT — Draggable Floating Chatbot
   ============================================================ */
(function () {
  'use strict';

  const fab        = document.getElementById('chat-fab');
  const win        = document.getElementById('chat-window');
  const dragHandle = document.getElementById('chat-drag-handle');
  const messagesEl = document.getElementById('chat-messages');
  const inputEl    = document.getElementById('chat-input');
  const sendBtn    = document.getElementById('chat-send-btn');
  const closeBtn   = document.getElementById('chat-close-btn');
  const clearBtn   = document.getElementById('chat-clear-btn');
  const fabOpenIcon  = fab ? fab.querySelector('.chat-fab-icon--open')  : null;
  const fabCloseIcon = fab ? fab.querySelector('.chat-fab-icon--close') : null;

  if (!fab || !win) return;   // chatbot markup not present

  // ── State ──────────────────────────────────────────────────
  let isOpen    = false;
  let chatHistory = [];       // [{role, content}] — sent to /chat
  const QUICK_PROMPTS = [
    'How do I upload my CSV?',
    'What does Zone distribution mean?',
    'How is AI used in this tool?',
    'What is SDG 15?',
    'Why does time-of-day matter?',
  ];

  // ── Open / Close ───────────────────────────────────────────
  // Show model name in header if available
  const statusLine = document.getElementById('chat-status-line');
  if (statusLine && window.WG_CONFIG && window.WG_CONFIG.model) {
    // Shorten the model name: show last segment after last '/'
    const modelFull = window.WG_CONFIG.model;
    const shortName = modelFull.split('/').pop().replace(/:.*$/, '');
    statusLine.textContent = `Model: ${shortName}`;
  }

  function openChat() {
    isOpen = true;
    win.classList.add('chat-open');
    win.setAttribute('aria-hidden', 'false');
    fab.setAttribute('aria-expanded', 'true');
    fabOpenIcon.style.display  = 'none';
    fabCloseIcon.style.display = '';
    if (messagesEl.childElementCount === 0) showWelcome();
    setTimeout(() => inputEl && inputEl.focus(), 250);
  }

  function closeChat() {
    isOpen = false;
    win.classList.remove('chat-open');
    win.setAttribute('aria-hidden', 'true');
    fab.setAttribute('aria-expanded', 'false');
    fabOpenIcon.style.display  = '';
    fabCloseIcon.style.display = 'none';
  }

  fab.addEventListener('click', () => isOpen ? closeChat() : openChat());
  if (closeBtn) closeBtn.addEventListener('click', closeChat);

  // Clear conversation
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      chatHistory = [];
      messagesEl.innerHTML = '';
      showWelcome();
    });
  }

  // ── Welcome message + quick prompts ───────────────────────
  function showWelcome() {
    appendMessage('assistant',
      'Hello! I\'m the WildGuard Assistant. Ask me anything about this tool, your HWC analysis, or wildlife conservation reporting.');

    // Quick-prompt chips
    const row = document.createElement('div');
    row.className = 'chat-quick-prompts';
    QUICK_PROMPTS.forEach(q => {
      const btn = document.createElement('button');
      btn.className = 'chat-quick-btn';
      btn.textContent = q;
      btn.addEventListener('click', () => {
        row.remove();
        sendMessage(q);
      });
      row.appendChild(btn);
    });
    messagesEl.appendChild(row);
    scrollBottom();
  }

  // ── Append a message bubble ────────────────────────────────
  function appendMessage(role, text) {
    const wrapper = document.createElement('div');
    wrapper.className = `chat-msg chat-msg--${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'chat-msg-bubble';
    // Simple markdown: **bold**, *italic*, newlines → <br>
    bubble.innerHTML = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');

    wrapper.appendChild(bubble);
    messagesEl.appendChild(wrapper);
    scrollBottom();
    return wrapper;
  }

  // ── Typing indicator ───────────────────────────────────────
  function showTyping() {
    const el = document.createElement('div');
    el.className = 'chat-typing';
    el.id = 'chat-typing-indicator';
    el.innerHTML = `<div class="chat-typing-dots">
      <div class="chat-typing-dot"></div>
      <div class="chat-typing-dot"></div>
      <div class="chat-typing-dot"></div>
    </div>`;
    messagesEl.appendChild(el);
    scrollBottom();
  }

  function hideTyping() {
    const el = document.getElementById('chat-typing-indicator');
    if (el) el.remove();
  }

  function scrollBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  // ── Send message ───────────────────────────────────────────
  async function sendMessage(text) {
    const msg = (text || '').trim();
    if (!msg) return;

    appendMessage('user', msg);
    chatHistory.push({ role: 'user', content: msg });
    inputEl.value = '';
    inputEl.style.height = 'auto';
    sendBtn.disabled = true;
    showTyping();

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, history: chatHistory.slice(0, -1) }),
      });

      hideTyping();

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const reply = data.reply || 'Sorry, I received an empty response.';
      appendMessage('assistant', reply);
      chatHistory.push({ role: 'assistant', content: reply });

      // keep history bounded (last 20 turns)
      if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);

    } catch (err) {
      hideTyping();
      appendMessage('assistant', 'Sorry, something went wrong connecting to the assistant. Please try again.');
      chatHistory.pop(); // remove the failed user turn
    }
  }

  // ── Input handlers ─────────────────────────────────────────
  if (inputEl) {
    inputEl.addEventListener('input', () => {
      sendBtn.disabled = inputEl.value.trim().length === 0;
      // Auto-grow
      inputEl.style.height = 'auto';
      inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
    });

    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled) sendMessage(inputEl.value);
      }
    });
  }

  if (sendBtn) {
    sendBtn.addEventListener('click', () => sendMessage(inputEl.value));
  }

  // ── Draggable ──────────────────────────────────────────────
  (function makeDraggable() {
    let dragging = false;
    let startX, startY, startLeft, startTop;

    function getWinPos() {
      const rect = win.getBoundingClientRect();
      return { left: rect.left, top: rect.top };
    }

    function clamp(val, min, max) {
      return Math.max(min, Math.min(max, val));
    }

    dragHandle.addEventListener('mousedown', startDrag);
    dragHandle.addEventListener('touchstart', startDrag, { passive: true });

    function startDrag(e) {
      if (e.target.closest('.chat-icon-btn')) return;  // don't drag on icon buttons
      dragging = true;
      win.classList.add('chat-dragging');
      const touch = e.touches ? e.touches[0] : e;
      startX = touch.clientX;
      startY = touch.clientY;
      const pos = getWinPos();
      startLeft = pos.left;
      startTop  = pos.top;
      // Switch from bottom/right to top/left positioning
      win.style.bottom = 'auto';
      win.style.right  = 'auto';
      win.style.left   = startLeft + 'px';
      win.style.top    = startTop  + 'px';
      e.preventDefault && e.preventDefault();
    }

    function onMove(e) {
      if (!dragging) return;
      const touch = e.touches ? e.touches[0] : e;
      const dx = touch.clientX - startX;
      const dy = touch.clientY - startY;
      const maxLeft = window.innerWidth  - win.offsetWidth;
      const maxTop  = window.innerHeight - win.offsetHeight;
      win.style.left = clamp(startLeft + dx, 0, maxLeft) + 'px';
      win.style.top  = clamp(startTop  + dy, 0, maxTop)  + 'px';
    }

    function endDrag() {
      dragging = false;
      win.classList.remove('chat-dragging');
    }

    document.addEventListener('mousemove', onMove);
    document.addEventListener('touchmove', onMove, { passive: true });
    document.addEventListener('mouseup', endDrag);
    document.addEventListener('touchend', endDrag);
  })();

})();
