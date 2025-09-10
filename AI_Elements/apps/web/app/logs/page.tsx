"use client";
import { useEffect, useState } from 'react';

export default function LogsPage(){
  const [logs, setLogs] = useState<string[]>([]);
  useEffect(()=>{
    const id = setInterval(()=> setLogs(l=>[...l.slice(-200), `[${new Date().toISOString()}] heartbeat`]), 5000);
    return ()=>clearInterval(id);
  },[]);
  return (
    <section className="panel">
      <h2>Tool/Stream Logs</h2>
      <pre style={{background:'#0b111a', border:'1px solid #223048', borderRadius:8, padding:10, minHeight:300, maxHeight:'60vh', overflow:'auto'}}>
        {logs.join('\n')}
      </pre>
    </section>
  );
}

