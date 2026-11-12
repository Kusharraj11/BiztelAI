import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState(false);
  const [result, setResult] = useState(null);
  const [asked, setAsked] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function ask(event) {
    event.preventDefault();
    if (!question.trim() || busy) return;
    setBusy(true); setError(''); setResult(null); setAsked(question);
    try {
      const response = await fetch('/api/ask', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({question, include_history: history})});
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Please check your question and try again.');
      setResult(data);
    } catch (err) { setError(err instanceof SyntaxError ? 'The backend is unavailable. Start the app and try again.' : err.message); }
    finally { setBusy(false); }
  }
  return <main>
    <header><a className="brand" href="/">B<span>BiztelAI</span></a><span className="local">LOCAL DOCUMENT COPILOT</span></header>
    <section className="intro"><span className="eyebrow">HOSUR PLANT / SUPERVISOR WORKSPACE</span><h1>Your documents.<br/><em>Clear answers.</em></h1><p>Ask about inspections, maintenance, or safety procedures.<br/>Every answer comes back to the source.</p></section>
    <form onSubmit={ask}>
      <label htmlFor="question">What would you like to know?</label>
      <div className="input-row"><input id="question" value={question} onChange={e => setQuestion(e.target.value)} maxLength={2000} placeholder="e.g. What should I do when alarm AL-104 appears?" required disabled={busy}/><button disabled={busy || !question.trim()}>{busy ? 'Finding answer…' : 'Ask question ↗'}</button></div>
      <label className="toggle"><input type="checkbox" checked={history} onChange={e => setHistory(e.target.checked)} disabled={busy}/> Include superseded revisions for historical questions</label>
      <p className="hint">{history ? 'Historical mode: ask explicitly about an older revision or compare revisions.' : 'Current revisions only · QC Rev 04 supersedes Rev 03 in the supplied documents.'}</p>
    </form>
    {!result && !busy && !error && <div className="suggestions">{['What is the coolant concentration for TX-200?', 'Who can remove a lockout lock?', 'What is the BH-220 outer diameter tolerance?'].map(q => <button key={q} onClick={() => setQuestion(q)}>{q} <span>↗</span></button>)}</div>}
    <section aria-live="polite" aria-busy={busy}>
      {busy && <p className="status">Retrieving document pages and asking the local model. The first answer may take a little longer.</p>}
      {error && <p role="alert" className="error">{error}</p>}
      {result && <article><span className="eyebrow">{result.found ? 'ANSWER FROM YOUR DOCUMENTS' : 'NOT FOUND IN DOCUMENTS'}</span><h2>{asked}</h2><p className="answer">{result.answer}</p>{result.sources.length > 0 && <><h3>Check the sources</h3><div className="sources">{result.sources.map(source => <details key={source.id}><summary>[{source.id}] {source.document} · Rev {String(source.revision).padStart(2, '0')} · Page {source.page}<span className={source.current ? 'badge' : 'badge old'}>{source.current ? 'Current' : 'Superseded'}</span></summary><a href={source.url} target="_blank" rel="noreferrer">Open original PDF ↗</a><pre>{source.text}</pre></details>)}</div></>}</article>}
    </section>
    <footer>4 source documents · Powered locally by Ollama<span>Verify the controlled version in QMS before use.</span></footer>
  </main>;
}
createRoot(document.getElementById('root')).render(<App/>);
