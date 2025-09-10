/**
 * Settingsタブ（暫定）
 */
"use client";
import { useEffect, useState } from 'react';

export default function SettingsPage() {
  const [saving, setSaving] = useState(false);
  const [cfg, setCfg] = useState({
    apiKey: '', web: true, vector: true, egress: false, http: '', https: '', noProxy: ''
  });

  useEffect(() => {
    // NOTE: 現状はlocalStorageのみ
    const ls = (k: string, d = '') => (typeof localStorage !== 'undefined' ? localStorage.getItem(k) ?? d : d);
    setCfg({
      apiKey: ls('cfg_api_key'),
      web: ls('cfg_web_search', 'true') !== 'false',
      vector: ls('cfg_vector', 'true') !== 'false',
      egress: ls('cfg_egress', 'false') === 'true',
      http: ls('cfg_http'), https: ls('cfg_https'), noProxy: ls('cfg_noproxy'),
    });
  }, []);

  async function save() {
    setSaving(true);
    // NOTE: 今はlocalStorage。将来 /api/settings へPOST
    Object.entries({
      cfg_api_key: cfg.apiKey,
      cfg_web_search: String(cfg.web),
      cfg_vector: String(cfg.vector),
      cfg_egress: String(cfg.egress),
      cfg_http: cfg.http,
      cfg_https: cfg.https,
      cfg_noproxy: cfg.noProxy,
    }).forEach(([k, v]) => localStorage.setItem(k, v as string));
    setSaving(false);
  }

  return (
    <section className="panel">
      <h2>API / Proxy / Policy</h2>
      <div className="grid">
        <label>OpenAI API Key <input value={cfg.apiKey} onChange={(e)=>setCfg({...cfg, apiKey: e.target.value})} placeholder="sk-..."/></label>
        <label><input type="checkbox" checked={cfg.web} onChange={(e)=>setCfg({...cfg, web: e.target.checked})}/> web_search enabled</label>
        <label><input type="checkbox" checked={cfg.vector} onChange={(e)=>setCfg({...cfg, vector: e.target.checked})}/> vector enabled</label>
        <label><input type="checkbox" checked={cfg.egress} onChange={(e)=>setCfg({...cfg, egress: e.target.checked})}/> EGRESS_STRICT</label>
        <label>HTTP_PROXY <input value={cfg.http} onChange={(e)=>setCfg({...cfg, http: e.target.value})} placeholder="http://..." /></label>
        <label>HTTPS_PROXY <input value={cfg.https} onChange={(e)=>setCfg({...cfg, https: e.target.value})} placeholder="http://..." /></label>
        <label>NO_PROXY <input value={cfg.noProxy} onChange={(e)=>setCfg({...cfg, noProxy: e.target.value})} placeholder="localhost,127.0.0.1" /></label>
      </div>
      <div className="row">
        <button onClick={save} disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
      </div>
    </section>
  );
}

