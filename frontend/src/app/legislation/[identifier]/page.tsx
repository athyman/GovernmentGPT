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
              {document.metadata?.web_url ? (
                <a 
                  href={document.metadata.web_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-government-600 hover:text-government-700 hover:underline transition-colors"
                >
                  {document.title}
                  <span className="ml-2 text-sm text-gray-500">↗</span>
                </a>
              ) : (
                document.title
              )}
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

              {/* Document Content */}
              <Card>
                <CardHeader>
                  <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                    <DocumentTextIcon className="h-5 w-5" />
                    Legislative Information
                    {document.metadata?.web_url && (
                      <a 
                        href={document.metadata.web_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-auto text-sm text-government-600 hover:text-government-700 font-normal flex items-center gap-1"
                      >
                        View on Congress.gov ↗
                      </a>
                    )}
                  </h2>
                </CardHeader>
                <CardContent>
                  {document.full_text ? (
                    <div className="space-y-4">
                      {/* Check if content is structured or just basic info */}
                      {document.full_text.includes('TITLE:') ? (
                        // Structured content - parse and display nicely
                        <div className="space-y-4">
                          {document.full_text.split('\n\n').map((section, index) => {
                            if (section.startsWith('TITLE:')) {
                              return (
                                <div key={index} className="pb-2 border-b border-gray-200">
                                  <h3 className="font-semibold text-gray-900 mb-2">Official Title</h3>
                                  <p className="text-gray-700 italic">{section.replace('TITLE: ', '')}</p>
                                </div>
                              );
                            } else if (section.startsWith('SPONSOR:')) {
                              return (
                                <div key={index} className="pb-2 border-b border-gray-200">
                                  <h3 className="font-semibold text-gray-900 mb-2">Primary Sponsor</h3>
                                  <p className="text-gray-700">{section.replace('SPONSOR: ', '')}</p>
                                </div>
                              );
                            } else if (section.startsWith('SUMMARY:')) {
                              return (
                                <div key={index} className="pb-2 border-b border-gray-200">
                                  <h3 className="font-semibold text-gray-900 mb-2">Congressional Summary</h3>
                                  <p className="text-gray-700 leading-relaxed">{section.replace('SUMMARY: ', '')}</p>
                                </div>
                              );
                            } else if (section.startsWith('RECENT ACTIONS:')) {
                              return (
                                <div key={index} className="pb-2 border-b border-gray-200">
                                  <h3 className="font-semibold text-gray-900 mb-2">Recent Legislative Actions</h3>
                                  <div className="text-gray-700 space-y-1">
                                    {section.replace('RECENT ACTIONS:\n', '').split('\n').map((action, idx) => (
                                      <p key={idx} className="text-sm">{action}</p>
                                    ))}
                                  </div>
                                </div>
                              );
                            } else if (section.startsWith('POLICY AREA:')) {
                              return (
                                <div key={index} className="pb-2 border-b border-gray-200">
                                  <h3 className="font-semibold text-gray-900 mb-2">Policy Area</h3>
                                  <p className="text-gray-700">{section.replace('POLICY AREA: ', '')}</p>
                                </div>
                              );
                            } else if (section.startsWith('SUBJECTS:')) {
                              return (
                                <div key={index} className="pb-2 border-b border-gray-200">
                                  <h3 className="font-semibold text-gray-900 mb-2">Subject Areas</h3>
                                  <p className="text-gray-700">{section.replace('SUBJECTS: ', '')}</p>
                                </div>
                              );
                            } else if (section.startsWith('COMMITTEES:')) {
                              return (
                                <div key={index} className="pb-2 border-b border-gray-200">
                                  <h3 className="font-semibold text-gray-900 mb-2">Assigned Committees</h3>
                                  <p className="text-gray-700">{section.replace('COMMITTEES: ', '')}</p>
                                </div>
                              );
                            } else if (section.startsWith('BILL TEXT:')) {
                              return (
                                <div key={index}>
                                  <h3 className="font-semibold text-gray-900 mb-3">Full Legislative Text</h3>
                                  <div className="whitespace-pre-wrap font-mono text-sm text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg border max-h-96 overflow-y-auto">
                                    {section.replace('BILL TEXT:\n', '')}
                                  </div>
                                </div>
                              );
                            } else if (section.trim()) {
                              return (
                                <div key={index} className="pb-2 border-b border-gray-200">
                                  <p className="text-gray-700">{section}</p>
                                </div>
                              );
                            }
                            return null;
                          })}
                        </div>
                      ) : (
                        // Unstructured content - display as-is
                        <div className="whitespace-pre-wrap font-sans text-sm text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg border">
                          {document.full_text}
                        </div>
                      )}
                      
                      {/* Additional note about full text availability */}
                      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="text-sm text-blue-800">
                          <strong>Note:</strong> Full bill text may not be available for all legislation, especially bills in early stages. 
                          For complete legislative text and the most current information, visit the official {' '}
                          {document.metadata?.web_url ? (
                            <a 
                              href={document.metadata.web_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 underline"
                            >
                              Congress.gov page
                            </a>
                          ) : (
                            'Congress.gov page'
                          )}.
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Content Not Available</h3>
                      <p className="text-gray-600 mb-4">
                        Detailed content for this legislation is not currently available. This often occurs for bills in early stages of the legislative process.
                      </p>
                      {document.metadata?.web_url && (
                        <a 
                          href={document.metadata.web_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-government-600 hover:bg-government-700 transition-colors"
                        >
                          View on Congress.gov ↗
                        </a>
                      )}
                    </div>
                  )}
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
                      {Object.entries(document.metadata)
                        .filter(([key, value]) => 
                          !key.includes('url') && 
                          !key.includes('text_fetched') && 
                          value !== null && 
                          value !== ''
                        )
                        .map(([key, value]) => (
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