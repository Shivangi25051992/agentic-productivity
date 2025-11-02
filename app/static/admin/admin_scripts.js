/* Admin UI Scripts
   - Theme management, authentication, fetch wrapper, toasts, ripple, forms
   - A11y: focus management, keyboard shortcuts, ARIA live regions
*/
(function(){
  const $ = (sel, root=document) => root.querySelector(sel);
  const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));

  /* Theme */
  function getSystemPrefersDark(){ return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches; }
  function applyTheme(theme){ document.documentElement.setAttribute('data-theme', theme); localStorage.setItem('theme', theme); }
  function initTheme(){ const stored = localStorage.getItem('theme'); applyTheme(stored || (getSystemPrefersDark() ? 'dark' : 'light')); }

  /* Auth */
  const auth = {
    get token(){ return sessionStorage.getItem('admin_token') || ''; },
    set token(t){ if(t) sessionStorage.setItem('admin_token', t); else sessionStorage.removeItem('admin_token'); },
    isExpired(payload){ if(!payload || !payload.exp) return true; return (Date.now()/1000) > payload.exp; },
    decode(token){ try{ return JSON.parse(atob(token.split('.')[1])); }catch{ return null; } },
    logout(){ this.token = ''; location.href = './admin_login.html'; }
  };

  /* Fetch wrapper */
  async function api(path, opts={}){
    const headers = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
    if(auth.token) headers['Authorization'] = `Bearer ${auth.token}`;
    const res = await fetch(path, Object.assign({}, opts, { headers }));
    if(res.status === 401){
      try{ await fetch('/admin/logout', { method:'POST', headers:{ 'Authorization': `Bearer ${auth.token}` }}); }catch{}
      auth.logout();
      throw new Error('Unauthorized');
    }
    if(!res.ok){ const text = await res.text(); throw new Error(text || `HTTP ${res.status}`); }
    const ct = res.headers.get('content-type') || '';
    return ct.includes('application/json') ? res.json() : res.text();
  }

  /* Ripple */
  function createRipple(e){
    const btn = e.currentTarget;
    const rect = btn.getBoundingClientRect();
    const circle = document.createElement('span');
    const size = Math.max(rect.width, rect.height);
    circle.style.width = circle.style.height = `${size}px`;
    circle.style.position = 'absolute'; circle.style.borderRadius = '50%';
    circle.style.left = `${e.clientX - rect.left - size/2}px`;
    circle.style.top = `${e.clientY - rect.top - size/2}px`;
    circle.style.background = 'rgba(255,255,255,.4)';
    circle.style.pointerEvents = 'none';
    circle.style.transform = 'scale(0)';
    circle.style.animation = 'ripple .6s ease forwards';
    btn.style.position = 'relative'; btn.style.overflow = 'hidden';
    btn.appendChild(circle);
    setTimeout(()=> circle.remove(), 650);
  }

  /* Toasts */
  function showToast(message, type='success'){
    const root = $('#toasts') || (()=>{ const t=document.createElement('div'); t.id='toasts'; t.className='toasts'; document.body.appendChild(t); return t; })();
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = message;
    root.appendChild(el);
    setTimeout(()=> el.remove(), 5000);
  }

  /* Validation */
  function validateInput(input){ if(input.hasAttribute('required') && !input.value.trim()) return 'Required'; return ''; }
  function scrollToError(el){ el.scrollIntoView({ behavior: 'smooth', block: 'center' }); el.focus({ preventScroll: true }); }

  /* Forms */
  function attachFormHandlers(){
    const form = $('#loginForm'); if(!form) return;
    const btn = $('#submitBtn'); const err = $('#error');
    const user = $('#username'); const pass = $('#password');
    const toggle = $('#togglePassword');
    toggle?.addEventListener('click', ()=>{ pass.type = pass.type === 'password' ? 'text' : 'password'; });

    const submit = async (e)=>{
      e?.preventDefault();
      err.classList.remove('show'); err.textContent = '';
      const uerr = validateInput(user); const perr = validateInput(pass);
      if(uerr){ user.classList.add('error'); scrollToError(user); return; } else user.classList.remove('error');
      if(perr){ pass.classList.add('error'); scrollToError(pass); return; } else pass.classList.remove('error');
      btn.setAttribute('aria-busy','true'); btn.querySelector('.spinner')?.removeAttribute('hidden');
      try{
        const res = await api('/admin/login', { method:'POST', body: JSON.stringify({ username: user.value, password: pass.value }) });
        auth.token = res.token; showToast('Logged in'); location.href = './admin_dashboard.html';
      }catch(ex){ err.textContent = 'Invalid credentials'; err.classList.add('show'); }
      finally{ btn.setAttribute('aria-busy','false'); btn.querySelector('.spinner')?.setAttribute('hidden',''); }
    };
    form.addEventListener('submit', submit);
    form.addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ submit(e); }});
  }

  function attachDashboardHandlers(){
    const themeToggle = $('#themeToggle');
    themeToggle?.addEventListener('click', ()=>{
      const current = document.documentElement.getAttribute('data-theme');
      applyTheme(current==='dark'?'light':'dark');
    });
    $$('.btn-primary').forEach(b=> b.addEventListener('click', createRipple));

    const save = $('#saveConfig');
    save?.addEventListener('click', async ()=>{
      try{
        const fbCfg = parseFirebaseConfig($('#fbConfig')?.value || '');
        if (fbCfg && (!fbCfg.apiKey || !fbCfg.projectId)) {
          showToast('Invalid Firebase Config: missing apiKey or projectId','error');
          return;
        }
        const payload = {
          openai_api_key: $('#openaiKey')?.value || undefined,
          gemini_api_key: $('#geminiKey')?.value || undefined,
          google_project_id: $('#gProject')?.value || undefined,
          google_application_credentials_json: $('#gCreds')?.value || undefined,
          firebase_config: fbCfg || {},
          llm_prompt_template: $('#llmTemplate')?.value || undefined,
          smtp_config: {
            host: $('#smtpHost')?.value || '',
            port: Number($('#smtpPort')?.value || 587),
            username: $('#smtpUser')?.value || '',
            password: $('#smtpPass')?.value || '',
          },
          app_settings: {
            default_calorie_goal: Number($('#defaultCalGoal')?.value || 2000),
            reminder_times: ($('#reminderTimes')?.value || '').split(',').map(s=>s.trim()).filter(Boolean),
          },
          is_active: true,
        };
        const res = await api('/admin/config', { method:'POST', body: JSON.stringify(payload) });
        // Best effort auto-activate and refresh
        let id = res?.config?.config_id;
        if(!id){
          try{
            const hist = await api('/admin/config/history');
            id = hist?.items?.[0]?.config_id;
          }catch(_){ /* ignore */ }
        }
        if(id){
          try{ await api(`/admin/config/${id}/activate`, { method:'PUT' }); }catch(_){ /* ignore */ }
        }
        await loadActiveConfig();
        showToast('Configuration saved','success');
      }catch(ex){ showToast('Failed to save configuration','error'); }
    });

    const testAll = $('#testAll');
    testAll?.addEventListener('click', async ()=>{
      try{
        const fbCfg = parseFirebaseConfig($('#fbConfig')?.value || '');
        const payload = {
          openai_api_key: $('#openaiKey')?.value || undefined,
          gemini_api_key: $('#geminiKey')?.value || undefined,
          google_project_id: $('#gProject')?.value || undefined,
          google_application_credentials_json: $('#gCreds')?.value || undefined,
          firebase_config: fbCfg || {},
          llm_prompt_template: $('#llmTemplate')?.value || undefined,
          smtp_config: {
            host: $('#smtpHost')?.value || '',
            port: Number($('#smtpPort')?.value || 587),
            username: $('#smtpUser')?.value || '',
            password: $('#smtpPass')?.value || '',
          },
        };
        const res = await api('/admin/config/test', { method:'POST', body: JSON.stringify(payload) });
        showToast(res.success ? 'All tests passed' : 'Some tests failed', res.success ? 'success' : 'error');
      }catch(ex){ showToast('Validation failed','error'); }
    });
  }

  function safeJson(str){ try{ return str ? JSON.parse(str) : {}; }catch{ return {}; } }

  // Accepts either pure JSON or the Firebase snippet like: const firebaseConfig = { ... };
  function parseFirebaseConfig(raw){
    const text = (raw || '').trim();
    if(!text) return {};
    // Try strict JSON first
    try { return JSON.parse(text); } catch {}
    // Extract object block
    const s = text.indexOf('{'); const e = text.lastIndexOf('}');
    if (s >= 0 && e > s) {
      const inner = text.slice(s, e+1);
      try { return JSON.parse(inner); } catch {}
      // Try converting single quotes to double quotes
      try { return JSON.parse(inner.replace(/'/g, '"')); } catch {}
    }
    return {};
  }

  /* Keyboard shortcuts */
  function initShortcuts(){
    document.addEventListener('keydown', (e)=>{
      if((e.ctrlKey||e.metaKey) && e.key.toLowerCase()==='k'){ e.preventDefault(); $('#search')?.focus(); }
      if(e.key==='Escape'){ $('#modalRoot')?.classList.remove('show'); }
    });
  }

  /* Init */
  document.addEventListener('DOMContentLoaded', ()=>{
    initTheme(); attachFormHandlers(); attachDashboardHandlers(); initShortcuts();
    // Try to load existing active config to prefill fields
    loadActiveConfig();
    const topbar = $('#topbar');
    if(topbar){ window.addEventListener('scroll', ()=>{ topbar.classList.toggle('scrolled', window.scrollY>4); }, { passive:true }); }
  });

  async function loadActiveConfig(){
    try{
      const res = await api('/admin/config/active');
      const cfg = res && res.config ? res.config : null;
      if(!cfg) return;
      // Non-sensitive fields can be shown as-is
      const setVal = (sel, val) => { const el = $(sel); if(el) el.value = val ?? ''; };
      setVal('#gProject', cfg.google_project_id || cfg.GOOGLE_CLOUD_PROJECT || '');
      if (cfg.firebase_config) {
        try {
          setVal('#fbConfig', JSON.stringify(cfg.firebase_config, null, 2));
        } catch(_) { /* ignore */ }
      }
      if (cfg.app_settings) {
        const goal = (cfg.app_settings.default_calorie_goal ?? cfg.app_settings.defaultCalorieGoal);
        const reminders = Array.isArray(cfg.app_settings.reminder_times || cfg.app_settings.reminderTimes) ?
          (cfg.app_settings.reminder_times || cfg.app_settings.reminderTimes).join(', ') : '';
        setVal('#defaultCalGoal', goal != null ? String(goal) : '');
        setVal('#reminderTimes', reminders);
      }
      if (cfg.llm_prompt_template) {
        setVal('#llmTemplate', cfg.llm_prompt_template);
      }
      if (cfg.smtp_config) {
        setVal('#smtpHost', cfg.smtp_config.host);
        setVal('#smtpPort', cfg.smtp_config.port != null ? String(cfg.smtp_config.port) : '');
        setVal('#smtpUser', cfg.smtp_config.username || '');
        // do not prefill password even if masked
      }
      // For sensitive API keys, we avoid filling the actual values; show placeholders
      const setPlaceholder = (sel) => { const el = $(sel); if(el){ el.placeholder = '**** saved ****'; el.classList.add('saved'); } };
      setPlaceholder('#openaiKey');
      setPlaceholder('#geminiKey');
      setPlaceholder('#gCreds');
      const savedInfo = document.querySelector('#lastSavedInfo');
      if(savedInfo && cfg.updated_at){ savedInfo.textContent = `Last saved: ${cfg.updated_at}`; }
    }catch(e){ /* ignore prefill errors */ }
  }

  /* Feedback View */
  async function loadFeedbackView(){
    const content = $('#content');
    if(!content) return;
    
    content.innerHTML = `
      <section aria-labelledby="feedback-header">
        <header class="card-header" id="feedback-header">
          <div>
            <h2 style="margin:0">User Feedback</h2>
            <p class="login-subtitle" style="margin:4px 0 0">Review and manage user feedback submissions</p>
          </div>
          <div style="display:flex;gap:8px;">
            <button class="btn-primary" id="refreshFeedback" style="width:auto;padding:0 14px;height:40px">Refresh</button>
          </div>
        </header>

        <div class="cards" style="margin-bottom:20px">
          <article class="card">
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px">
              <div style="text-align:center">
                <div style="font-size:32px;font-weight:bold;color:var(--primary)" id="totalFeedback">-</div>
                <div style="font-size:14px;color:var(--text-secondary)">Total</div>
              </div>
              <div style="text-align:center">
                <div style="font-size:32px;font-weight:bold;color:#ef4444" id="bugCount">-</div>
                <div style="font-size:14px;color:var(--text-secondary)">🐛 Bugs</div>
              </div>
              <div style="text-align:center">
                <div style="font-size:32px;font-weight:bold;color:#f59e0b" id="suggestionCount">-</div>
                <div style="font-size:14px;color:var(--text-secondary)">💡 Suggestions</div>
              </div>
              <div style="text-align:center">
                <div style="font-size:32px;font-weight:bold;color:#3b82f6" id="questionCount">-</div>
                <div style="font-size:14px;color:var(--text-secondary)">❓ Questions</div>
              </div>
              <div style="text-align:center">
                <div style="font-size:32px;font-weight:bold;color:#10b981" id="praiseCount">-</div>
                <div style="font-size:14px;color:var(--text-secondary)">👍 Praise</div>
              </div>
            </div>
          </article>
        </div>

        <div style="display:flex;gap:8px;margin-bottom:16px">
          <button class="btn-primary" data-filter="all" style="width:auto;padding:0 14px;height:36px;background:var(--primary)">All</button>
          <button class="btn-primary" data-filter="bug" style="width:auto;padding:0 14px;height:36px;background:#ef4444">🐛 Bugs</button>
          <button class="btn-primary" data-filter="suggestion" style="width:auto;padding:0 14px;height:36px;background:#f59e0b">💡 Suggestions</button>
          <button class="btn-primary" data-filter="question" style="width:auto;padding:0 14px;height:36px;background:#3b82f6">❓ Questions</button>
          <button class="btn-primary" data-filter="praise" style="width:auto;padding:0 14px;height:36px;background:#10b981">👍 Praise</button>
        </div>

        <div id="feedbackList" class="card">
          <div style="text-align:center;padding:40px;color:var(--text-secondary)">
            Loading feedback...
          </div>
        </div>
      </section>
    `;

    // Load stats and feedback
    await loadFeedbackStats();
    await loadFeedbackList();

    // Attach handlers
    $('#refreshFeedback')?.addEventListener('click', async ()=>{
      await loadFeedbackStats();
      await loadFeedbackList();
    });

    $$('[data-filter]').forEach(btn=>{
      btn.addEventListener('click', async ()=>{
        const filter = btn.getAttribute('data-filter');
        await loadFeedbackList(filter === 'all' ? null : filter);
      });
    });
  }

  async function loadFeedbackStats(){
    try{
      const stats = await api('/admin/feedback/stats');
      setVal('#totalFeedback', stats.total);
      setVal('#bugCount', stats.bugs);
      setVal('#suggestionCount', stats.suggestions);
      setVal('#questionCount', stats.questions);
      setVal('#praiseCount', stats.praise);
    }catch(e){
      showToast('Failed to load stats','error');
    }
  }

  async function loadFeedbackList(filterType = null){
    try{
      const url = filterType ? `/admin/feedback/list?filter_type=${filterType}` : '/admin/feedback/list';
      const res = await api(url);
      const feedbackList = $('#feedbackList');
      
      if(!res.feedback || res.feedback.length === 0){
        feedbackList.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-secondary)">No feedback found</div>';
        return;
      }

      feedbackList.innerHTML = res.feedback.map(fb=>{
        const typeColors = {
          bug: '#ef4444',
          suggestion: '#f59e0b',
          question: '#3b82f6',
          praise: '#10b981'
        };
        const typeEmojis = {
          bug: '🐛',
          suggestion: '💡',
          question: '❓',
          praise: '👍'
        };
        const color = typeColors[fb.type] || '#666';
        const emoji = typeEmojis[fb.type] || '📝';
        const statusBadge = fb.status === 'resolved' 
          ? '<span style="background:#d1fae5;color:#10b981;padding:4px 10px;border-radius:12px;font-size:11px;font-weight:bold">RESOLVED</span>'
          : '<span style="background:#fef3c7;color:#f59e0b;padding:4px 10px;border-radius:12px;font-size:11px;font-weight:bold">NEW</span>';
        
        return `
          <div style="padding:20px;border-bottom:1px solid var(--border);border-left:4px solid ${color}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
              <div>
                <span style="background:${color}20;color:${color};padding:5px 12px;border-radius:20px;font-size:12px;font-weight:bold">${emoji} ${fb.type.toUpperCase()}</span>
                ${statusBadge}
              </div>
              <div style="font-size:12px;color:var(--text-secondary)">${new Date(fb.timestamp).toLocaleString()}</div>
            </div>
            <div style="font-size:12px;color:var(--text-secondary);margin-bottom:10px">
              <strong>User:</strong> ${fb.user_email} | <strong>Screen:</strong> ${fb.screen}
            </div>
            <div style="color:var(--text);line-height:1.6">${fb.comment}</div>
            ${fb.has_screenshot ? `<div style="margin-top:10px;color:var(--primary);font-size:12px">📷 Screenshot attached (${(fb.screenshot_size/1024).toFixed(1)} KB)</div>` : ''}
            <div style="display:flex;gap:8px;margin-top:15px">
              ${fb.status !== 'resolved' ? `<button class="btn-primary" onclick="window.resolveFeedback('${fb.id}')" style="width:auto;padding:0 14px;height:32px;background:#10b981">✓ Mark Resolved</button>` : ''}
              <button class="btn-primary" onclick="alert('Feedback ID: ${fb.id}')" style="width:auto;padding:0 14px;height:32px">View Details</button>
            </div>
          </div>
        `;
      }).join('');
    }catch(e){
      showToast('Failed to load feedback','error');
    }
  }

  window.resolveFeedback = async (feedbackId)=>{
    try{
      await api(`/admin/feedback/${feedbackId}/resolve`, { method:'POST' });
      showToast('Feedback marked as resolved','success');
      await loadFeedbackStats();
      await loadFeedbackList();
    }catch(e){
      showToast('Failed to resolve feedback','error');
    }
  };

  /* View Router */
  function attachViewRouter(){
    $$('[data-view]').forEach(link=>{
      link.addEventListener('click', (e)=>{
        e.preventDefault();
        const view = link.getAttribute('data-view');
        
        // Update active state
        $$('[data-view]').forEach(l=>l.classList.remove('active'));
        link.classList.add('active');
        
        // Load view
        if(view === 'feedback'){
          loadFeedbackView();
        }
        // Add other views here as needed
      });
    });
  }

  // Initialize on dashboard page
  if(document.getElementById('content')){
    attachDashboardHandlers();
    attachViewRouter();
  }
})();


