import { useState, useRef, useCallback } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_KEY = import.meta.env.VITE_API_KEY || 'dev-api-key-change-in-production'

const STATES = { IDLE: 'idle', UPLOADING: 'uploading', SUCCESS: 'success', ERROR: 'error' }

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function App() {
  const [status, setStatus] = useState(STATES.IDLE)
  const [file, setFile] = useState(null)
  const [email, setEmail] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [progress, setProgress] = useState(0)
  const [dragging, setDragging] = useState(false)
  const fileInputRef = useRef()

  const handleFile = (f) => {
    if (!f) return
    const ext = f.name.split('.').pop().toLowerCase()
    if (!['csv', 'xlsx', 'xls'].includes(ext)) {
      setError('Only CSV and Excel (.xlsx/.xls) files are accepted.')
      return
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File exceeds 10 MB limit.')
      return
    }
    setFile(f)
    setError('')
    setStatus(STATES.IDLE)
    setResult(null)
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }, [])

  const onDragOver = (e) => { e.preventDefault(); setDragging(true) }
  const onDragLeave = () => setDragging(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file || !email) return

    setStatus(STATES.UPLOADING)
    setProgress(0)
    setError('')

    const formData = new FormData()
    formData.append('file', file)
    formData.append('recipient_email', email)

    try {
      const res = await axios.post(`${API_BASE}/api/v1/analyze`, formData, {
        headers: {
          'X-API-Key': API_KEY,
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (e) => {
          setProgress(Math.round((e.loaded * 100) / (e.total || 1)))
        },
      })
      setResult(res.data)
      setStatus(STATES.SUCCESS)
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'An unexpected error occurred.'
      setError(msg)
      setStatus(STATES.ERROR)
    }
  }

  const reset = () => {
    setStatus(STATES.IDLE)
    setFile(null)
    setEmail('')
    setResult(null)
    setError('')
    setProgress(0)
  }

  return (
    <div className="layout">
      {/* Decorative background shapes */}
      <div className="bg-shape bg-shape-1" />
      <div className="bg-shape bg-shape-2" />

      <header className="site-header">
        <div className="header-inner">
          <div className="logo-block">
            <svg className="logo-icon" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="6" fill="var(--ink)" />
              <path d="M8 22 L16 10 L24 22" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              <circle cx="16" cy="10" r="2" fill="var(--accent)" />
              <line x1="11" y1="19" x2="21" y2="19" stroke="var(--paper)" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
            <span className="logo-text">Rabbitt<em>AI</em></span>
          </div>
          <nav className="header-nav">
            <a href={`${API_BASE}/docs`} target="_blank" rel="noopener" className="nav-link">API Docs</a>
            <a href={`${API_BASE}/redoc`} target="_blank" rel="noopener" className="nav-link">ReDoc</a>
          </nav>
        </div>
      </header>

      <main className="main-content">
        <section className="hero">
          <div className="hero-eyebrow">Q1 2026 · Sales Intelligence</div>
          <h1 className="hero-title">
            From raw data to<br />
            <span className="title-accent">executive insight</span>
          </h1>
          <p className="hero-sub">
            Upload your sales CSV or Excel file. Our AI distills the numbers into a
            professional executive briefing — delivered straight to your inbox.
          </p>
        </section>

        <div className="card-container">
          {status === STATES.SUCCESS && result ? (
            <SuccessCard result={result} onReset={reset} />
          ) : (
            <UploadCard
              file={file}
              email={email}
              status={status}
              error={error}
              progress={progress}
              dragging={dragging}
              fileInputRef={fileInputRef}
              onFile={handleFile}
              onEmail={setEmail}
              onSubmit={handleSubmit}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
            />
          )}
        </div>

        <div className="steps-row">
          {[
            { n: '01', label: 'Upload', desc: 'Drop your CSV or Excel sales file — up to 10 MB.' },
            { n: '02', label: 'Analyze', desc: 'AI parses the data and generates a narrative summary.' },
            { n: '03', label: 'Deliver', desc: 'A formatted report lands in your inbox within seconds.' },
          ].map(s => (
            <div className="step" key={s.n}>
              <span className="step-number">{s.n}</span>
              <strong className="step-label">{s.label}</strong>
              <p className="step-desc">{s.desc}</p>
            </div>
          ))}
        </div>
      </main>

      <footer className="site-footer">
        <span>© 2026 Rabbitt AI · Sales Insight Automator</span>
        <span className="footer-sep">·</span>
        <span>Built with FastAPI · React · Gemini</span>
      </footer>
    </div>
  )
}

