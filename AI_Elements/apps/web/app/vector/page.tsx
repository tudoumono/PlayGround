"use client";
import { useState } from 'react';

type Store = { id: string; layer: 'L1'|'L2'|'L3'; name: string; files: number; size: string };

export default function VectorPage(){
  const [stores, setStores] = useState<Store[]>([
    { id: 'L1-default', layer: 'L1', name: 'Default KB', files: 12, size: '3.2MB' },
  ]);
  const [layer, setLayer] = useState<'L2'|'L3'>('L2');
  const [name, setName] = useState('');

  function create(){
    const id = `${layer}-${Math.random().toString(36).slice(2,8)}`;
    setStores([{ id, layer, name: name || 'New Store', files: 0, size: '0B' }, ...stores]);
    setName('');
  }
  function remove(id: string){ setStores(stores.filter(s=>s.id!==id)); }

  return (
    <section className="panel">
      <div className="row" style={{justifyContent:'space-between'}}>
        <h2>Vector Stores</h2>
        <div className="row">
          <select value={layer} onChange={(e)=>setLayer(e.target.value as any)}>
            <option value="L2">L2</option>
            <option value="L3">L3</option>
          </select>
          <input value={name} onChange={(e)=>setName(e.target.value)} placeholder="Store name"/>
          <button onClick={create}>Create</button>
        </div>
      </div>
      <table className="table" style={{width:'100%', borderCollapse:'collapse'}}>
        <thead><tr><th>ID</th><th>Layer</th><th>Name</th><th>Files</th><th>Size</th><th></th></tr></thead>
        <tbody>
        {stores.map(s=> (
          <tr key={s.id}>
            <td>{s.id}</td><td>{s.layer}</td><td>{s.name}</td><td>{s.files}</td><td>{s.size}</td>
            <td><button onClick={()=>remove(s.id)}>Delete</button></td>
          </tr>
        ))}
        </tbody>
      </table>
    </section>
  );
}

