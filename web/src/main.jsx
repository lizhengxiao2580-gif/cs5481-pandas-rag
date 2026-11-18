import React, { useCallback, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  BookOpen,
  Braces,
  Database,
  Moon,
  Search,
  Settings2,
  Sun,
} from 'lucide-react';
import '@fontsource-variable/inter/wght.css';
import './style.css';
import { Ask } from './ask.jsx';
import { Library } from './library.jsx';
import { Settings } from './settings.jsx';
import { ACTIVE, Notice, Spinner, Status, request } from './ui.jsx';

const PAGES = [
  { path: '/', label: 'Ask & Compare', icon: Search },
  { path: '/library', label: 'Library', icon: Database },
  { path: '/settings', label: 'Settings', icon: Settings2 },
];

function App() {
  const [route, setRoute] = useState(window.location.pathname);
  const [workspace, setWorkspace] = useState(null);
  const [problem, setProblem] = useState('');
  const [askState, setAskState] = useState({ question: '', mode: 'answer', strategy: '', run: null });

  // Dark / Light Theme management
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('pandas_docs_theme') || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('pandas_docs_theme', theme);
  }, [theme]);

  function toggleTheme() {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  }

  const refresh = useCallback(async () => {
    try {
      const data = await request('/workspace');
      setWorkspace(data);
      setProblem('');
      return data;
    } catch (error) {
      setProblem(error.message);
      return null;
    }
  }, []);

  useEffect(() => {
    refresh();
    const handlePop = () => setRoute(window.location.pathname);
    window.addEventListener('popstate', handlePop);
    return () => window.removeEventListener('popstate', handlePop);
  }, [refresh]);

  useEffect(() => {
    if (!ACTIVE.has(workspace?.job?.state)) return;
    const task = window.setInterval(refresh, 1300);
    return () => window.clearInterval(task);
  }, [workspace?.job?.state, refresh]);

  function navigate(path, event) {
    if (event) {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
    }
    if (path === route) return;
    window.history.pushState({}, '', path);
    setRoute(path);
    window.scrollTo(0, 0);
    refresh();
  }

  const ready = workspace?.documents.filter(doc => doc.ready).length || 0;
  const previousContext = askState.run?.context;
  const context = workspace
    ? workspace.active + ':' + workspace.documents.filter(doc => doc.ready).map(doc => doc.id).join(',')
    : '';
  const ask = previousContext && previousContext !== context ? { ...askState, run: null } : askState;

  return (
    <>
      <a className="skip-link" href="#main">
        Skip to main content
      </a>

      {/* Sticky Glassmorphic Header */}
      <header className="site-header">
        <div className="site-frame">
          <a className="brand-logo" href="/" onClick={event => navigate('/', event)}>
            <div className="brand-icon-box">
              <Braces size={18} strokeWidth={2.4} aria-hidden="true" />
            </div>
            <div className="brand-text-col">
              <span className="brand-title">pandas <strong>Docs QA</strong></span>
              <span className="brand-badge">CS5481</span>
            </div>
          </a>

          <nav className="site-nav" aria-label="Main navigation">
            {PAGES.map(({ path, label, icon: Icon }) => {
              const isCurrent = route === path;
              return (
                <a
                  key={path}
                  href={path}
                  className={'nav-item' + (isCurrent ? ' active' : '')}
                  aria-current={isCurrent ? 'page' : undefined}
                  onClick={event => navigate(path, event)}
                >
                  <Icon size={15} aria-hidden="true" />
                  <span>{label}</span>
                </a>
              );
            })}
          </nav>

          <div className="header-right-tools">
            <a
              className="header-library-status"
              href="/library"
              onClick={event => navigate('/library', event)}
              title={ready ? `${ready} docs searchable` : 'Open Library'}
            >
              <Status ready={Boolean(ready)}>
                {ready ? `${ready} Docs Indexed` : 'Unindexed Library'}
              </Status>
            </a>

            <button
              type="button"
              className="icon-button theme-toggle-btn"
              onClick={toggleTheme}
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Viewport */}
      <main id="main" className="site-main">
        {problem && (
          <Notice tone="error">
            <span>{problem}</span>
            <button type="button" className="text-button underline ml-2" onClick={refresh}>
              Retry connection
            </button>
          </Notice>
        )}

        {!workspace && !problem && (
          <div className="loading-fullscreen">
            <Spinner size={24} />
            <p>Initializing pandas documentation workspace…</p>
          </div>
        )}

        {workspace && route === '/' && (
          <Ask
            workspace={workspace}
            context={context}
            state={ask}
            setState={setAskState}
            navigate={navigate}
          />
        )}
        {workspace && route === '/library' && (
          <Library workspace={workspace} refresh={refresh} navigate={navigate} />
        )}
        {workspace && route === '/settings' && (
          <Settings
            workspace={workspace}
            refresh={refresh}
            onSaved={() => setAskState(previous => ({ ...previous, run: null }))}
          />
        )}
      </main>

      {/* Minimal Footer */}
      <footer className="site-footer">
        <div className="footer-content">
          <BookOpen size={14} aria-hidden="true" />
          <span>pandas 3.1.1 Documentation · RAG Retrieval Evaluation System</span>
        </div>
      </footer>
    </>
  );
}

createRoot(document.getElementById('root')).render(<App />);
