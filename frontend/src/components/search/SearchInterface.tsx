'use client';

import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { SearchBar } from './SearchBar';
import { SearchResults } from './SearchResults';
import { ClaudeResponse } from './ClaudeResponse';
import { searchDocuments, type SearchRequest, type ConversationalSearchResponse } from '@/lib/api';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

interface SearchInterfaceProps {
  onSearch?: (query: string) => void;
  initialQuery?: string;
  showResults?: boolean;
}

export function SearchInterface({ onSearch, initialQuery = '', showResults = false }: SearchInterfaceProps) {
  const [searchRequest, setSearchRequest] = useState<SearchRequest | null>(
    initialQuery ? {
      query: initialQuery,
      search_type: 'conversational',
      limit: 20,
      offset: 0,
    } : null
  );

  const { data: searchResults, isLoading, error } = useQuery({
    queryKey: ['search', searchRequest],
    queryFn: () => searchDocuments(searchRequest!),
    enabled: !!searchRequest,
    staleTime: 30 * 1000, // 30 seconds
  });

  const handleSearch = useCallback((query: string, filters?: any) => {
    const newSearchRequest: SearchRequest = {
      query,
      search_type: 'conversational',
      filters,
      limit: 20,
      offset: 0,
    };
    
    setSearchRequest(newSearchRequest);
    onSearch?.(query);
  }, [onSearch]);

  const handleSuggestionClick = useCallback((suggestion: string) => {
    handleSearch(suggestion);
  }, [handleSearch]);

  return (
    <div className="w-full">
      {/* Search Bar */}
      <div className="mb-8">
        <SearchBar
          onSearch={handleSearch}
          initialQuery={initialQuery}
          placeholder="What would you like to know about recent government actions?"
          className="max-w-4xl mx-auto"
        />
      </div>

      {/* Search Results */}
      {showResults && searchRequest && (
        <div className="max-w-4xl mx-auto">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner size="lg" />
              <span className="ml-3 text-gray-600">Searching government documents...</span>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <div className="mx-auto w-16 h-16 mb-4 flex items-center justify-center bg-red-50 rounded-full">
                <MagnifyingGlassIcon className="w-8 h-8 text-red-500" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Search Failed</h3>
              <p className="text-gray-600 mb-4">
                We encountered an error while searching. Please try again.
              </p>
              <button
                onClick={() => handleSearch(searchRequest.query, searchRequest.filters)}
                className="text-primary hover:text-primary/80 font-medium"
              >
                Try Again
              </button>
            </div>
          ) : searchResults ? (
            <div className="space-y-6">
              {/* Claude AI Response */}
              {searchResults.claude_response && (
                <ClaudeResponse
                  query={searchResults.query}
                  response={searchResults.claude_response}
                  confidence={searchResults.confidence}
                  suggestions={searchResults.suggestions}
                  responseTime={searchResults.response_time_ms}
                  onSuggestionClick={handleSuggestionClick}
                />
              )}
              
              {/* Search Results */}
              <SearchResults 
                results={searchResults}
                onRefineSearch={handleSearch}
              />
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}