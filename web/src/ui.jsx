import { useEffect, useId, useRef, useState } from 'react';
import { AlertCircle, Check, ChevronDown, Copy, LoaderCircle, Sparkles, X } from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-json';

export const STRATEGIES = {
  structure_aware: 'Structure-aware',
  fixed_size: 'Fixed window',
};

export const ACTIVE = new Set(['running', 'pausing', 'paused', 'stopping']);

export async function request(path, { method = 'GET', data } = {}) {
  const form = data instanceof FormData;
  const response = await fetch('/api' + path, {
    method,
    headers: data && !form ? { 'Content-Type': 'application/json' } : undefined,
    body: form ? data : data ? JSON.stringify(data) : undefined,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = Array.isArray(payload.detail)
      ? payload.detail.map(item => item.msg).join(' ')
      : payload.detail;
    throw new Error(message || 'The app could not complete that request. Try again.');
  }
  return payload;
}

export function Notice({ children, tone = 'info' }) {
  const Icon = tone === 'success' ? Check : tone === 'error' ? AlertCircle : Sparkles;
  return (
    <div className={'notice ' + tone} role={tone === 'error' ? 'alert' : 'status'}>
      <Icon size={16} className="notice-icon" aria-hidden="true" />
      <div className="notice-content">{children}</div>
    </div>
  );
}

export function Spinner({ size = 16, className = '' }) {
  return <LoaderCircle className={'spin ' + className} size={size} aria-hidden="true" />;
}

export function Status({ ready, children }) {
  return (
    <span className={'status' + (ready ? ' ready' : '')}>
      <span className="status-dot" aria-hidden="true" />
      <span>{children}</span>
    </span>
  );
}

export function CustomSelect({ value, options, onChange, label, ariaLabel, className = '' }) {
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const containerRef = useRef(null);
  const listId = useId();
  const selectedIndex = options.findIndex(option => String(option.value) === String(value));
  const selectedOption = options[Math.max(0, selectedIndex)];
  const activeId = open && options[activeIndex] ? `${listId}-${activeIndex}` : undefined;

  useEffect(() => {
    if (!open) return;
    function handleClickOutside(event) {
      if (!containerRef.current?.contains(event.target)) setOpen(false);
    }
    document.addEventListener('pointerdown', handleClickOutside);
    return () => document.removeEventListener('pointerdown', handleClickOutside);
  }, [open]);

  useEffect(() => {
    if (activeId) document.getElementById(activeId)?.scrollIntoView({ block: 'nearest' });
  }, [activeId]);

  function showOptions() {
    setActiveIndex(Math.max(0, selectedIndex));
    setOpen(true);
  }

  function selectOption(option) {
    onChange(option.value);
    setOpen(false);
  }

  function handleKeyDown(event) {
    if (!open && ['ArrowDown', 'ArrowUp'].includes(event.key)) {
      event.preventDefault();
      showOptions();
      return;
    }
    if (!open) return;

    switch (event.key) {
      case 'ArrowDown':
        setActiveIndex(index => Math.min(index + 1, options.length - 1));
        break;
      case 'ArrowUp':
        setActiveIndex(index => Math.max(index - 1, 0));
        break;
      case 'Home':
        setActiveIndex(0);
        break;
      case 'End':
        setActiveIndex(options.length - 1);
        break;
      case 'Enter':
      case ' ':
        if (options[activeIndex]) selectOption(options[activeIndex]);
        break;
      case 'Escape':
        event.stopPropagation();
        setOpen(false);
        break;
      default:
        return;
    }
    event.preventDefault();
  }

  return (
    <div
      className={'custom-select-wrap ' + className}
      ref={containerRef}
      onBlur={event => {
        if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
      }}
    >
      {label && <span className="custom-select-label">{label}</span>}
      <button
        type="button"
        role="combobox"
        className={'custom-select-trigger' + (open ? ' active' : '')}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={ariaLabel || label}
        aria-controls={open ? listId : undefined}
        aria-activedescendant={activeId}
        disabled={!options.length}
        onClick={open ? () => setOpen(false) : showOptions}
        onKeyDown={handleKeyDown}
      >
        <span className="custom-select-text">{selectedOption ? selectedOption.label : 'Select...'}</span>
        <ChevronDown size={14} className={'custom-select-arrow' + (open ? ' rotated' : '')} aria-hidden="true" />
      </button>

      {open && (
        <ul id={listId} className="custom-select-menu" role="listbox" aria-label={ariaLabel || label}>
          {options.map((option, index) => {
            const isSelected = index === selectedIndex;
            const isActive = index === activeIndex;
            return (
              <li
                key={option.value}
                id={`${listId}-${index}`}
                role="option"
                aria-selected={isSelected}
                className={'custom-select-option' + (isSelected ? ' selected' : '') + (isActive ? ' active' : '')}
                onMouseDown={event => event.preventDefault()}
                onClick={() => selectOption(option)}
              >
                <span>{option.label}</span>
                {isSelected && <Check size={14} className="option-check" aria-hidden="true" />}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

/**
 * Custom Collapsible / Accordion - Replaces native <details><summary>
 */
export function Collapsible({ title, defaultOpen = false, children, extra, className = '' }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={'collapsible-panel ' + className + (open ? ' is-open' : '')}>
      <div className="collapsible-heading">
        <button type="button" className="collapsible-header" aria-expanded={open}
          onClick={() => setOpen(prev => !prev)}>
          <span className="collapsible-title">
            <ChevronDown size={15} className={'collapsible-chevron' + (open ? ' rotated' : '')} aria-hidden="true" />
            <span>{title}</span>
          </span>
        </button>
        {extra && <div className="collapsible-extra">{extra}</div>}
      </div>
      {open && <div className="collapsible-content">{children}</div>}
    </div>
  );
}

export function Modal({ title, close, children }) {
  const modalRef = useRef(null);

  useEffect(() => {
    const modal = modalRef.current;
    const trigger = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    modal.showModal();
    document.body.style.overflow = 'hidden';
    return () => {
      if (modal.open) modal.close();
      document.body.style.overflow = previousOverflow;
      if (trigger instanceof HTMLElement && trigger.isConnected) trigger.focus();
    };
  }, []);

  return (
    <dialog className="modal-container" ref={modalRef} aria-label={title}
      onCancel={event => { event.preventDefault(); close(); }}
      onClick={event => {
        if (event.target !== event.currentTarget) return;
        const { left, right, top, bottom } = event.currentTarget.getBoundingClientRect();
        if (event.clientX < left || event.clientX > right || event.clientY < top || event.clientY > bottom) close();
      }}>
      <header className="modal-header">
        <h2>{title}</h2>
        <button type="button" className="icon-button modal-close" onClick={close} aria-label="Close dialog">
          <X size={18} />
        </button>
      </header>
      <div className="modal-body">{children}</div>
    </dialog>
  );
}

/**
 * Custom Modern Progress Bar - Replaces native <progress>
 */
export function ProgressBar({ value, max = 100, label, showPercent = true }) {
  const percentage = max > 0 ? Math.min(100, Math.max(0, Math.round((value / max) * 100))) : 0;
  return (
    <div className="progress-wrap" role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={max} aria-label={label}>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${percentage}%` }}>
          <div className="progress-shimmer" />
        </div>
      </div>
      {showPercent && <span className="progress-text">{percentage}%</span>}
    </div>
  );
}

/**
 * Code Block with Prism Syntax Highlighting and Copy Button
 */
export function CodeBlock({ code, language = 'python' }) {
  const [copied, setCopied] = useState(false);
  const codeRef = useRef(null);

  useEffect(() => {
    if (codeRef.current) {
      Prism.highlightElement(codeRef.current);
    }
  }, [code, language]);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="code-block-container">
      <div className="code-block-header">
        <span className="code-block-lang">{language}</span>
        <button
          type="button"
          className="code-copy-btn"
          onClick={handleCopy}
          aria-label={copied ? 'Copied' : 'Copy code'}
        >
          {copied ? (
            <>
              <Check size={13} className="text-emerald" />
              <span>Copied</span>
            </>
          ) : (
            <>
              <Copy size={13} />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      <pre className="code-block-pre">
        <code ref={codeRef} className={`language-${language}`}>
          {code}
        </code>
      </pre>
    </div>
  );
}

/**
 * Visual Score Bar for Cosine Similarity
 */
export function ScoreBar({ score }) {
  const percent = Math.min(100, Math.max(0, Math.round(score * 100)));
  return (
    <div className="score-badge-wrap" title={`Cosine Similarity: ${score.toFixed(4)}`}>
      <span className="score-number">{score.toFixed(3)}</span>
      <div className="score-mini-track">
        <div className="score-mini-bar" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}
