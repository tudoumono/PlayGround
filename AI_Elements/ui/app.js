/**
 * 最小UIロジック（暫定）
 * - タブ切替、ローカル会話/メッセージ、設定(localStorage)の保存、
 *   ペルソナJSONの入出力、Vectorストアのモック表示、簡易ログ出力。
 * - 将来: API配線（OpenAI/SQLite/Vector）に差し替え。
 *
 * NOTE: SSE/ツール呼び出しはUI上で擬似的に再現（setInterval）。
 */
(function () {
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  // --- Tabs
  const tabs = $('#tabs');
  tabs.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-tab]');
    if (!btn) return;
    $$('#tabs button').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    const tab = btn.dataset.tab;
    $$('.tab').forEach((s) => s.classList.remove('active'));
    $(`#tab-${tab}`).classList.add('active');
  });

  // --- Settings (localStorageのみ)
  const settingsKeys = {
    apiKey: 'cfg_api_key',
    webSearch: 'cfg_web_search',
    vector: 'cfg_vector',
    egress: 'cfg_egress',
    http: 'cfg_http',
    https: 'cfg_https',
    noProxy: 'cfg_noproxy',
  };
  function loadSettings() {
    $('#cfg-api-key').value = localStorage.getItem(settingsKeys.apiKey) || '';
    $('#cfg-web-search').checked = localStorage.getItem(settingsKeys.webSearch) !== 'false';
    $('#cfg-vector').checked = localStorage.getItem(settingsKeys.vector) !== 'false';
    $('#cfg-egress').checked = localStorage.getItem(settingsKeys.egress) === 'true';
    $('#cfg-http').value = localStorage.getItem(settingsKeys.http) || '';
    $('#cfg-https').value = localStorage.getItem(settingsKeys.https) || '';
    $('#cfg-noproxy').value = localStorage.getItem(settingsKeys.noProxy) || '';
  }
  function saveSettings() {
    localStorage.setItem(settingsKeys.apiKey, $('#cfg-api-key').value.trim());
    localStorage.setItem(settingsKeys.webSearch, String($('#cfg-web-search').checked));
    localStorage.setItem(settingsKeys.vector, String($('#cfg-vector').checked));
    localStorage.setItem(settingsKeys.egress, String($('#cfg-egress').checked));
    localStorage.setItem(settingsKeys.http, $('#cfg-http').value.trim());
    localStorage.setItem(settingsKeys.https, $('#cfg-https').value.trim());
    localStorage.setItem(settingsKeys.noProxy, $('#cfg-noproxy').value.trim());
    log('settings', 'Saved settings to localStorage');
  }
  $('#save-settings').addEventListener('click', saveSettings);
  $('#test-key').addEventListener('click', () => {
    // 疎通は未配線のため簡易チェック
    const key = $('#cfg-api-key').value.trim();
    const msg = key.startsWith('sk-') ? 'Looks like a key (not validated)' : 'Invalid format';
    $('#health').textContent = msg;
  });
  loadSettings();

  // --- Conversations (メモリのみ)
  const conversations = [];
  let activeConvId = null;
  function newConversation() {
    const id = crypto.randomUUID();
    conversations.unshift({ id, title: 'New chat', messages: [] });
    activeConvId = id;
    renderConversations();
    renderMessages();
  }
  function renderConversations() {
    const ul = $('#conversations');
    ul.innerHTML = '';
    for (const c of conversations) {
      const li = document.createElement('li');
      li.textContent = c.title;
      li.className = c.id === activeConvId ? 'muted' : '';
      li.style.cursor = 'pointer';
      li.onclick = () => {
        activeConvId = c.id;
        renderConversations();
        renderMessages();
      };
      ul.appendChild(li);
    }
  }
  function renderMessages() {
    const conv = conversations.find((c) => c.id === activeConvId);
    const list = $('#message-list');
    list.innerHTML = '';
    if (!conv) return;
    for (const m of conv.messages) {
      const div = document.createElement('div');
      div.className = `message ${m.role}`;
      div.textContent = m.content;
      list.appendChild(div);
    }
    list.scrollTop = list.scrollHeight;
  }
  $('#new-conv').addEventListener('click', newConversation);
  newConversation();

  // --- Chat send (擬似ストリーミング)
  $('#send').addEventListener('click', () => {
    const text = $('#input').value.trim();
    if (!text || !activeConvId) return;
    $('#input').value = '';
    const conv = conversations.find((c) => c.id === activeConvId);
    conv.messages.push({ role: 'user', content: text });
    renderMessages();
    // 擬似: assistantのデルタを1文字ずつ出す
    const reply = `Echo: ${text}`;
    const m = { role: 'assistant', content: '' };
    conv.messages.push(m);
    renderMessages();
    let i = 0;
    const timer = setInterval(() => {
      m.content += reply[i++] || '';
      renderMessages();
      if (i >= reply.length) {
        clearInterval(timer);
        log('stream', 'response.done');
      }
    }, 20);
  });

  // --- Tools/Vector (モック)
  const stores = [
    { id: 'L1-default', layer: 'L1', name: 'Default KB', files: 12, size: '3.2MB' },
  ];
  function renderStores() {
    const t = $('#stores');
    t.innerHTML = '<tr><th>ID</th><th>Layer</th><th>Name</th><th>Files</th><th>Size</th><th></th></tr>';
    for (const s of stores) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${s.id}</td><td>${s.layer}</td><td>${s.name}</td><td>${s.files}</td><td>${s.size}</td><td><button data-id="${s.id}">Delete</button></td>`;
      tr.querySelector('button').onclick = () => {
        const idx = stores.findIndex((x) => x.id === s.id);
        if (idx >= 0) stores.splice(idx, 1);
        renderStores();
      };
      t.appendChild(tr);
    }
  }
  $('#create-store').addEventListener('click', () => {
    const layer = $('#new-store-layer').value;
    const name = $('#new-store-name').value.trim() || 'New Store';
    const id = `${layer}-${Math.random().toString(36).slice(2, 8)}`;
    stores.unshift({ id, layer, name, files: 0, size: '0B' });
    renderStores();
  });
  renderStores();

  // --- Personas 入出力（ローカルのみ）
  let personas = [
    { id: 'general', name: 'General', systemPrompt: 'あなたは有能なアシスタントです。', allowedTools: ['web_search', 'file_search'] },
  ];
  function renderPersonas() {
    const ul = $('#persona-list');
    ul.innerHTML = '';
    for (const p of personas) {
      const li = document.createElement('li');
      li.innerHTML = `<strong>${p.name}</strong><br><span class="muted">tools: ${p.allowedTools.join(', ')}</span>`;
      ul.appendChild(li);
    }
  }
  renderPersonas();
  $('#export-personas').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(personas, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'personas.json';
    a.click();
    URL.revokeObjectURL(a.href);
  });
  $('#import-personas').addEventListener('change', (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    file.text().then((txt) => {
      try {
        const arr = JSON.parse(txt);
        if (Array.isArray(arr)) {
          personas = arr;
          renderPersonas();
          log('personas', `Imported ${arr.length} personas`);
        }
      } catch (err) {
        log('error', 'Failed to parse personas.json');
      }
    });
  });

  // --- Logs
  function log(tag, msg) {
    const el = $('#logs');
    const line = `[${new Date().toISOString()}] [${tag}] ${msg}`;
    el.textContent += (el.textContent ? '\n' : '') + line;
    el.scrollTop = el.scrollHeight;
  }
})();

