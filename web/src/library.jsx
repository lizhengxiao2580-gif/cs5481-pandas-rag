import { useState } from 'react';
import {
  ArrowUpRight,
  Check,
  ChevronLeft,
  ChevronRight,
  Database,
  FileCode,
  FileUp,
  FolderOpen,
  Pause,
  Play,
  Plus,
  RefreshCw,
  Search,
  Sparkles,
  Square,
  UploadCloud,
  X,
} from 'lucide-react';
import {
  ACTIVE,
  CustomSelect,
  Modal,
  Notice,
  ProgressBar,
  Spinner,
  Status,
  request,
} from './ui.jsx';

const SCOPES = {
  user_guide: 'User guide',
  getting_started: 'Getting started',
  reference: 'API reference',
  'reference/api': 'API reference',
};

const PHASES = {
  prepare: 'Preparing passages',
  embedding: 'Generating vector embeddings',
  fixed_size: 'Writing fixed-window index',
  structure_aware: 'Writing structure-aware index',
  publish: 'Publishing both indexes',
};

const PAGE_SIZE = 12;

function ManageLibraries({ workspace, run, action, feedback, close, navigate }) {
  const [name, setName] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const preset = workspace.preset;
  const presetBinding = workspace.libraries.find(library => library.id === preset?.id && library.has_settings);
  const busy = ACTIVE.has(workspace.job?.state) || Boolean(action);

  function act(path, data) {
    run(path, data, close);
  }

  return (
    <Modal title="Manage Vector Libraries" close={close}>
      {!workspace.embedding_ready && (
        <Notice tone="info">
          Configure an embedding connection before loading or creating a library.{' '}
          <a
            href="/settings"
            onClick={event => {
              close();
              navigate('/settings', event);
            }}
          >
            Open Settings
          </a>
        </Notice>
      )}

      <div className="libraries-container">
        {preset && (
          <div className="library-card preset-card">
            <div className="library-card-icon">
              <Database size={20} className="text-accent" />
            </div>
            <div className="library-card-body">
              <div className="library-card-title-row">
                <h4>{preset.name}</h4>
                <span className="badge-preset">Included Preset</span>
              </div>
              <p className="library-card-meta">
                {preset.pages} indexed documents · {preset.dimensions ? preset.dimensions.toLocaleString() : '1,024'} dims
              </p>
            </div>
            <div className="library-card-actions">
              {workspace.active === preset.id ? (
                <Status ready>Active</Status>
              ) : (
                <div className="inline-actions">
                  {presetBinding && (
                    <button
                      type="button"
                      className="button secondary sm"
                      disabled={busy}
                      onClick={() => act('/libraries/' + preset.id + '/activate', {})}
                    >
                      Switch
                    </button>
                  )}
                  {(!presetBinding || preset.verify) && (
                    <button
                      type="button"
                      className="button primary sm"
                      disabled={!workspace.embedding_ready || busy}
                      onClick={() => act('/libraries/preset')}
                    >
                      {preset.verify ? 'Verify & Load' : 'Load preset'}
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {workspace.libraries
          .filter(library => library.id !== preset?.id)
          .map(library => (
            <div className="library-card" key={library.id}>
              <div className="library-card-icon">
                <FolderOpen size={20} />
              </div>
              <div className="library-card-body">
                <h4>{library.name}</h4>
                <p className="library-card-meta">
                  {library.pages} indexed · {library.model || 'Default model'}
                </p>
              </div>
              <div className="library-card-actions">
                {workspace.active === library.id ? (
                  <Status ready>Active</Status>
                ) : (
                  <div className="inline-actions">
                    {library.has_settings && (
                      <button
                        type="button"
                        className="button secondary sm"
                        disabled={busy}
                        onClick={() => act('/libraries/' + library.id + '/activate', {})}
                      >
                        Switch
                      </button>
                    )}
                    {library.pages > 0 && workspace.embedding_ready && (
                      <button
                        type="button"
                        className="button quiet sm"
                        disabled={busy}
                        title="Check up to three public passages against current embedding model"
                        onClick={() =>
                          act('/libraries/' + library.id + '/activate', { use_current_embedding: true })
                        }
                      >
                        Use current
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
      </div>

      {showCreate ? (
        <form
          className="create-library-box"
          onSubmit={event => {
            event.preventDefault();
            if (name.trim()) act('/libraries', { name: name.trim() });
          }}
        >
          <label className="form-field-label">
            <span>New Library Name</span>
            <input
              value={name}
              maxLength={80}
              onChange={event => setName(event.target.value)}
              placeholder="e.g. Pandas Production Index"
              required
            />
          </label>
          <p className="form-field-hint">
            Binds to your current embedding parameters. You can build indexes after creating it.
          </p>
          <div className="inline-actions mt-3">
            <button
              type="submit"
              className="button primary sm"
              disabled={busy || !workspace.embedding_ready || !name.trim()}
            >
              Create Library
            </button>
            <button type="button" className="button quiet sm" onClick={() => setShowCreate(false)}>
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <button
          type="button"
          className="button quiet create-btn-trigger"
          disabled={busy || !workspace.embedding_ready}
          onClick={() => setShowCreate(true)}
        >
          <Plus size={16} />
          <span>Create a new library</span>
        </button>
      )}

      {action && (
        <div className="request-status-banner" role="status">
          <Spinner size={16} />
          <span>Updating workspace state…</span>
        </div>
      )}

      {feedback?.error && <Notice tone="error">{feedback.message}</Notice>}
    </Modal>
  );
}

function ImportDocument({ close, onImported }) {
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState('');
  const [preview, setPreview] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function submit(event) {
    event.preventDefault();
    if (!file || busy || preview?.duplicate) return;
    setBusy(true);
    setError('');
    const data = new FormData();
    data.append('file', file);
    if (url.trim()) data.append('source_url', url.trim());
    data.append('commit', String(Boolean(preview)));
    try {
      const result = await request('/documents/import', { method: 'POST', data });
      if (preview) onImported(result.message);
      else setPreview(result);
    } catch (failure) {
      setError(failure.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal title="Import Pandas HTML Documentation" close={close}>
      <form className="import-modal-form" onSubmit={submit}>
        <label className={'file-drop-zone' + (file ? ' has-file' : '')}>
          <UploadCloud size={32} className="upload-icon" />
          <div className="drop-zone-text">
            <strong>{file ? file.name : 'Select or drop an official pandas HTML page'}</strong>
            <span>Accepts .html exported documentation files</span>
          </div>
          <input
            type="file"
            accept=".html,.htm,text/html"
            aria-label="Pandas HTML file"
            disabled={busy}
            onChange={event => {
              setFile(event.target.files[0] || null);
              setPreview(null);
              setError('');
            }}
          />
        </label>

        <label className="form-field-label">
          <span>Official page URL</span>
          <input
            type="url"
            value={url}
            disabled={busy}
            placeholder="https://pandas.pydata.org/docs/..."
            onChange={event => {
              setUrl(event.target.value);
              setPreview(null);
            }}
          />
          <small className="form-field-hint">Optional fallback if the HTML lacks source meta tag</small>
        </label>

        {error && <Notice tone="error">{error}</Notice>}

        {preview && (
          <Notice tone={preview.duplicate ? 'info' : 'success'}>
            <strong>{preview.title}</strong> · {preview.sections} section headings parsed
            {preview.duplicate && <div className="mt-1">This page already exists in the library.</div>}
          </Notice>
        )}

        <div className="modal-actions-bar">
          <button type="button" className="button secondary" onClick={close}>
            Cancel
          </button>
          <button className="button primary" disabled={!file || busy || preview?.duplicate}>
            {busy && <Spinner size={15} />}
            <span>{preview ? 'Confirm & Import' : 'Analyze HTML'}</span>
          </button>
        </div>
      </form>
    </Modal>
  );
}

export function Library({ workspace, refresh, navigate }) {
  const [scope, setScope] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const [modal, setModal] = useState('');
  const [action, setAction] = useState('');
  const [feedback, setFeedback] = useState(null);

  const ready = workspace.documents.filter(doc => doc.ready).length;
  const pending = workspace.documents.length - ready;
  const active = workspace.libraries.find(library => library.id === workspace.active);
  const hasJob = ACTIVE.has(workspace.job?.state);
  const query = search.trim().toLowerCase();

  const docs = workspace.documents.filter(
    doc => (!scope || doc.scope === scope) && (doc.title + ' ' + doc.id).toLowerCase().includes(query)
  );
  const shown = docs.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const totalPages = Math.ceil(docs.length / PAGE_SIZE);

  async function run(path, data, after) {
    setFeedback(null);
    setAction(path);
    try {
      const result = await request(path, { method: 'POST', data });
      if (result.message) setFeedback({ message: result.message });
      after?.();
      await refresh();
    } catch (error) {
      setFeedback({ message: error.message, error: true });
    } finally {
      setAction('');
    }
  }

  // Options for custom collection select
  const collectionOptions = [
    { value: '', label: 'All collections' },
    ...[...new Set(workspace.documents.map(doc => doc.scope))].map(item => ({
      value: item,
      label: SCOPES[item] || item,
    })),
  ];

  return (
    <div className="page library-page">
      <header className="page-heading">
        <div className="page-title-group">
          <h1>Document Library</h1>
          <p className="page-subtext">Manage crawled pandas documentation and active vector indexes.</p>
        </div>
        <div className="inline-actions">
          <button className="button secondary" type="button" onClick={() => setModal('manage')}>
            <FolderOpen size={16} />
            <span>Manage Libraries</span>
          </button>
          <button className="button primary" type="button" onClick={() => setModal('import')}>
            <Plus size={16} />
            <span>Import HTML</span>
          </button>
        </div>
      </header>

      {/* Bento Summary Card */}
      <section className="panel library-summary-card">
        <div className="library-hero-icon">
          <Database size={24} className="text-accent" />
        </div>
        <div className="library-hero-info">
          <h2>{active?.name || 'No library activated'}</h2>
          <div className="library-meta-tags">
            <span className="meta-tag">
              <strong>{ready}</strong> / {workspace.documents.length} docs searchable
            </span>
            {workspace.dimensions && (
              <span className="meta-tag">
                <strong>{workspace.dimensions.toLocaleString()}</strong> dimensions
              </span>
            )}
            {pending > 0 && <span className="meta-tag warning">{pending} pending vectorization</span>}
          </div>
        </div>
        <div className="library-hero-actions">
          {pending > 0 && !hasJob ? (
            <button
              className="button primary"
              type="button"
              disabled={!workspace.embedding_ready || Boolean(action)}
              onClick={() => run('/index/update')}
            >
              <RefreshCw size={15} />
              <span>Update Index</span>
            </button>
          ) : (
            <Status ready={!pending}>{hasJob ? 'Building...' : 'Ready & Synced'}</Status>
          )}
        </div>
      </section>

      {workspace.problem && <Notice tone="error">{workspace.problem}</Notice>}
      {!workspace.embedding_ready && (
        <Notice tone="info">
          Set up an embedding connection in Settings to vectorize or verify the preset.{' '}
          <a href="/settings" onClick={event => navigate('/settings', event)}>
            Open Settings <ArrowUpRight size={13} />
          </a>
        </Notice>
      )}
      {workspace.embedding_ready && !active && workspace.preset && (
        <Notice tone="info">
          <span>{workspace.preset.pages} prebuilt indexed documents are ready to load.</span>
          <button type="button" className="text-button font-bold ml-2" onClick={() => setModal('manage')}>
            Load preset library
          </button>
        </Notice>
      )}
      {feedback && !modal && (
        <Notice tone={feedback.error ? 'error' : 'success'}>{feedback.message}</Notice>
      )}

      {/* Ongoing Job Progress Panel */}
      {hasJob && (
        <section className="panel job-progress-card">
          <div className="job-card-header">
            <div>
              <h3>{PHASES[workspace.job.stage] || 'Indexing in progress'}</h3>
              <p className="job-status-desc">
                {workspace.job.state === 'paused'
                  ? 'Paused · State preserved'
                  : workspace.job.state === 'pausing'
                  ? 'Pausing after current batch finishes...'
                  : workspace.job.state === 'stopping'
                  ? 'Stopping after current batch...'
                  : workspace.job.total
                  ? `Completed ${workspace.job.done.toLocaleString()} of ${workspace.job.total.toLocaleString()} batches`
                  : 'Initializing pipeline…'}
              </p>
            </div>
            <div className="inline-actions">
              {['paused', 'pausing'].includes(workspace.job.state) ? (
                <button
                  className="button secondary sm"
                  type="button"
                  disabled={Boolean(action)}
                  onClick={() => run('/index/resume')}
                >
                  <Play size={14} />
                  <span>Resume</span>
                </button>
              ) : (
                <button
                  className="button secondary sm"
                  type="button"
                  disabled={
                    Boolean(action) ||
                    workspace.job.state !== 'running' ||
                    workspace.job.stage === 'publish'
                  }
                  onClick={() => run('/index/pause')}
                >
                  <Pause size={14} />
                  <span>Pause</span>
                </button>
              )}
              <button
                className="button quiet sm"
                type="button"
                disabled={
                  Boolean(action) ||
                  workspace.job.state === 'stopping' ||
                  workspace.job.stage === 'publish'
                }
                onClick={() => run('/index/stop')}
              >
                <Square size={14} />
                <span>Stop</span>
              </button>
            </div>
          </div>

          <ProgressBar
            value={workspace.job.stage === 'publish' ? 100 : workspace.job.done}
            max={workspace.job.stage === 'publish' ? 100 : workspace.job.total || 1}
            label="Indexing progress"
          />
        </section>
      )}

      {workspace.job?.state === 'failed' && (
        <Notice tone="error">
          {workspace.job.error || 'Index update failed.'} Processed batches were preserved for retry.
        </Notice>
      )}
      {workspace.job?.state === 'stopped' && (
        <Notice tone="info">Index update stopped. Completed embeddings will be reused on resumption.</Notice>
      )}

      {/* Documents Table */}
      <section className="panel docs-section">
        <div className="table-filter-bar">
          <div className="search-box">
            <Search size={16} className="search-icon" aria-hidden="true" />
            <input
              type="search"
              aria-label="Search documents"
              placeholder="Search by page title or identifier..."
              value={search}
              onChange={event => {
                setSearch(event.target.value);
                setPage(0);
              }}
            />
            {search && (
              <button
                type="button"
                className="search-clear-btn"
                aria-label="Clear search"
                onClick={() => setSearch('')}
              >
                <X size={14} />
              </button>
            )}
          </div>

          <div className="table-scope-select">
            <CustomSelect
              value={scope}
              options={collectionOptions}
              onChange={val => {
                setScope(val);
                setPage(0);
              }}
              ariaLabel="Document collection filter"
            />
          </div>
        </div>

        {shown.length ? (
          <div className="table-responsive">
            <table className="modern-table">
              <thead>
                <tr>
                  <th scope="col" style={{ width: '45%' }}>Document Title</th>
                  <th scope="col">Collection</th>
                  {pending > 0 && <th scope="col">Status</th>}
                  <th scope="col" className="text-right">Reference</th>
                </tr>
              </thead>
              <tbody>
                {shown.map(doc => (
                  <tr key={doc.id}>
                    <td>
                      <div className="doc-cell">
                        <FileCode size={15} className="doc-icon text-muted" />
                        <span className="doc-title">{doc.title}</span>
                      </div>
                    </td>
                    <td>
                      <span className="collection-pill">{SCOPES[doc.scope] || doc.scope}</span>
                    </td>
                    {pending > 0 && (
                      <td>
                        <span className={'doc-status-badge ' + (doc.ready ? 'ready' : 'pending')}>
                          {doc.ready ? 'Indexed' : 'Pending'}
                        </span>
                      </td>
                    )}
                    <td className="text-right">
                      <a
                        href={doc.url}
                        target="_blank"
                        rel="noreferrer"
                        className="official-docs-link"
                        aria-label={'Official pandas documentation for ' + doc.title}
                      >
                        <span>Official Docs</span>
                        <ArrowUpRight size={13} />
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="table-empty-state">
            <Search size={28} className="empty-icon" />
            <p>No documents match your query.</p>
          </div>
        )}

        <footer className="table-pagination-footer">
          <span className="pagination-count">
            {docs.length
              ? `${page * PAGE_SIZE + 1}–${Math.min((page + 1) * PAGE_SIZE, docs.length)} of ${docs.length} documents`
              : '0 documents'}
          </span>
          {totalPages > 1 && (
            <div className="pagination-nav">
              <button
                type="button"
                className="icon-button"
                aria-label="Previous page"
                disabled={page === 0}
                onClick={() => setPage(p => p - 1)}
              >
                <ChevronLeft size={16} />
              </button>
              <span className="pagination-page-indicator">
                {page + 1} / {totalPages}
              </span>
              <button
                type="button"
                className="icon-button"
                aria-label="Next page"
                disabled={page + 1 >= totalPages}
                onClick={() => setPage(p => p + 1)}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </footer>
      </section>

      {/* Modals */}
      {modal === 'manage' && (
        <ManageLibraries
          workspace={workspace}
          action={action}
          feedback={feedback}
          close={() => setModal('')}
          navigate={navigate}
          run={(path, data, closeFn) => run(path, data, closeFn)}
        />
      )}
      {modal === 'import' && (
        <ImportDocument
          close={() => setModal('')}
          onImported={message => {
            setModal('');
            setFeedback({ message });
            refresh();
          }}
        />
      )}
    </div>
  );
}
