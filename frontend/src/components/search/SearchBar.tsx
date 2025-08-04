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
          "relative flex items-center transition-all duration-300 bg-white",
          isFocused ? "ring-2 ring-blue-600 ring-offset-2 shadow-xl" : "shadow-lg hover:shadow-xl",
          "rounded-2xl border-2 border-gray-100 overflow-hidden min-h-[64px]"
        )}>
          {/* Search Icon */}
          <div className="flex items-center justify-center pl-6 pr-4">
            <MagnifyingGlassIcon className={cn(
              "h-6 w-6 transition-colors duration-200",
              isFocused ? "text-blue-600" : "text-gray-500"
            )} />
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
            className="flex-1 border-0 bg-transparent px-0 py-6 text-lg placeholder:text-gray-500 focus-visible:ring-0 focus-visible:ring-offset-0 text-gray-900 font-medium h-auto"
            aria-label="Search query"
          />

          {/* Clear Button */}
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="flex items-center justify-center px-3 text-gray-400 hover:text-gray-600 transition-colors duration-200 h-10 w-10 rounded-full hover:bg-gray-100"
              aria-label="Clear search"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          )}

          {/* Search Button */}
          <div className="flex items-center pr-3">
            <Button 
              type="submit" 
              disabled={!query.trim()}
              size="lg"
              className={cn(
                "h-12 px-8 text-white font-semibold transition-all duration-200 text-base",
                "bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800",
                "disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed",
                "rounded-xl shadow-md hover:shadow-lg disabled:shadow-none",
                "border-0 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              )}
            >
              <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
              Search
            </Button>
          </div>
        </div>

        {/* Search Suggestions (placeholder for future implementation) */}
        {isFocused && query.length > 2 && (
          <div className="absolute top-full left-0 right-0 mt-3 bg-white border border-gray-200 rounded-xl shadow-xl z-50 overflow-hidden">
            <div className="p-4 text-sm text-gray-600 border-b border-gray-100">
              <span className="font-medium text-gray-800">Search suggestions</span>
            </div>
            <div className="p-3">
              <div className="text-sm text-gray-500">
                Advanced search suggestions will appear here based on government document content
              </div>
            </div>
          </div>
        )}
      </form>

      {/* Search Tips */}
      {!initialQuery && (
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600 leading-relaxed">
            Try searching for <span className="font-medium text-blue-600">"climate change"</span>, 
            <span className="font-medium text-blue-600"> "healthcare reform"</span>, or 
            <span className="font-medium text-blue-600">"infrastructure bill"</span>
          </p>
          <p className="text-xs text-gray-500 mt-2">
            Search across thousands of bills, executive orders, and government documents
          </p>
        </div>
      )}
    </div>
  );
}