'use client';

import { useState, useEffect, useRef } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SearchBarProps {
  onSearch: (query: string, filters?: any) => void;
  initialQuery?: string;
  placeholder?: string;
  className?: string;
}

export function SearchBar({ 
  onSearch, 
  initialQuery = '', 
  placeholder = "Search government documents...",
  className 
}: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      inputRef.current?.blur();
      setIsFocused(false);
    }
  };

  return (
    <div className={cn("w-full", className)}>
      <form onSubmit={handleSubmit} className="relative">
        <div className={cn(
          "relative flex items-center transition-all duration-200",
          isFocused ? "ring-2 ring-primary ring-offset-2" : "",
          "rounded-lg border border-input bg-background shadow-sm"
        )}>
          {/* Search Icon */}
          <div className="pl-4 pr-2">
            <MagnifyingGlassIcon className="h-5 w-5 text-muted-foreground" />
          </div>

          {/* Input Field */}
          <Input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="flex-1 border-0 bg-transparent px-0 py-4 text-lg focus-visible:ring-0 focus-visible:ring-offset-0"
            aria-label="Search query"
          />

          {/* Clear Button */}
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="p-2 text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Clear search"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          )}

          {/* Search Button */}
          <div className="pr-2">
            <Button 
              type="submit" 
              size="sm"
              disabled={!query.trim()}
              className="px-6"
            >
              Search
            </Button>
          </div>
        </div>

        {/* Search Suggestions (placeholder for future implementation) */}
        {isFocused && query.length > 2 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-background border border-input rounded-lg shadow-lg z-50">
            <div className="p-2 text-sm text-muted-foreground">
              Search suggestions will appear here
            </div>
          </div>
        )}
      </form>

      {/* Search Tips */}
      {!initialQuery && (
        <div className="mt-4 text-center">
          <p className="text-sm text-muted-foreground">
            Try searching for "climate change", "healthcare reform", or "infrastructure bill"
          </p>
        </div>
      )}
    </div>
  );
}