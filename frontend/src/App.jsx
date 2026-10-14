import { useState } from 'react'
import {
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Check,
  ChevronDown,
  Clock3,
  ExternalLink,
  FileText,
  Gavel,
  Landmark,
  LoaderCircle,
  Menu,
  MessageSquareText,
  Plus,
  Scale,
  Search,
  ShieldCheck,
  Sparkles,
  X,
} from 'lucide-react'
import './App.css'

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/$/, '')

const examples = [
  {
    icon: ShieldCheck,
    title: 'Rights during arrest',
    question: 'What are my rights if I am arrested in New Zealand?',
    tag: 'Section 23',
  },
  {
    icon: Scale,
    title: 'Freedom from discrimination',
    question: 'What protection does the Bill of Rights provide against discrimination?',
    tag: 'Section 19',
  },
  {
    icon: BookOpen,
    title: 'Freedom of expression',
    question: 'Does New Zealand law protect freedom of expression?',
    tag: 'Section 14',
  },
]

function getCitationLabel(citation, index) {
  if (typeof citation === 'string') return citation

  return (
    citation?.label ||
    citation?.section ||
    citation?.provision_label ||
    citation?.title ||
    `Source ${index + 1}`
  )
}

function getCitationUrl(citation) {
  if (typeof citation === 'string') return ''
  return citation?.section_url || citation?.url || citation?.source_url || ''
}

function getCitationDescription(citation) {
  if (typeof citation === 'string') return ''
  return (
    citation?.heading ||
    citation?.title ||
    citation?.description ||
    citation?.text ||
    ''
  )
}

