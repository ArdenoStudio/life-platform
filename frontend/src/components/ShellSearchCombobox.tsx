import { Search } from 'lucide-react'
import { useId, useRef, useState, type KeyboardEvent } from 'react'

import type { SearchResult } from '../types'

export function ShellSearchCombobox({
  label,
  onChange,
  onSelectResult,
  placeholder,
  results,
  value,
}: {
  label: string
  onChange: (value: string) => void
  onSelectResult: (result: SearchResult) => void
  placeholder: string
  results: SearchResult[]
  value: string
}) {
  const listboxId = useId()
  const inputRef = useRef<HTMLInputElement>(null)
  const [activeIndex, setActiveIndex] = useState(-1)
  const items = results.slice(0, 5)
  const open = value.trim().length > 1 && items.length > 0

  function select(index: number) {
    const result = items[index]
    if (!result) return
    onSelectResult(result)
    setActiveIndex(-1)
    inputRef.current?.focus()
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (!open || items.length === 0) return

    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setActiveIndex((current) => (current + 1) % items.length)
      return
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((current) => (current <= 0 ? items.length - 1 : current - 1))
      return
    }
    if (event.key === 'Enter' && activeIndex >= 0) {
      event.preventDefault()
      select(activeIndex)
      return
    }
    if (event.key === 'Escape') {
      event.preventDefault()
      setActiveIndex(-1)
    }
  }

  return (
    <div className="relative min-w-0">
      <label className="pulse-search-field">
        <Search className="pulse-search-field__icon" aria-hidden="true" />
        <input
          ref={inputRef}
          aria-activedescendant={activeIndex >= 0 ? `${listboxId}-option-${activeIndex}` : undefined}
          aria-autocomplete="list"
          aria-controls={open ? listboxId : undefined}
          aria-expanded={open}
          aria-label={label}
          className="pulse-search-field__input"
          onChange={(event) => {
            onChange(event.target.value)
            setActiveIndex(-1)
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          role="combobox"
          type="search"
          value={value}
        />
      </label>
      {open ? (
        <ul aria-label={label} className="pulse-search-listbox" id={listboxId} role="listbox">
          {items.map((result, index) => {
            const active = index === activeIndex
            return (
              <li key={`${result.domain}-${result.label}`} role="presentation">
                <button
                  aria-selected={active}
                  className={`pulse-search-option${active ? ' pulse-search-option--active' : ''}`}
                  id={`${listboxId}-option-${index}`}
                  onMouseDown={(event) => event.preventDefault()}
                  onClick={() => select(index)}
                  role="option"
                  type="button"
                >
                  <span className="block text-sm font-semibold text-foreground">{result.label}</span>
                  <span className="block truncate text-xs text-muted">{result.description}</span>
                </button>
              </li>
            )
          })}
        </ul>
      ) : null}
    </div>
  )
}
