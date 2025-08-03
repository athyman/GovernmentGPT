'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeftIcon, CalendarIcon, UserIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { getDocument } from '@/lib/api';
import { formatDate, getDocumentTypeColor, getStatusColor } from '@/lib/utils';

export default function LegislationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const identifier = params.identifier as string;

  const { data: document, isLoading, error } = useQuery({
    queryKey: ['document', identifier],
    queryFn: () => getDocument(identifier),
    enabled: !!identifier,
  });

  const handleBackClick = () => {
    router.back();
  };

  if (isLoading) {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <LoadingSpinner size="lg" />
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Document Not Found</h1>
            <p className="text-gray-600 mb-6">
              The legislation document you're looking for could not be found.
            </p>
            <Button onClick={handleBackClick}>
              <ArrowLeftIcon className="mr-2 h-4 w-4" />
              Go Back
            </Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const sponsorDisplay = document.sponsor 
    ? `${document.sponsor.full_name} (${document.sponsor.party}-${document.sponsor.state})`
    : null;

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      
      <main className="flex-1">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Back button */}
          <div className="mb-6">
            <Button 
              variant="ghost" 
              onClick={handleBackClick}
              className="text-gray-600 hover:text-gray-900"
            >
              <ArrowLeftIcon className="mr-2 h-4 w-4" />
              Back to Search
            </Button>
          </div>

          {/* Document header */}
          <div className="mb-8">
            <div className="flex flex-wrap gap-2 mb-4">
              <Badge className={getDocumentTypeColor(document.document_type)}>
                {document.document_type === 'bill' ? 'Bill' : 'Executive Order'}
              </Badge>
              <Badge variant="outline" className="font-mono">
                {document.identifier}
              </Badge>
              {document.status && (
                <Badge className={getStatusColor(document.status)}>
                  {document.status}
                </Badge>
              )}
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              {document.title}
            </h1>
            
            <div className="flex flex-wrap gap-6 text-sm text-gray-500">
              {document.introduced_date && (
                <div className="flex items-center gap-1">
                  <CalendarIcon className="h-4 w-4" />
                  <span>Introduced: {formatDate(document.introduced_date)}</span>
                </div>
              )}
              
              {document.last_action_date && (
                <div className="flex items-center gap-1">
                  <CalendarIcon className="h-4 w-4" />
                  <span>Last Action: {formatDate(document.last_action_date)}</span>
                </div>
              )}
              
              {sponsorDisplay && (
                <div className="flex items-center gap-1">
                  <UserIcon className="h-4 w-4" />
                  <span>Sponsored by: {sponsorDisplay}</span>
                </div>
              )}
            </div>
          </div>

          {/* Document content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Summary */}
              {document.summary && (
                <Card>
                  <CardHeader>
                    <h2 className="text-xl font-semibold text-gray-900">Summary</h2>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700 leading-relaxed">
                      {document.summary}
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Full text */}
              <Card>
                <CardHeader>
                  <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                    <DocumentTextIcon className="h-5 w-5" />
                    Full Text
                  </h2>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none">
                    <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700 leading-relaxed">
                      {document.full_text}
                    </pre>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Document details */}
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold text-gray-900">Document Details</h3>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <span className="font-medium text-gray-700">Type:</span>
                    <span className="ml-2 text-gray-600 capitalize">
                      {document.document_type.replace('_', ' ')}
                    </span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Identifier:</span>
                    <span className="ml-2 text-gray-600 font-mono">
                      {document.identifier}
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
                  
                  <div>
                    <span className="font-medium text-gray-700">Created:</span>
                    <span className="ml-2 text-gray-600">
                      {formatDate(document.created_at)}
                    </span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Updated:</span>
                    <span className="ml-2 text-gray-600">
                      {formatDate(document.updated_at)}
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* Sponsor information */}
              {document.sponsor && (
                <Card>
                  <CardHeader>
                    <h3 className="text-lg font-semibold text-gray-900">Sponsor</h3>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <span className="font-medium text-gray-700">Name:</span>
                      <span className="ml-2 text-gray-600">
                        {document.sponsor.full_name}
                      </span>
                    </div>
                    
                    {document.sponsor.party && (
                      <div>
                        <span className="font-medium text-gray-700">Party:</span>
                        <span className="ml-2 text-gray-600">
                          {document.sponsor.party}
                        </span>
                      </div>
                    )}
                    
                    {document.sponsor.state && (
                      <div>
                        <span className="font-medium text-gray-700">State:</span>
                        <span className="ml-2 text-gray-600">
                          {document.sponsor.state}
                        </span>
                      </div>
                    )}
                    
                    <div>
                      <span className="font-medium text-gray-700">Chamber:</span>
                      <span className="ml-2 text-gray-600 capitalize">
                        {document.sponsor.chamber}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Metadata */}
              {document.metadata && Object.keys(document.metadata).length > 0 && (
                <Card>
                  <CardHeader>
                    <h3 className="text-lg font-semibold text-gray-900">Additional Information</h3>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      {Object.entries(document.metadata).map(([key, value]) => (
                        <div key={key}>
                          <span className="font-medium text-gray-700 capitalize">
                            {key.replace('_', ' ')}:
                          </span>
                          <span className="ml-2 text-gray-600">
                            {typeof value === 'string' ? value : JSON.stringify(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}