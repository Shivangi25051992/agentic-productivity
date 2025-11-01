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
})();


