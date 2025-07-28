'use client';

import { useState } from 'react';
import { ChevronDownIcon, ChevronUpIcon, DocumentTextIcon, UserIcon, CalendarIcon } from '@heroicons/react/24/outline';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { type DocumentResult } from '@/lib/api';
import { formatDate, getDocumentTypeColor, getStatusColor, truncateText } from '@/lib/utils';
import Link from 'next/link';

interface DocumentCardProps {
  document: DocumentResult;
  showRelevanceScore?: boolean;
}

export function DocumentCard({ document, showRelevanceScore = false }: DocumentCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const sponsorDisplay = document.sponsor_name 
    ? `${document.sponsor_name} (${document.sponsor_party}-${document.sponsor_state})`
    : null;

  return (
    <Card className="hover:shadow-md transition-shadow duration-200">
      <CardHeader className="pb-3">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            <Badge className={getDocumentTypeColor(document.document_type)}>
              {document.document_type === 'bill' ? 'Bill' : 'Executive Order'}
            </Badge>
            <Badge variant="outline">{document.identifier}</Badge>
            {document.status && (
              <Badge className={getStatusColor(document.status)}>
                {document.status}
              </Badge>
            )}
            {showRelevanceScore && document.relevance_score && (
              <Badge variant="secondary">
                {Math.round(document.relevance_score * 100)}% match
              </Badge>
            )}
          </div>
          
          <div className="flex items-center gap-2 text-sm text-gray-500">
            {document.introduced_date && (
              <div className="flex items-center gap-1">
                <CalendarIcon className="h-4 w-4" />
                <span>{formatDate(document.introduced_date)}</span>
              </div>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          <Link 
            href={`/legislation/${document.identifier}`}
            className="hover:text-primary transition-colors"
          >
            {document.title}
          </Link>
        </h3>
        
        {/* Summary or highlight snippet */}
        <div className="text-gray-600 mb-4">
          {document.highlight_snippet ? (
            <p 
              className="line-clamp-3"
              dangerouslySetInnerHTML={{ __html: document.highlight_snippet }}
            />
          ) : document.summary ? (
            <p className="line-clamp-3">
              {truncateText(document.summary, 300)}
            </p>
          ) : (
            <p className="italic text-gray-500">No summary available</p>
          )}
        </div>
        
        {/* Sponsor information */}
        {sponsorDisplay && (
          <div className="flex items-center gap-1 text-sm text-gray-500 mb-3">
            <UserIcon className="h-4 w-4" />
            <span>Sponsored by: {sponsorDisplay}</span>
          </div>
        )}
        
        {/* Action buttons */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-600 hover:text-gray-900"
          >
            {isExpanded ? (
              <>
                <span>Show Less</span>
                <ChevronUpIcon className="ml-1 h-4 w-4" />
              </>
            ) : (
              <>
                <span>Show More</span>
                <ChevronDownIcon className="ml-1 h-4 w-4" />
              </>
            )}
          </Button>
          
          <Link
            href={`/legislation/${document.identifier}`}
            className="text-primary hover:text-primary/80 text-sm font-medium flex items-center gap-1"
          >
            <DocumentTextIcon className="h-4 w-4" />
            <span>Full Details</span>
          </Link>
        </div>
        
        {/* Expanded content */}
        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-gray-200 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700">Document Type:</span>
                <span className="ml-2 text-gray-600 capitalize">
                  {document.document_type.replace('_', ' ')}
                </span>
              </div>
              
              {document.status && (
                <div>
                  <span className="font-medium text-gray-700">Status:</span>
                  <span className="ml-2 text-gray-600 capitalize">
                    {document.status.replace('_', ' ')}
                  </span>
                </div>
              )}
              
              {document.last_action_date && (
                <div>
                  <span className="font-medium text-gray-700">Last Action:</span>
                  <span className="ml-2 text-gray-600">
                    {formatDate(document.last_action_date)}
                  </span>
                </div>
              )}
              
              {document.document_type === 'bill' && document.sponsor_state && (
                <div>
                  <span className="font-medium text-gray-700">State:</span>
                  <span className="ml-2 text-gray-600">{document.sponsor_state}</span>
                </div>
              )}
            </div>
            
            {/* Full summary if available */}
            {document.summary && !document.highlight_snippet && (
              <div className="mt-4">
                <span className="font-medium text-gray-700">Summary:</span>
                <p className="mt-1 text-gray-600 leading-relaxed">
                  {document.summary}
                </p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}