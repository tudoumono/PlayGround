"use client";
import { useCallback, useEffect, useState } from 'react';

type LogEntry = { ts: string; level: 'info'|'warn'|'error'|'debug'; tag: string; message: string };

export default function LogsPage(){
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    const res = await fetch('/api/logs?limit=200', { cache: 'no-store' });
    const json = await res.json();
    setLogs(json.logs as LogEntry[]);
    setLoading(false);
  }, []);

  const clear = useCallback(async () => {
    await fetch('/api/logs', { method: 'DELETE' });
    setLogs([]);
  }, []);

  useEffect(() => {
    void load();
    const id = setInterval(load, 3000);
    return () => clearInterval(id);
  }, [load]);

  return (
    <section className="panel">
      <div className="row" style={{justifyContent:'space-between'}}>
        <h2>ログ（ツール/ストリーム）</h2>
        <div className="row">
          <button onClick={load} disabled={loading}>{loading ? '更新中…' : '更新'}</button>
          <button onClick={clear}>クリア</button>
        </div>
      </div>
      <pre style={{background:'#0b111a', border:'1px solid #223048', borderRadius:8, padding:10, minHeight:300, maxHeight:'60vh', overflow:'auto'}}>
        {logs.map(l => `[${l.ts}] [${l.level}] [${l.tag}] ${l.message}`).join('\n')}
      </pre>
    </section>
  );
}