function UploadCard({ file, email, status, error, progress, dragging, fileInputRef, onFile, onEmail, onSubmit, onDrop, onDragOver, onDragLeave }) {
  const isLoading = status === STATES.UPLOADING
  const canSubmit = file && email && !isLoading

  return (
    <div className="upload-card">
      <div className="card-label">New Analysis</div>

      <div
        className={`drop-zone ${dragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => !file && fileInputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          style={{ display: 'none' }}
          onChange={(e) => onFile(e.target.files[0])}
        />
        {file ? (
          <div className="file-info">
            <FileIcon ext={file.name.split('.').pop()} />
            <div className="file-meta">
              <span className="file-name">{file.name}</span>
              <span className="file-size">{formatBytes(file.size)}</span>
            </div>
            <button className="file-remove" onClick={(e) => { e.stopPropagation(); onFile(null); }} aria-label="Remove file">
              ✕
            </button>
          </div>
        ) : (
          <div className="drop-prompt">
            <svg className="drop-icon" viewBox="0 0 48 48" fill="none">
              <path d="M24 8v24M14 18l10-10 10 10" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M8 36h32v4H8z" fill="currentColor" opacity="0.15" rx="2"/>
              <rect x="8" y="36" width="32" height="4" rx="2" fill="currentColor" opacity="0.3"/>
            </svg>
            <p className="drop-text">Drop your file here</p>
            <p className="drop-sub">CSV or XLSX · Max 10 MB</p>
          </div>
        )}
      </div>

      <div className="form-section">
        <label className="field-label" htmlFor="email-input">
          Recipient Email
        </label>
        <input
          id="email-input"
          className="text-input"
          type="email"
          placeholder="exec@company.com"
          value={email}
          onChange={(e) => onEmail(e.target.value)}
          disabled={isLoading}
          autoComplete="email"
        />
      </div>

      {error && (
        <div className="error-banner" role="alert">
          <span className="error-icon">⚠</span>
          {error}
        </div>
      )}

      {isLoading && (
        <div className="progress-block">
          <div className="progress-bar-track">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
          </div>
          <div className="progress-steps">
            <ProgressStep active={progress >= 0} done={progress >= 33} label="Uploading" />
            <ProgressStep active={progress >= 33} done={progress >= 66} label="Analyzing with AI" />
            <ProgressStep active={progress >= 66} done={progress >= 100} label="Sending email" />
          </div>
        </div>
      )}

      <button
        className={`submit-btn ${canSubmit ? 'active' : 'disabled'}`}
        onClick={handleButtonClick}
        disabled={!canSubmit}
        aria-busy={isLoading}
      >
        {isLoading ? (
          <span className="btn-loading"><span className="spinner" />Processing…</span>
        ) : (
          <span>Generate & Send Report →</span>
        )}
      </button>

      {/* Helper: fix event propagation */}
      {null}
    </div>
  )

  function handleButtonClick(e) {
    e.preventDefault()
    onSubmit(e)
  }
}

function SuccessCard({ result, onReset }) {
  return (
    <div className="success-card">
      <div className="success-icon-wrap">
        <svg viewBox="0 0 48 48" fill="none" className="success-icon">
          <circle cx="24" cy="24" r="22" fill="var(--teal)" opacity="0.12"/>
          <circle cx="24" cy="24" r="22" stroke="var(--teal)" strokeWidth="2"/>
          <path d="M14 24l7 7 13-14" stroke="var(--teal)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
      <h2 className="success-title">Report Delivered</h2>
      <p className="success-sub">
        Your AI-generated sales briefing has been sent to <strong>{result.recipient}</strong>
      </p>

      <div className="result-meta">
        <div className="meta-chip">
          <span className="meta-key">File</span>
          <span className="meta-val">{result.filename}</span>
        </div>
        <div className="meta-chip">
          <span className="meta-key">Rows</span>
          <span className="meta-val">{result.data_stats?.rows ?? '—'}</span>
        </div>
        <div className="meta-chip">
          <span className="meta-key">Columns</span>
          <span className="meta-val">{result.data_stats?.columns?.length ?? '—'}</span>
        </div>
      </div>

      {result.summary_preview && (
        <div className="preview-block">
          <div className="preview-label">Summary Preview</div>
          <p className="preview-text">{result.summary_preview}</p>
        </div>
      )}

      <button className="reset-btn" onClick={onReset}>Analyze Another File</button>
    </div>
  )
}

function FileIcon({ ext }) {
  const color = ext === 'csv' ? 'var(--teal)' : 'var(--gold)'
  return (
    <div className="file-icon" style={{ '--icon-color': color }}>
      {ext.toUpperCase()}
    </div>
  )
}

function ProgressStep({ active, done, label }) {
  return (
    <div className={`p-step ${active ? 'active' : ''} ${done ? 'done' : ''}`}>
      <span className="p-dot">{done ? '✓' : ''}</span>
      <span className="p-label">{label}</span>
    </div>
  )
}
