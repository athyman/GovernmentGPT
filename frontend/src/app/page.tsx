'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { SearchInterface } from '@/components/search/SearchInterface';
import { DocumentCards } from '@/components/documents/DocumentCards';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { ErrorBoundary } from '@/components/ui/error-boundary';
import { fetchRecentDocuments } from '@/lib/api';

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [hasSearched, setHasSearched] = useState(false);

  // Fetch recent documents for the landing page
  const { data: recentDocuments, isLoading, error } = useQuery({
    queryKey: ['recent-documents'],
    queryFn: () => fetchRecentDocuments(10),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setHasSearched(true);
  };

  const handleBackToHome = () => {
    setSearchQuery('');
    setHasSearched(false);
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header onBackToHome={handleBackToHome} showBackButton={hasSearched} />
      
      <main className="flex-1">
        <ErrorBoundary>
          {!hasSearched ? (
            // Landing page with recent documents
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              {/* Hero section */}
              <div className="text-center mb-12">
                <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl lg:text-6xl">
                  Understand Your{' '}
                  <span className="text-government-600">Government</span>
                </h1>
                <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
                  Get AI-powered summaries and intelligent search across congressional bills 
                  and executive orders. Making government actions accessible to every citizen.
                </p>
              </div>

              {/* Search interface */}
              <div className="mb-12">
                <SearchInterface onSearch={handleSearch} />
              </div>

              {/* Recent documents */}
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  Recent Government Actions
                </h2>
                
                {isLoading ? (
                  <div className="flex justify-center py-12">
                    <LoadingSpinner size="lg" />
                  </div>
                ) : error ? (
                  <div className="text-center py-12">
                    <p className="text-red-600">
                      Failed to load recent documents. Please try again later.
                    </p>
                  </div>  
                ) : (
                  <DocumentCards documents={recentDocuments || []} />
                )}
              </div>
            </div>
          ) : (
            // Search results view
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <SearchInterface 
                onSearch={handleSearch}
                initialQuery={searchQuery}
                showResults={true}
              />
            </div>
          )}
        </ErrorBoundary>
      </main>

      <Footer />
    </div>
  );
}