function App() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [menuOpen, setMenuOpen] = useState(false)
  const [history, setHistory] = useState([])

  async function askQuestion(nextQuestion = question) {
    const cleanedQuestion = nextQuestion.trim()

    if (cleanedQuestion.length < 3) {
      setError('Please enter a question with at least 3 characters.')
      return
    }

    setQuestion(cleanedQuestion)
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: cleanedQuestion }),
      })

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        const detail =
          typeof data.detail === 'string'
            ? data.detail
            : 'The research service is temporarily unavailable.'

        throw new Error(
          response.status === 503
            ? 'The research service is unavailable. Check that the backend and its configuration are ready.'
            : detail,
        )
      }

      setResult(data)
      setHistory((previous) => [
        cleanedQuestion,
        ...previous.filter((item) => item !== cleanedQuestion),
      ].slice(0, 5))
    } catch (err) {
      setError(
        err instanceof TypeError
          ? 'Could not connect to the API. Make sure the FastAPI backend is running and CORS is configured.'
          : err.message || 'Something went wrong. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  function startNewQuestion() {
    setQuestion('')
    setResult(null)
    setError('')
    setMenuOpen(false)
  }

  const citations = Array.isArray(result?.citations) ? result.citations : []
  const isAbstained = result?.abstained === true

  return (
    <div className="app-shell">
      {menuOpen && (
        <button
          className="mobile-scrim"
          aria-label="Close navigation"
          onClick={() => setMenuOpen(false)}
        />
      )}

      <aside className={`sidebar ${menuOpen ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark">
            <Scale size={22} strokeWidth={2.1} />
          </div>
          <div className="brand-copy">
            <span className="brand-name">PolicyPilot</span>
            <span className="brand-region">NEW ZEALAND</span>
          </div>
          <button
            className="icon-button sidebar-close"
            onClick={() => setMenuOpen(false)}
            aria-label="Close menu"
          >
            <X size={19} />
          </button>
        </div>

        <button className="new-question-button" onClick={startNewQuestion}>
          <Plus size={18} />
          <span>New research</span>
          <span className="shortcut">⌘ K</span>
        </button>

        <div className="nav-section">
          <p className="nav-label">WORKSPACE</p>
          <button className="nav-item nav-item-active" onClick={startNewQuestion}>
            <MessageSquareText size={17} />
            <span>Legal assistant</span>
            <span className="nav-dot" />
          </button>
          <button
            className="nav-item"
            onClick={() =>
              document.getElementById('legislation')?.scrollIntoView({
                behavior: 'smooth',
              })
            }
          >
            <BookOpen size={17} />
            <span>Legislation library</span>
            <ArrowUpRight className="nav-trailing" size={15} />
          </button>
        </div>

        <div className="nav-section recent-section">
          <div className="nav-label-row">
            <p className="nav-label">RECENT RESEARCH</p>
            <Clock3 size={14} />
          </div>
          {history.length ? (
            history.map((item) => (
              <button
                className="history-item"
                key={item}
                title={item}
                onClick={() => askQuestion(item)}
              >
                <span className="history-dot" />
                <span>{item}</span>
              </button>
            ))
          ) : (
            <p className="empty-history">
              Your recent questions will appear here.
            </p>
          )}
        </div>

        <div className="sidebar-bottom">
          <div className="legislation-mini-card">
            <div className="mini-card-icon">
              <Landmark size={19} />
            </div>
            <div>
              <p className="mini-card-title">One source of truth.</p>
              <p className="mini-card-copy">Official NZ legislation</p>
            </div>
            <ArrowUpRight size={15} className="mini-card-arrow" />
          </div>
          <div className="profile-row">
            <div className="profile-avatar">NZ</div>
            <div className="profile-copy">
              <span>PolicyPilot workspace</span>
              <span>Research preview</span>
            </div>
            <ChevronDown size={16} className="profile-chevron" />
          </div>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="icon-button mobile-menu-button"
              aria-label="Open navigation"
              onClick={() => setMenuOpen(true)}
            >
              <Menu size={20} />
            </button>
            <div className="breadcrumb">
              <span>Workspace</span>
              <span className="breadcrumb-slash">/</span>
              <strong>Legal assistant</strong>
            </div>
          </div>
          <div className="topbar-right">
            <span className="environment-pill">
              <span className="status-dot" />
              AI research preview
            </span>
            <button
              className="topbar-icon"
              title="Start a new question"
              aria-label="Start a new question"
              onClick={startNewQuestion}
            >
              <Plus size={19} />
            </button>
          </div>
        </header>

        <div className="page-content">
          <section className="welcome-section">
            <div className="eyebrow">
              <span className="eyebrow-line" />
              YOUR NEW ZEALAND LEGAL RESEARCH ASSISTANT
            </div>
            <h1>
              The law, made
              <br />
              <span className="headline-accent">a little clearer.</span>
            </h1>
            <p className="welcome-description">
              Ask questions about the New Zealand Bill of Rights Act 1990.
              Get grounded answers, with legislation references you can check.
            </p>

            <div className="trust-row">
              <span>
                <ShieldCheck size={15} />
                Source-backed responses
              </span>
              <span className="trust-divider" />
              <span>
                <FileText size={15} />
                Section-level citations
              </span>
            </div>
          </section>

          <section className="research-composer" aria-label="Ask a legal question">
            <div className="composer-topline">
              <div className="composer-source">
                <div className="source-icon">
                  <Landmark size={17} />
                </div>
                <div>
                  <span className="source-label">RESEARCHING FROM</span>
                  <span className="source-title">
                    NZ Bill of Rights Act 1990
                  </span>
                </div>
              </div>
              <span className="source-version">LEGISLATION</span>
            </div>

            <form
              onSubmit={(event) => {
                event.preventDefault()
                askQuestion()
              }}
            >
              <label className="sr-only" htmlFor="question-input">
                Ask a question about New Zealand legislation
              </label>
              <textarea
                id="question-input"
                value={question}
                onChange={(event) => {
                  setQuestion(event.target.value)
                  if (error) setError('')
                }}
                onKeyDown={(event) => {
                  if (
                    event.key === 'Enter' &&
                    !event.shiftKey &&
                    !event.nativeEvent.isComposing
                  ) {
                    event.preventDefault()
                    askQuestion()
                  }
                }}
                placeholder="Ask a question about your rights..."
                rows={3}
                maxLength={1000}
                disabled={loading}
              />
              <div className="composer-footer">
                <span className="input-hint">
                  <Search size={14} />
                  Answers grounded in the selected Act
                </span>
                <div className="composer-actions">
                  <span className="character-count">{question.length}/1000</span>
                  <button
                    type="submit"
                    className="ask-button"
                    disabled={loading || question.trim().length < 3}
                  >
                    {loading ? (
                      <>
                        <LoaderCircle className="spin" size={17} />
                        Researching
                      </>
                    ) : (
                      <>
                        Ask PolicyPilot
                        <ArrowRight size={17} />
                      </>
                    )}
                  </button>
                </div>
              </div>
            </form>
          </section>

          {error && (
            <div className="error-banner" role="alert">
              <div className="error-icon">
                <X size={17} />
              </div>
              <div>
                <strong>We couldn’t complete that request.</strong>
                <p>{error}</p>
              </div>
              <button
                className="icon-button error-dismiss"
                onClick={() => setError('')}
                aria-label="Dismiss error"
              >
                <X size={17} />
              </button>
            </div>
          )}

          {loading && (
            <div className="loading-card" aria-live="polite">
              <div className="loading-orb">
                <Sparkles size={22} />
              </div>
              <div>
                <strong>Reviewing the legislation</strong>
                <p>Finding relevant sections and preparing your answer…</p>
              </div>
              <LoaderCircle className="spin loading-spinner" size={20} />
            </div>
          )}

          {result && !loading && (
            <section className="answer-section" aria-live="polite">
              <div className="answer-heading-row">
                <div>
                  <div className="answer-eyebrow">
                    <Sparkles size={15} />
                    RESEARCH RESULT
                  </div>
                  <h2>Your answer</h2>
                </div>
                <button
                  className="text-button"
                  onClick={startNewQuestion}
                >
                  <Plus size={16} />
                  New question
                </button>
              </div>

              <div className={`answer-card ${isAbstained ? 'answer-cautious' : ''}`}>
                <div className="answer-card-top">
                  <span className="answer-type">
                    {isAbstained ? (
                      <Search size={15} />
                    ) : (
                      <Check size={15} />
                    )}
                    {isAbstained ? 'Unable to verify' : 'Legislation-based answer'}
                  </span>
                  <span className="answer-source-name">
                    <Scale size={14} />
                    PolicyPilot NZ
                  </span>
                </div>
                <div className="answer-body">
                  {result.answer || 'No answer text was returned by the API.'}
                </div>
                {isAbstained && (
                  <div className="caution-note">
                    PolicyPilot could not verify an answer from the available
                    evidence. Do not treat this response as a legal conclusion.
                  </div>
                )}
                {!isAbstained && citations.length > 0 && (
                  <div className="answer-citation-summary">
                    <ShieldCheck size={16} />
                    Supported by {citations.length}{' '}
                    {citations.length === 1 ? 'reference' : 'references'} from
                    the selected Act.
                  </div>
                )}
              </div>

              <div className="citations-heading">
                <div>
                  <span className="section-kicker">EXPLORE THE EVIDENCE</span>
                  <h3>Legislation references</h3>
                </div>
                <span className="reference-count">
                  {citations.length} {citations.length === 1 ? 'SOURCE' : 'SOURCES'}
                </span>
              </div>

              {citations.length > 0 ? (
                <div className="citation-list">
                  {citations.map((citation, index) => {
                    const label = getCitationLabel(citation, index)
                    const url = getCitationUrl(citation)
                    const description = getCitationDescription(citation)

                    return (
                      <article
                        className="citation-card"
                        key={`${label}-${index}`}
                      >
                        <div className="citation-icon">
                          <FileText size={19} />
                        </div>
                        <div className="citation-copy">
                          <span className="citation-kicker">
                            REFERENCE {String(index + 1).padStart(2, '0')}
                          </span>
                          <h4>{label}</h4>
                          {description && (
                            <p>
                              {description.length > 260
                                ? `${description.slice(0, 257)}…`
                                : description}
                            </p>
                          )}
                          {url && (
                            <a
                              className="citation-link"
                              href={url}
                              target="_blank"
                              rel="noreferrer"
                            >
                              Read official legislation
                              <ExternalLink size={14} />
                            </a>
                          )}
                        </div>
                        {url && (
                          <a
                            className="citation-open"
                            href={url}
                            target="_blank"
                            rel="noreferrer"
                            aria-label={`Open ${label}`}
                          >
                            <ArrowUpRight size={18} />
                          </a>
                        )}
                      </article>
                    )
                  })}
                </div>
              ) : (
                <div className="no-citations">
                  No legislation references were returned for this response.
                </div>
              )}

              <p className="legal-disclaimer">
                <Gavel size={14} />
                Informational research only. This is not legal advice. Check
                the official legislation and consult a qualified lawyer for
                advice about your circumstances.
              </p>
            </section>
          )}

          {!result && !loading && (
            <section className="examples-section">
              <div className="section-heading-row">
                <div>
                  <span className="section-kicker">NOT SURE WHERE TO START?</span>
                  <h2>Explore a question</h2>
                </div>
                <span className="curated-label">
                  <Sparkles size={14} />
                  SUGGESTED TOPICS
                </span>
              </div>

              <div className="example-grid">
                {examples.map((example, index) => {
                  const ExampleIcon = example.icon

                  return (
                    <button
                      className="example-card"
                      key={example.title}
                      onClick={() => askQuestion(example.question)}
                      disabled={loading}
                    >
                      <div className={`example-icon example-icon-${index + 1}`}>
                        <ExampleIcon size={19} />
                      </div>
                      <span className="example-tag">{example.tag}</span>
                      <h3>{example.title}</h3>
                      <p>{example.question}</p>
                      <span className="example-arrow">
                        Explore question <ArrowUpRight size={15} />
                      </span>
                    </button>
                  )
                })}
              </div>
            </section>
          )}

          <section className="legislation-section" id="legislation">
            <div className="legislation-icon">
              <BookOpen size={21} />
            </div>
            <div className="legislation-copy">
              <span className="section-kicker">CURRENT RESEARCH COLLECTION</span>
              <h3>New Zealand Bill of Rights Act 1990</h3>
              <p>
                A focused research experience for exploring rights and
                freedoms under one foundational New Zealand Act.
              </p>
            </div>
            <div className="legislation-badge">
              <span className="status-dot" />
              <span>Source configured</span>
            </div>
          </section>

          <footer className="page-footer">
            <span>© 2026 PolicyPilot NZ</span>
            <span className="footer-separator">·</span>
            <span>Built for clearer legal research</span>
            <a
              href="https://www.legislation.govt.nz/"
              target="_blank"
              rel="noreferrer"
            >
              Official legislation <ArrowUpRight size={13} />
            </a>
          </footer>
        </div>
      </main>
    </div>
  )
}

export default App 