import { useEffect, useState } from 'react';

const API = 'http://127.0.0.1:8000/api';
export default function App() {
  const [summary, setSummary] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [error, setError] = useState('');
  const [text, setText] = useState('Flood water rising fast near Rampur; 12 people trapped, urgent boat and rescue support needed.');
  const [location, setLocation] = useState('Rampur');
  const [replaying, setReplaying] = useState(false);

  async function refresh() {
    try {
      const [s, i] = await Promise.all([fetch(`${API}/summary`), fetch(`${API}/incidents`)]);
      if (!s.ok || !i.ok) throw new Error('API request failed');
      setSummary(await s.json()); setIncidents(await i.json()); setError('');
    } catch { setError('Backend unavailable. Start FastAPI on http://127.0.0.1:8000'); }
  }
  useEffect(() => { refresh(); }, []);

  async function replay(e) {
    e.preventDefault(); setReplaying(true);
    try {
      const res = await fetch(`${API}/scenario/replay`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text, location_name:location, source:'dashboard_scenario'})});
      if (!res.ok) throw new Error('Replay failed');
      const snapshot = await res.json();
      setIncidents(snapshot.incidents || []);
      setSummary(prev => ({...(prev || {}), report_count: snapshot.report_count, incident_count: (snapshot.incidents || []).length, critical_count: (snapshot.incidents || []).filter(i => i.priority === 'CRITICAL').length, high_count: (snapshot.incidents || []).filter(i => i.priority === 'HIGH').length, duplicate_count: (snapshot.incidents || []).filter(i => Boolean(i.duplicate_of)).length, conflict_count: (snapshot.incidents || []).filter(i => Boolean(i.conflict_flag)).length}));
      setError('');
    } catch { setError('Scenario replay failed. Check the backend and try again.'); }
    finally { setReplaying(false); }
  }

  return <main className="shell">
    <header className="topbar">
      <div className="brandmark">S</div>
      <div><div className="eyebrow">DISASTER INTELLIGENCE PLATFORM</div><h1>SURAKSHA <span>AI</span></h1></div>
      <div className="live"><i/> SYNTHETIC DEMO</div>
    </header>
    <section className="hero">
      <div><div className="eyebrow">COMMAND OVERVIEW / AI-001</div><h2>From fragmented reports<br/>to actionable response.</h2><p>Evidence-aware incident triage and constrained resource recommendations.</p></div>
      <button className="ghost" onClick={refresh}>↻ Refresh data</button>
    </section>
    {error && <div className="error">{error}</div>}
    <section className="metrics">
      {[
        ['Reports processed', summary?.report_count ?? '—', 'All synthetic sources'],
        ['Critical incidents', summary?.critical_count ?? '—', 'Highest current priority'],
        ['Duplicates flagged', summary?.duplicate_count ?? '—', 'Requires report review'],
        ['Conflicts detected', summary?.conflict_count ?? '—', 'Evidence is inconsistent'],
      ].map(([label,value,note]) => <article className="metric" key={label}><div>{label}</div><strong>{value}</strong><small>{note}</small></article>)}
    </section>
    <section className="layout">
      <article className="panel incidents">
        <div className="panel-head"><div><div className="eyebrow">PRIORITY QUEUE</div><h3>Incident intelligence</h3></div><span className="count">{incidents.length} records</span></div>
        <div className="table-wrap"><table><thead><tr><th>Incident / Location</th><th>Risk</th><th>Evidence</th><th>Recommended resources</th></tr></thead>
          <tbody>{incidents.slice(0,30).map(i=><tr key={i.incident_id}>
            <td><b>{i.incident_id}</b><div className="muted">{i.location_name} · {i.incident_type.replaceAll('_',' ')}</div><div className="report">{i.text}</div></td>
            <td><span className={`priority ${i.priority.toLowerCase()}`}>{i.priority}</span><div className="risk">{i.risk_score}/100</div></td>
            <td><span className={`evidence ${i.confidence < .6 || i.conflict_flag ? 'warn':''}`}>{i.conflict_flag ? 'Conflict' : i.duplicate_of ? 'Duplicate' : i.confidence < .6 ? 'Unverified' : 'Review'}</span><div className="muted">Confidence {(i.confidence*100).toFixed(0)}%</div></td>
            <td>{i.assigned_resources?.length ? i.assigned_resources.map((r,n)=><span className="resource" key={r+n}>{r.replaceAll('_',' ')}</span>) : <span className="muted">No stock assigned</span>}<details><summary>Why this score?</summary><ul>{i.explanation?.map((x,n)=><li key={n}>{x}</li>)}</ul></details></td>
          </tr>)}</tbody></table></div>
      </article>
      <aside className="panel replay">
        <div className="eyebrow">WHAT-IF SIMULATION</div><h3>Scenario replay</h3><p className="muted">Inject a new synthetic report and recompute the recommendation snapshot.</p>
        <form onSubmit={replay}>
          <label>Location<input value={location} onChange={e=>setLocation(e.target.value)} /></label>
          <label>Incoming report<textarea rows="6" value={text} onChange={e=>setText(e.target.value)} /></label>
          <button className="primary" disabled={replaying}>{replaying ? 'Replaying…' : 'Inject report & recompute'}</button>
        </form>
        <div className="notice"><b>Decision-support only</b><br/>Reports and locations are synthetic. Recommendations must be reviewed by a human operator; this prototype is not validated for real emergencies.</div>
      </aside>
    </section>
    <footer> SURAKSHA AI · Prototype v0.1 · Rule-based baseline · Human oversight required</footer>
  </main>;
}
