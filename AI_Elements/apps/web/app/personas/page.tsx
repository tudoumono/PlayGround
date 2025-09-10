"use client";
import { useState } from 'react';

type Persona = { id: string; name: string; systemPrompt: string; allowedTools: string[] };

export default function PersonasPage(){
  const [personas, setPersonas] = useState<Persona[]>([
    { id:'general', name:'General', systemPrompt:'あなたは有能なアシスタントです。', allowedTools:['web_search','file_search'] }
  ]);

  function exportJson(){
    const blob = new Blob([JSON.stringify(personas,null,2)],{type:'application/json'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = 'personas.json'; a.click(); URL.revokeObjectURL(a.href);
  }
  function importJson(e: React.ChangeEvent<HTMLInputElement>){
    const f = e.target.files?.[0]; if(!f) return; f.text().then(t=>{
      try { const arr = JSON.parse(t); if(Array.isArray(arr)) setPersonas(arr); } catch {}
    });
  }

  return (
    <section className="panel">
      <div className="row" style={{justifyContent:'space-between'}}>
        <h2>ペルソナ</h2>
        <div className="row">
          <button onClick={exportJson}>JSONエクスポート</button>
          <label><input type="file" accept="application/json" onChange={importJson}/> インポート</label>
      </div>
      </div>
      <ul style={{listStyle:'none', padding:0}}>
        {personas.map(p => (
          <li key={p.id} className="message" style={{background:'#0b111a'}}>
            <strong>{p.name}</strong><div className="muted">tools: {p.allowedTools.join(', ')}</div>
          </li>
        ))}
      </ul>
    </section>
  );
}
