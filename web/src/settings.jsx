import { useEffect, useState } from 'react';
import {
  ArrowRight,
  Cable,
  Check,
  ChevronDown,
  Eye,
  EyeOff,
  KeyRound,
  Plug,
  RotateCcw,
  Search,
  Server,
  Sparkles,
} from 'lucide-react';
import {
  ACTIVE,
  Collapsible,
  Notice,
  Spinner,
  Status,
  request,
} from './ui.jsx';

export function Settings({ workspace, refresh, onSaved }) {
  const [kind, setKind] = useState(
    workspace.embedding_ready && !workspace.generation_ready ? 'generation' : 'embedding'
  );
  const [data, setData] = useState(null);
  const [drafts, setDrafts] = useState({});
  const [showKey, setShowKey] = useState(false);
  const [pending, setPending] = useState('');
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    let active = true;
    request('/settings')
      .then(config => {
        if (!active) return;
        setData(config);
        setDrafts({
          embedding: { ...config.embedding },
          generation: { ...config.generation },
        });
      })
      .catch(error => {
        if (active) setFeedback({ tone: 'error', text: error.message });
      });
    return () => {
      active = false;
    };
  }, []);

  function edit(patch) {
    setDrafts(previous => ({ ...previous, [kind]: { ...previous[kind], ...patch } }));
    setFeedback(null);
  }

  async function submit(action) {
    const current = drafts[kind];
    setPending(action);
    setFeedback(null);
    const payload = {
      base_url: current.base_url,
      model: current.model,
      api_key: current.api_key ?? null,
      ...(kind === 'embedding'
        ? {
            dimensions: current.dimensions === '' ? null : Number(current.dimensions) || null,
            batch_size: Number(current.batch_size) || 8,
            query_instruction: current.query_instruction,
          }
        : { system_prompt: current.system_prompt }),
    };

    try {
      const result = await request('/settings/' + kind + (action === 'test' ? '/test' : ''), {
        method: action === 'test' ? 'POST' : 'PUT',
        data: payload,
      });

      if (action === 'save') {
        setDrafts(previous => ({ ...previous, [kind]: result }));
        setData(previous => ({ ...previous, [kind]: result }));
        setShowKey(false);
        onSaved();
        await refresh();
      }
      setFeedback({ tone: 'success', text: result.message || 'Settings successfully saved.' });
    } catch (error) {
      setFeedback({ tone: 'error', text: error.message });
    } finally {
      setPending('');
    }
  }

  const current = drafts[kind];
  const busy = kind === 'embedding' && ACTIVE.has(workspace.job?.state);

  return (
    <div className="page settings-page">
      <header className="page-heading">
        <div className="page-title-group">
          <h1>Model Settings</h1>
          <p className="page-subtext">Configure OpenAI-compatible endpoints for Vector Embedding and LLM Answer Generation.</p>
        </div>
      </header>

      <div className="settings-layout-grid">
        {/* Navigation Sidebar */}
        <nav className="settings-nav-sidebar" aria-label="Model connection tabs">
          {[
            ['embedding', 'Embedding Model', Search, 'Vector indexing and retrieval'],
            ['generation', 'Generation Model', Sparkles, 'Synthesize cited answers'],
          ].map(([key, title, Icon, subtitle]) => {
            const isSelected = kind === key;
            const isConfigured = Boolean(data?.[key]?.configured);

            return (
              <button
                key={key}
                className={'settings-nav-card' + (isSelected ? ' selected' : '')}
                type="button"
                aria-pressed={isSelected}
                disabled={Boolean(pending)}
                onClick={() => {
                  setKind(key);
                  setShowKey(false);
                  setFeedback(null);
                }}
              >
                <div className="settings-nav-icon">
                  <Icon size={18} />
                </div>
                <div className="settings-nav-info">
                  <div className="settings-nav-title-row">
                    <strong>{title}</strong>
                    <span className={'status-dot-mini ' + (isConfigured ? 'ready' : 'unconfigured')} />
                  </div>
                  <small>{subtitle}</small>
                </div>
                <ArrowRight size={14} className="settings-nav-arrow" />
              </button>
            );
          })}
        </nav>

        {/* Main Settings Form */}
        {current ? (
          <form
            className="panel connection-form-card"
            onSubmit={event => {
              event.preventDefault();
              if (!pending && !busy) submit('save');
            }}
          >
            <header className="connection-card-header">
              <div className="connection-header-info">
                <div className="connection-title-row">
                  <Server size={18} className="text-accent" />
                  <h2>{kind === 'embedding' ? 'Embedding Connection' : 'Generation Connection'}</h2>
                </div>
                <p className="muted">Standard OpenAI-compatible API protocol</p>
              </div>

              <Status ready={Boolean(data?.[kind]?.configured)}>
                {data?.[kind]?.configured ? 'Configured' : 'Not Configured'}
              </Status>
            </header>

            <div className="form-fields-grid">
              <label className="form-field-label">
                <span>API Base URL</span>
                <input
                  type="url"
                  value={current.base_url}
                  placeholder="https://api.openai.com/v1"
                  required
                  onChange={event => edit({ base_url: event.target.value })}
                />
                <small className="form-field-hint">Include version path (e.g. /v1)</small>
              </label>

              <label className="form-field-label">
                <span>Model Identifier</span>
                <input
                  value={current.model}
                  placeholder={kind === 'embedding' ? 'text-embedding-3-small' : 'gpt-4o-mini'}
                  required
                  onChange={event => edit({ model: event.target.value })}
                />
                <small className="form-field-hint">Exact model ID recognized by provider</small>
              </label>
            </div>

            <div className="api-key-section">
              <label className="form-field-label">
                <span>API Key</span>
                <div className="password-input-group">
                  <span className="key-input-icon">
                    <KeyRound size={15} />
                  </span>
                  <input
                    type={showKey ? 'text' : 'password'}
                    name="model-key"
                    autoComplete="off"
                    value={current.api_key || ''}
                    placeholder={
                      current.stored_key && current.api_key !== ''
                        ? 'Key saved locally · leave empty to preserve'
                        : current.has_key && !current.stored_key
                        ? `Loaded from env (${current.key_env})`
                        : 'Enter your API authorization key'
                    }
                    onChange={event => edit({ api_key: event.target.value || null })}
                  />
                  {current.api_key && (
                    <button
                      className="icon-button key-visibility-btn"
                      type="button"
                      aria-label={showKey ? 'Hide key' : 'Show key'}
                      onClick={() => setShowKey(val => !val)}
                    >
                      {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  )}
                </div>
              </label>

              {current.stored_key && (
                <div className="key-actions-row">
                  <button
                    className="text-button key-clear-btn"
                    type="button"
                    onClick={() => edit({ api_key: current.api_key === '' ? null : '' })}
                  >
                    {current.api_key === '' ? 'Restore saved key' : 'Clear saved key from disk'}
                  </button>
                </div>
              )}
            </div>

            {/* Custom Collapsible replacing native <details><summary> */}
            <Collapsible
              title="Advanced Connection Parameters"
              key={kind}
              className="settings-advanced-panel"
            >
              {kind === 'embedding' ? (
                <div className="advanced-fields-box">
                  <div className="form-fields-grid">
                    <label className="form-field-label">
                      <span>Vector Dimensions</span>
                      <input
                        type="number"
                        min="0"
                        value={current.dimensions ?? ''}
                        placeholder="Provider default (e.g. 1024)"
                        onChange={event => edit({ dimensions: event.target.value })}
                      />
                      <small className="form-field-hint">Must match target vector library</small>
                    </label>

                    <label className="form-field-label">
                      <span>Batch Size</span>
                      <input
                        type="number"
                        min="1"
                        max="1024"
                        value={current.batch_size}
                        onChange={event => edit({ batch_size: event.target.value })}
                      />
                      <small className="form-field-hint">Texts submitted per embedding request</small>
                    </label>
                  </div>

                  <label className="form-field-label mt-3">
                    <span>Query Instruction Prefix</span>
                    <textarea
                      rows="2"
                      value={current.query_instruction}
                      onChange={event => edit({ query_instruction: event.target.value })}
                    />
                    <small className="form-field-hint">
                      Prepend prefix required by asymmetric embedding models (e.g. Qwen/BGE)
                    </small>
                  </label>
                </div>
              ) : (
                <div className="advanced-fields-box">
                  <label className="form-field-label">
                    <span>System Prompt</span>
                    <textarea
                      className="prompt-textarea"
                      rows="8"
                      value={current.system_prompt}
                      onChange={event => edit({ system_prompt: event.target.value })}
                    />
                    <small className="form-field-hint">
                      Directs how citations and answers are synthesized from retrieved snippets
                    </small>
                  </label>

                  <div className="mt-2">
                    <button
                      className="button quiet sm"
                      type="button"
                      onClick={() => edit({ system_prompt: data.default_prompt })}
                    >
                      <RotateCcw size={14} />
                      <span>Restore Default Prompt</span>
                    </button>
                  </div>
                </div>
              )}
            </Collapsible>

            {feedback && <Notice tone={feedback.tone}>{feedback.text}</Notice>}
            {busy && (
              <Notice tone="info">
                Vector indexing is currently active. Finish or pause the job before changing embedding settings.
              </Notice>
            )}

            <footer className="form-actions-footer">
              <button
                className="button secondary"
                type="button"
                disabled={Boolean(pending)}
                onClick={() => submit('test')}
              >
                {pending === 'test' ? <Spinner size={15} /> : <Plug size={15} />}
                <span>Test Connection</span>
              </button>
              <button
                className="button primary"
                type="submit"
                disabled={Boolean(pending) || busy}
              >
                {pending === 'save' && <Spinner size={15} />}
                <span>Save Settings</span>
              </button>
            </footer>
          </form>
        ) : feedback ? (
          <Notice tone={feedback.tone}>{feedback.text}</Notice>
        ) : (
          <div className="loading-card panel">
            <Cable size={22} className="spin text-accent" />
            <p>Loading model configurations…</p>
          </div>
        )}
      </div>
    </div>
  );
}
