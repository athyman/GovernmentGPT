'use client';

import { type DocumentResult } from '@/lib/api';
import { DocumentCard } from './DocumentCard';

interface DocumentCardsProps {
  documents: DocumentResult[];
  loading?: boolean;
  title?: string;
}

export function DocumentCards({ documents, loading = false, title }: DocumentCardsProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {title && (
          <h2 className="text-2xl font-bold text-gray-900 mb-6">{title}</h2>
        )}
        {/* Loading skeleton */}
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="bg-white border border-gray-200 rounded-lg p-6 animate-pulse">
            <div className="flex gap-2 mb-4">
              <div className="h-6 bg-gray-200 rounded-full w-16"></div>
              <div className="h-6 bg-gray-200 rounded-full w-24"></div>
              <div className="h-6 bg-gray-200 rounded-full w-20"></div>
            </div>
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded w-full"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              <div className="h-4 bg-gray-200 rounded w-4/6"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
            <svg 
              className="w-8 h-8 text-gray-400" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No documents available
          </h3>
          <p className="text-gray-600">
            There are currently no documents to display. Check back later for updates.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {title && (
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
      )}
      
      <div className="space-y-4">
        {documents.map((document) => (
          <DocumentCard 
            key={document.id} 
            document={document}
          />
        ))}
      </div>
      
      {documents.length >= 10 && (
        <div className="text-center pt-6">
          <p className="text-sm text-gray-600">
            Showing {documents.length} documents
          </p>
        </div>
      )}
    </div>
  );
}