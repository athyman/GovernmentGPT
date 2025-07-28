'use client';

import { useState } from 'react';
import { DocumentTextIcon, ClockIcon, UserIcon } from '@heroicons/react/24/outline';
import { type SearchResponse } from '@/lib/api';
import { DocumentCard } from '@/components/documents/DocumentCard';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { formatRelativeTime } from '@/lib/utils';

interface SearchResultsProps {
  results: SearchResponse;
  onRefineSearch?: (query: string, filters?: any) => void;
}

export function SearchResults({ results, onRefineSearch }: SearchResultsProps) {
  const [showAISummary, setShowAISummary] = useState(true);

  if (results.returned_results === 0) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
        <p className="text-gray-600 mb-4">
          We couldn't find any documents matching your search. Try different keywords or check your spelling.
        </p>
        {results.suggestions && results.suggestions.length > 0 && (
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-2">Did you mean:</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {results.suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => onRefineSearch?.(suggestion)}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            Search Results for "{results.query}"
          </h2>
          <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
            <span>
              {results.total_results.toLocaleString()} documents found
            </span>
            <div className="flex items-center gap-1">
              <ClockIcon className="h-4 w-4" />
              <span>{results.response_time_ms}ms</span>
            </div>
            <Badge variant="outline" className="capitalize">
              {results.search_type} search
            </Badge>
          </div>
        </div>
      </div>

      {/* AI Summary */}
      {results.ai_summary && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-medium text-blue-900">AI Summary</h3>
            <div className="flex items-center gap-2">
              {results.confidence_score && (
                <Badge variant="secondary">
                  {Math.round(results.confidence_score * 100)}% confidence
                </Badge>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAISummary(!showAISummary)}
              >
                {showAISummary ? 'Hide' : 'Show'}
              </Button>
            </div>
          </div>
          
          {showAISummary && (
            <div className="prose prose-blue max-w-none">
              <p className="text-blue-800 leading-relaxed">
                {results.ai_summary}
              </p>
              {results.source_documents && results.source_documents.length > 0 && (
                <div className="mt-4 pt-4 border-t border-blue-200">
                  <p className="text-sm font-medium text-blue-900 mb-2">
                    Based on {results.source_documents.length} source documents
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {results.source_documents.slice(0, 5).map((docId, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {docId}
                      </Badge>
                    ))}
                    {results.source_documents.length > 5 && (
                      <Badge variant="outline" className="text-xs">
                        +{results.source_documents.length - 5} more
                      </Badge>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Document Results */}
      <div className="space-y-4">
        {results.documents.map((document) => (
          <DocumentCard 
            key={document.id} 
            document={document}
            showRelevanceScore={true}
          />
        ))}
      </div>

      {/* Load More (placeholder for pagination) */}
      {results.total_results > results.returned_results && (
        <div className="text-center pt-6">
          <Button variant="outline" size="lg">
            Load More Results
          </Button>
          <p className="text-sm text-gray-600 mt-2">
            Showing {results.returned_results} of {results.total_results.toLocaleString()} results
          </p>
        </div>
      )}

      {/* Search Suggestions */}
      {results.suggestions && results.suggestions.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            Related searches:
          </h4>
          <div className="flex flex-wrap gap-2">
            {results.suggestions.map((suggestion, index) => (
              <Button
                key={index}
                variant="ghost"
                size="sm"
                onClick={() => onRefineSearch?.(suggestion)}
                className="text-sm"
              >
                {suggestion}
              </Button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}