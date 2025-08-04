'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  ChatBubbleLeftRightIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';

interface ClaudeResponseProps {
  query: string;
  response: string;
  confidence: number;
  suggestions: string[];
  responseTime: number;
  onSuggestionClick?: (suggestion: string) => void;
}

export function ClaudeResponse({ 
  query, 
  response, 
  confidence, 
  suggestions, 
  responseTime,
  onSuggestionClick 
}: ClaudeResponseProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-orange-600 bg-orange-50 border-orange-200';
  };

  const getConfidenceIcon = (score: number) => {
    if (score >= 0.8) return <CheckCircleIcon className="h-4 w-4" />;
    if (score >= 0.6) return <ExclamationTriangleIcon className="h-4 w-4" />;
    return <ExclamationTriangleIcon className="h-4 w-4" />;
  };

  const getConfidenceText = (score: number) => {
    if (score >= 0.8) return 'High Confidence';
    if (score >= 0.6) return 'Medium Confidence';
    return 'Low Confidence';
  };

  // Process response text to make bill references clickable
  const processResponseText = (text: string) => {
    // Look for bill/EO patterns like HR-1234, S-567, EO-14001
    const billPattern = /\b(HR|S|EO)-\d+(-\d+)?\b/g;
    
    const parts = text.split(billPattern);
    const elements = [];
    
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      
      if (part && part.match(/^(HR|S|EO)-\d+(-\d+)?$/)) {
        // This is a bill reference
        elements.push(
          <a
            key={i}
            href={`/legislation/${part}`}
            className="text-blue-600 hover:text-blue-800 underline font-medium"
            target="_blank"
            rel="noopener noreferrer"
          >
            {part}
          </a>
        );
      } else if (part) {
        // Regular text
        elements.push(part);
      }
    }
    
    return elements;
  };

  return (
    <Card className="mb-6 border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <ChatBubbleLeftRightIcon className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                AI Analysis
              </h3>
              <p className="text-sm text-gray-600">
                Response to: "{query}"
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Confidence indicator */}
            <div className={`flex items-center gap-1 px-2 py-1 rounded-md border text-xs font-medium ${getConfidenceColor(confidence)}`}>
              {getConfidenceIcon(confidence)}
              <span>{getConfidenceText(confidence)}</span>
            </div>
            
            {/* Response time */}
            <div className="text-xs text-gray-500">
              {responseTime}ms
            </div>
            
            {/* Expand/collapse button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-gray-600 hover:text-gray-900"
            >
              {isExpanded ? (
                <ChevronUpIcon className="h-4 w-4" />
              ) : (
                <ChevronDownIcon className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </CardHeader>
      
      {isExpanded && (
        <CardContent className="pt-0">
          {/* AI Response */}
          <div className="mb-6">
            <div className="prose prose-blue max-w-none">
              <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                {processResponseText(response)}
              </div>
            </div>
          </div>
          
          {/* Suggestions */}
          {suggestions && suggestions.length > 0 && (
            <div className="border-t border-gray-200 pt-4">
              <div className="flex items-center gap-2 mb-3">
                <LightBulbIcon className="h-4 w-4 text-yellow-500" />
                <span className="text-sm font-medium text-gray-700">
                  Related searches you might try:
                </span>
              </div>
              
              <div className="flex flex-wrap gap-2">
                {suggestions.slice(0, 5).map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => onSuggestionClick?.(suggestion)}
                    className="text-xs hover:bg-blue-50 hover:border-blue-300"
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>
          )}
          
          {/* Disclaimer */}
          <div className="mt-4 p-3 bg-gray-50 rounded-lg border">
            <p className="text-xs text-gray-600">
              <strong>Note:</strong> This response is generated by AI and provides a summary of available government documents. 
              Always refer to official sources for legal or professional purposes. 
              Click on document identifiers above to view official details.
            </p>
          </div>
        </CardContent>
      )}
    </Card>
  );
}