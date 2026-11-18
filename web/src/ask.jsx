import { useState, useMemo } from 'react';
import {
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Check,
  Columns2,
  Copy,
  ExternalLink,
  FileText,
  GitMerge,
  Layers,
  ListTree,
  Sparkles,
  Zap,
} from 'lucide-react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  CodeBlock,
  Collapsible,
  CustomSelect,
  Notice,
  ScoreBar,
  Spinner,
  STRATEGIES,
  request,
} from './ui.jsx';

const EXAMPLES = [
  {
    label: 'Group and aggregate',
    question: 'How do I group by two columns and compute the mean of a third column?',
    icon: ListTree,
    desc: 'Aggregation over multi-column groupings',
  },
  {
    label: 'Merge two DataFrames',
    question: 'How do I merge two DataFrames on two keys and validate that the keys are unique?',
    icon: GitMerge,
    desc: 'Safe relational joins with key validation',
  },
  {
    label: 'Read filtered CSV',
    question: 'How can I read selected columns from a CSV and parse one column as dates?',
    icon: FileText,
    desc: 'Optimized I/O and date parsing parameters',
  },
];

function citationLinks(markdown) {
  return markdown
    .split(/(\x60{3}[\s\S]*?(?:\x60{3}|$)|~~~[\s\S]*?(?:~~~|$)|\x60[^\x60\n]*\x60)/g)
    .map((part, index) =>
      index % 2 ? part : part.replace(/(?<!!)\[([0-9]+)\](?!\()/g, '[\\[$1\\]](#citation-$1)')
    )
    .join('');
}

function Passage({ hit }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(hit.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="passage-body">
      <div className="passage-viewer">
        <div className="passage-viewer-header">
          <span className="passage-viewer-title">Doc Passage Excerpt</span>
          <button
            type="button"
            className="passage-copy-btn"
            onClick={handleCopy}
            aria-label={copied ? 'Copied excerpt' : 'Copy excerpt'}
            title={copied ? 'Copied' : 'Copy excerpt'}
          >
            {copied ? (
              <>
                <Check size={12} className="text-emerald" />
                <span>Copied</span>
              </>
            ) : (
              <>
                <Copy size={12} />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>

        <div className="passage-scroll-box" tabIndex={0} role="region" aria-label="Passage excerpt text">
          <pre className="passage-text-pre">{hit.text}</pre>
        </div>
      </div>

      <div className="passage-sources-list">
        {hit.sources.map(source => (
          <a
            href={source.url}
            target="_blank"
            rel="noreferrer"
            key={source.section_id}
            className="passage-source-link"
          >
            <span>{source.heading_path}</span>
            <ArrowUpRight size={13} aria-hidden="true" />
          </a>
        ))}
      </div>
    </div>
  );
}

function Answer({ data, strategy, retrievalMs }) {
  const [selected, setSelected] = useState(data.citations[0]?.n);
  const [copied, setCopied] = useState(false);
  const [hoveredCitation, setHoveredCitation] = useState(null);

  const active = data.citations.find(citation => citation.n === selected) || data.citations[0];

  if (data.refused) {
    return (
      <div className="refusal-card panel">
        <div className="refusal-icon-wrap">
          <BookOpen size={24} />
        </div>
        <div className="refusal-content">
          <h3>No answer found in documentation</h3>
          <p>{data.answer}</p>
        </div>
      </div>
    );
  }

  const totalTimeSeconds = ((data.latency_ms + retrievalMs) / 1000).toFixed(2);

  return (
    <div className="answer-layout">
      {/* Main answer article */}
      <article className="panel answer-paper">
        <header className="answer-header">
          <div className="answer-meta">
            <span className="answer-pill">
              <Zap size={13} className="text-accent" />
              <span>{STRATEGIES[strategy]}</span>
            </span>
            <span className="answer-time">{totalTimeSeconds}s latency</span>
          </div>

          <button
            type="button"
            className="icon-button"
            aria-label={copied ? 'Answer copied' : 'Copy answer'}
            title={copied ? 'Copied' : 'Copy answer'}
            onClick={async () => {
              try {
                await navigator.clipboard.writeText(data.answer);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
              } catch {
                setCopied(false);
              }
            }}
          >
            {copied ? <Check size={16} className="text-emerald" /> : <Copy size={16} />}
          </button>
        </header>

        <div className="prose">
          <Markdown
            remarkPlugins={[remarkGfm]}
            disallowedElements={['img']}
            components={{
              pre({ node, children, ...props }) {
                const block = node?.children[0];
                if (block?.tagName !== 'code') return <pre {...props}>{children}</pre>;
                const language = block.properties.className?.find(name => name.startsWith('language-'));
                const code = block.children.map(part => part.value || '').join('').replace(/\n$/, '');
                return <CodeBlock code={code} language={language ? language.slice(9) : 'text'} />;
              },
              code({ node, children, ...props }) {
                return <code className="inline-code" {...props}>{children}</code>;
              },
              a: ({ href, children }) => {
                const id = href?.match(/^#citation-(\d+)$/);
                if (!id) {
                  return (
                    <a href={href} target="_blank" rel="noreferrer" className="external-prose-link">
                      {children}
                      <ExternalLink size={12} className="inline-ext-icon" />
                    </a>
                  );
                }
                const number = Number(id[1]);
                const hit = data.citations.find(citation => citation.n === number);
                if (!hit) return <span>{children}</span>;

                const isSelected = number === active?.n;
                const isHovered = hoveredCitation === number;

                return (
                  <span className="citation-wrap">
                    <button
                      type="button"
                      className={'citation-pill' + (isSelected ? ' selected' : '')}
                      aria-label={'Show source ' + number}
                      onMouseEnter={() => setHoveredCitation(number)}
                      onMouseLeave={() => setHoveredCitation(null)}
                      onClick={() => {
                        setSelected(number);
                        if (window.matchMedia('(max-width: 860px)').matches) {
                          document.getElementById('source-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                      }}
                    >
                      {number}
                    </button>
                    {isHovered && (
                      <span className="citation-popover" role="tooltip">
                        <strong>Source [{number}]</strong>
                        <small>{hit.sources[0]?.heading_path || 'Pandas Documentation'}</small>
                      </span>
                    )}
                  </span>
                );
              },
            }}
          >
            {citationLinks(data.answer)}
          </Markdown>
        </div>
      </article>

      {/* Sources sidebar */}
      <aside className="panel sources-panel" id="source-panel" aria-label="Sources">
        <header className="sources-header">
          <div className="sources-header-title">
            <BookOpen size={16} className="text-accent" />
            <h3>Cited Sources ({data.citations.length})</h3>
          </div>
          <span className="sources-header-sub">Click reference to inspect</span>
        </header>

        <div className="sources-list">
          {data.citations.map(hit => {
            const isSelected = active?.n === hit.n;
            return (
              <div
                className={'source-card' + (isSelected ? ' active' : '')}
                key={hit.n}
                id={`source-item-${hit.n}`}
              >
                <button
                  type="button"
                  className="source-toggle-btn"
                  aria-expanded={isSelected}
                  onClick={() => setSelected(hit.n)}
                >
                  <span className={'source-badge' + (isSelected ? ' active' : '')}>{hit.n}</span>
                  <div className="source-heading-meta">
                    <span className="source-heading-title">{hit.sources[0]?.heading_path}</span>
                    <span className="source-doc-id">{hit.doc_id}</span>
                  </div>
                </button>
                {isSelected && <Passage hit={hit} />}
              </div>
            );
          })}
        </div>
      </aside>
    </div>
  );
}

function passageKey(hit) {
  return JSON.stringify([hit.doc_id, hit.text]);
}

function Comparison({ results, top, setTop }) {
  const topOptions = Array.from({ length: 10 }, (_, index) => ({
    value: index + 1,
    label: `Top ${index + 1} passages`,
  }));

  const fixedPassages = useMemo(() => new Set(results.fixed_size?.slice(0, top).map(passageKey) || []), [results, top]);
  const structuredPassages = useMemo(() => new Set(results.structure_aware?.slice(0, top).map(passageKey) || []), [results, top]);

  return (
    <section className="panel ranking-section">
      <header className="ranking-header">
        <div className="ranking-title-area">
          <div className="ranking-title-row">
            <Layers size={18} className="text-accent" />
            <h2>Retrieval Strategy Comparison</h2>
          </div>
          <p className="muted">Evaluating chunking performance using the exact same question and embedding model.</p>
        </div>
        <div className="ranking-controls">
          <CustomSelect
            value={top}
            options={topOptions}
            onChange={val => setTop(Number(val))}
            ariaLabel="Results per strategy"
          />
        </div>
      </header>

      <div className="ranking-grid">
        {['fixed_size', 'structure_aware'].map(strategy => {
          const hits = results[strategy]?.slice(0, top) || [];
          const otherSet = strategy === 'fixed_size' ? structuredPassages : fixedPassages;

          return (
            <div key={strategy} className="ranking-column" aria-label={STRATEGIES[strategy]}>
              <div className="ranking-column-header">
                <h3>{STRATEGIES[strategy]}</h3>
                <span className="ranking-count-badge">{hits.length} retrieved</span>
              </div>

              <div className="ranking-items">
                {hits.map((hit, index) => {
                  const isCommon = otherSet.has(passageKey(hit));
                  return (
                    <div className={'rank-card' + (isCommon ? ' is-common-match' : '')} key={hit.chunk_id}>
                      <div className="rank-card-head">
                        <div className="rank-num-title">
                          <span className="rank-num">{String(index + 1).padStart(2, '0')}</span>
                          <strong className="rank-heading">{hit.sources[0]?.heading_path}</strong>
                        </div>
                        <div className="rank-score-cell">
                          <ScoreBar score={hit.score} />
                        </div>
                      </div>

                      {isCommon && (
                        <div className="common-hit-badge" title="Retrieved by both chunking strategies">
                          <Sparkles size={11} /> Both strategies matched
                        </div>
                      )}

                      <p className="rank-excerpt">{hit.text.replace(/\s+/g, ' ')}</p>

                      <Collapsible
                        title="Read full excerpt"
                        className="rank-collapsible"
                        extra={
                          <a
                            href={hit.sources[0]?.url}
                            target="_blank"
                            rel="noreferrer"
                            className="rank-source-link"
                            onClick={e => e.stopPropagation()}
                          >
                            <span>Docs</span>
                            <ArrowUpRight size={12} />
                          </a>
                        }
                      >
                        <Passage hit={hit} />
                      </Collapsible>
                    </div>
                  );
                })}

                {!hits.length && (
                  <div className="empty-ranking-notice">
                    <p>No passages found for this strategy.</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export function Ask({ workspace, context, state, setState, navigate }) {
  const [stage, setStage] = useState('');
  const [error, setError] = useState('');
  const [top, setTop] = useState(5);

  const { question, mode, run } = state;
  const strategy = state.strategy || workspace.default_strategy;
  const indexed = workspace.documents.some(doc => doc.ready);
  const canRetrieve = workspace.embedding_ready && indexed;
  const canAnswer = canRetrieve && workspace.generation_ready;
  const ready = mode === 'compare' ? canRetrieve : canAnswer;
  const answer = run?.answers[strategy];
  const activeLibrary = workspace.libraries.find(library => library.id === workspace.active);

  const strategyOptions = Object.entries(STRATEGIES).map(([val, label]) => ({
    value: val,
    label,
  }));

  async function submit(text, requestedMode = mode) {
    const value = text.trim();
    if (!value || stage || (requestedMode === 'compare' ? !canRetrieve : !canAnswer)) return;
    setError('');
    setState(previous => ({
      ...previous,
      question: value,
      mode: requestedMode,
      run: run?.question === value ? run : null,
    }));
    let next = run?.question === value ? run : null;
    try {
      if (!next) {
        setStage('Searching both vector indexes…');
        const result = await request('/retrieve', { method: 'POST', data: { question: value } });
        next = { ...result, context, answers: {} };
        setState(previous => ({ ...previous, run: next }));
      }
      if (requestedMode === 'answer' && !next.answers[strategy]) {
        setStage('Generating cited answer with ' + STRATEGIES[strategy] + '…');
        const response = await request('/answer', {
          method: 'POST',
          data: { retrieval_id: next.id, strategy },
        });
        const completed = { ...next, answers: { ...next.answers, [strategy]: response } };
        setState(previous => ({ ...previous, run: completed }));
      }
    } catch (failure) {
      if (failure.message.includes('retrieval is no longer current')) {
        setState(previous => ({ ...previous, run: null }));
      }
      setError(failure.message);
    } finally {
      setStage('');
    }
  }

  return (
    <div className={'ask-page' + (run ? ' has-result' : '')}>
      <div className="ask-start">
        <header className="ask-intro">
          <div className="ask-hero-badge">
            <Sparkles size={14} className="text-accent" />
            <span>pandas v3.1.1 Documentation Assistant</span>
          </div>
          <h1>
            Ask the pandas docs<span className="accent-dot">.</span>
          </h1>
          {!run && (
            <p className="hero-subtext">
              High-precision answers grounded in official documentation with exact section citations.
            </p>
          )}
        </header>

        {/* Notices for unconfigured states */}
        {!workspace.embedding_ready && (
          <Notice tone="error">
            Configure an embedding connection to search documentation.{' '}
            <a href="/settings" onClick={event => navigate('/settings', event)}>
              Open Settings <ArrowUpRight size={13} />
            </a>
          </Notice>
        )}
        {workspace.embedding_ready && !indexed && (
          <Notice tone="info">
            Load the included preset library or build an index to begin.{' '}
            <a href="/library" onClick={event => navigate('/library', event)}>
              Open Library <ArrowUpRight size={13} />
            </a>
          </Notice>
        )}
        {canRetrieve && !workspace.generation_ready && (
          <Notice tone="info">
            Configure a generation model to get answers. Comparison and vector search are already active.{' '}
            <a href="/settings" onClick={event => navigate('/settings', event)}>
              Open Settings <ArrowUpRight size={13} />
            </a>
          </Notice>
        )}

        {/* Modern Composer */}
        <form
          className="composer"
          onSubmit={event => {
            event.preventDefault();
            submit(question);
          }}
        >
          <div className="composer-top">
            <textarea
              aria-label="Question"
              value={question}
              rows={run ? 1 : 2}
              maxLength={6000}
              placeholder="Ask a question about pandas operations, API parameters, indexing, etc..."
              onChange={event => setState(previous => ({ ...previous, question: event.target.value }))}
              onKeyDown={event => {
                if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
                  event.preventDefault();
                  submit(question);
                }
              }}
            />
          </div>

          <div className="composer-actions">
            <div className="segmented-control" role="radiogroup" aria-label="Question mode">
              <button
                type="button"
                role="radio"
                aria-checked={mode === 'answer'}
                className={'segmented-btn' + (mode === 'answer' ? ' active' : '')}
                onClick={() => setState(previous => ({ ...previous, mode: 'answer' }))}
              >
                <Sparkles size={14} />
                <span>Answer</span>
              </button>
              <button
                type="button"
                role="radio"
                aria-checked={mode === 'compare'}
                className={'segmented-btn' + (mode === 'compare' ? ' active' : '')}
                onClick={() => setState(previous => ({ ...previous, mode: 'compare' }))}
              >
                <Columns2 size={14} />
                <span>Compare</span>
              </button>
            </div>

            <div className="composer-right">
              {mode === 'answer' && (
                <CustomSelect
                  value={strategy}
                  options={strategyOptions}
                  onChange={val => setState(previous => ({ ...previous, strategy: val }))}
                  ariaLabel="Retrieval strategy"
                />
              )}

              <button
                type="submit"
                className="button primary composer-submit"
                disabled={!ready || !question.trim() || Boolean(stage)}
              >
                {stage ? <Spinner /> : <ArrowRight size={16} />}
                <span>{mode === 'compare' ? 'Compare' : 'Ask'}</span>
              </button>
            </div>
          </div>

          <div className="composer-footer-hint">
            <span>
              Press <kbd>↵</kbd> to submit, <kbd>Shift + ↵</kbd> for new line
            </span>
          </div>
        </form>

        {stage && (
          <div className="request-status-banner" role="status">
            <Spinner size={16} />
            <span>{stage}</span>
          </div>
        )}

        {error && <Notice tone="error">{error}</Notice>}

        {/* Suggestion Examples */}
        {!run && !stage && (
          <div className="ask-examples-grid">
            {EXAMPLES.map(({ label, question: example, icon: Icon, desc }) => (
              <button
                key={label}
                type="button"
                className="example-card"
                disabled={!ready}
                onClick={() => submit(example)}
              >
                <div className="example-icon-wrapper">
                  <Icon size={16} />
                </div>
                <div className="example-texts">
                  <strong>{label}</strong>
                  <p>{desc}</p>
                </div>
                <ArrowRight size={14} className="example-arrow" aria-hidden="true" />
              </button>
            ))}
          </div>
        )}

        {run && run.question !== question.trim() && (
          <p className="previous-question-tag">Showing results for “{run.question}”</p>
        )}
        {run && run.question === question.trim() && activeLibrary && (
          <div className="active-library-meta">
            <span className="dot-indicator" />
            <span>Active Library: {activeLibrary.name}</span>
          </div>
        )}
      </div>

      {run && mode === 'compare' && <Comparison results={run.results} top={top} setTop={setTop} />}

      {answer && mode === 'answer' && (
        <Answer
          key={run.id + strategy}
          data={answer}
          strategy={strategy}
          retrievalMs={run.latency_ms}
        />
      )}

      {run && !answer && mode === 'answer' && !stage && !error && (
        <Notice tone="info">
          Passages are ready. Click <strong>Ask</strong> to generate an answer with {STRATEGIES[strategy]}.
        </Notice>
      )}
    </div>
  );
}
