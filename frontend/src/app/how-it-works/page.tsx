'use client';

import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  CloudArrowDownIcon,
  CpuChipIcon,
  DocumentMagnifyingGlassIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

export default function HowItWorksPage() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      
      <main className="flex-1">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              How Government<span className="text-blue-600">GPT</span> Works
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Discover how we transform complex legislative documents into accessible, 
              searchable insights using cutting-edge AI and official government data sources.
            </p>
          </div>

          {/* Process Overview */}
          <div className="mb-12">
            <h2 className="text-2xl font-semibold text-gray-900 mb-8 text-center">
              From Government Documents to Citizen Insights
            </h2>
            
            <div className="grid md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CloudArrowDownIcon className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Data Collection</h3>
                <p className="text-sm text-gray-600">
                  Automatic ingestion from official government APIs
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CpuChipIcon className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">AI Processing</h3>
                <p className="text-sm text-gray-600">
                  Advanced language models analyze and summarize content
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <ShieldCheckIcon className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Verification</h3>
                <p className="text-sm text-gray-600">
                  Multi-layer validation ensures accuracy and neutrality
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <UserGroupIcon className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Citizen Access</h3>
                <p className="text-sm text-gray-600">
                  Accessible, searchable information for everyone
                </p>
              </div>
            </div>
          </div>

          {/* Data Sources */}
          <Card className="mb-8">
            <CardHeader>
              <h2 className="text-2xl font-semibold text-gray-900">Official Data Sources</h2>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 mb-6">
                We collect information exclusively from authoritative government sources to ensure 
                accuracy and authenticity. Our data pipeline processes thousands of documents daily.
              </p>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Congressional Data</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span><strong>Congress.gov API</strong> - Official bill text and metadata</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span><strong>GovInfo API</strong> - Congressional documents and records</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span><strong>GovTrack API</strong> - Voting records and legislator info</span>
                    </li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Executive Branch</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span><strong>Federal Register API</strong> - Executive orders and regulations</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span><strong>White House API</strong> - Presidential documents</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span><strong>Agency APIs</strong> - Department-specific actions</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Processing Pipeline */}
          <Card className="mb-8">
            <CardHeader>
              <h2 className="text-2xl font-semibold text-gray-900">AI Processing Pipeline</h2>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold">1</span>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Document Analysis</h3>
                    <p className="text-gray-700 mb-3">
                      Our AI system analyzes the structure, content, and legal language of each document 
                      to understand key provisions, impacts, and legislative context.
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="outline">Legal Text Processing</Badge>
                      <Badge variant="outline">Section Identification</Badge>
                      <Badge variant="outline">Context Understanding</Badge>
                    </div>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold">2</span>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Plain Language Translation</h3>
                    <p className="text-gray-700 mb-3">
                      Complex legal language is transformed into citizen-friendly explanations while 
                      preserving accuracy and nuance. We follow Federal Plain Writing Act guidelines.
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="outline">8th Grade Reading Level</Badge>
                      <Badge variant="outline">Active Voice</Badge>
                      <Badge variant="outline">Common Vocabulary</Badge>
                    </div>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold">3</span>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Semantic Indexing</h3>
                    <p className="text-gray-700 mb-3">
                      Documents are indexed using advanced embedding techniques that understand 
                      context and meaning, enabling intelligent search beyond simple keyword matching.
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="outline">Vector Embeddings</Badge>
                      <Badge variant="outline">Topic Modeling</Badge>
                      <Badge variant="outline">Relationship Mapping</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quality Assurance */}
          <Card className="mb-8">
            <CardHeader>
              <h2 className="text-2xl font-semibold text-gray-900">Quality Assurance & Verification</h2>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <p className="text-gray-700">
                  Every AI-generated summary goes through multiple validation layers to ensure accuracy, 
                  neutrality, and readability while maintaining connection to official source documents.
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Automated Checks</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-start gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Source Verification:</strong> Cross-reference with original documents</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Fact Accuracy:</strong> Validate specific claims and numbers</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Bias Detection:</strong> Identify and correct partisan language</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Readability:</strong> Ensure appropriate grade level and clarity</span>
                    </li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Editorial Review</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-start gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Professional Staff:</strong> Subject matter expert validation</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Legal Accuracy:</strong> Verify interpretation and implications</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Neutrality Check:</strong> Ensure political balance and objectivity</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Accessibility:</strong> Test with real users and screen readers</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Search Technology */}
          <Card className="mb-8">
            <CardHeader>
              <div className="flex items-center gap-3">
                <DocumentMagnifyingGlassIcon className="h-6 w-6 text-blue-600" />
                <h2 className="text-2xl font-semibold text-gray-900">Intelligent Search Technology</h2>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Hybrid Search Approach</h3>
                  <p className="text-gray-700 mb-4">
                    Our search combines multiple techniques to find the most relevant information, 
                    even when you don't know the exact terms or official language.
                  </p>
                  
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Semantic Search</h4>
                      <p className="text-sm text-blue-800">
                        Understands meaning and context, finding relevant content even with different wording
                      </p>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Keyword Matching</h4>
                      <p className="text-sm text-blue-800">
                        Traditional text search for precise terms and official language
                      </p>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Fuzzy Matching</h4>
                      <p className="text-sm text-blue-800">
                        Finds results even with typos, abbreviations, or partial information
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Search Features</h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    <ul className="space-y-2 text-gray-700">
                      <li className="flex items-center gap-2">
                        <ArrowRightIcon className="h-4 w-4 text-blue-600 flex-shrink-0" />
                        <span>Natural language queries</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <ArrowRightIcon className="h-4 w-4 text-blue-600 flex-shrink-0" />
                        <span>Advanced filtering by date, status, and type</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <ArrowRightIcon className="h-4 w-4 text-blue-600 flex-shrink-0" />
                        <span>Related document suggestions</span>
                      </li>
                    </ul>
                    <ul className="space-y-2 text-gray-700">
                      <li className="flex items-center gap-2">
                        <ArrowRightIcon className="h-4 w-4 text-blue-600 flex-shrink-0" />
                        <span>Topic-based categorization</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <ArrowRightIcon className="h-4 w-4 text-blue-600 flex-shrink-0" />
                        <span>Impact and scope analysis</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <ArrowRightIcon className="h-4 w-4 text-blue-600 flex-shrink-0" />
                        <span>Real-time search suggestions</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* User Experience Design */}
          <Card className="mb-8">
            <CardHeader>
              <h2 className="text-2xl font-semibold text-gray-900">User Experience Design</h2>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Progressive Disclosure</h3>
                  <p className="text-gray-700 mb-4">
                    Information is presented in layers, allowing you to dive as deep as your interest 
                    and expertise require without being overwhelmed by complexity.
                  </p>
                  
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-green-600 font-medium text-sm">L1</span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-900">Summary Level:</span>
                        <span className="text-gray-700 ml-2">Key points and citizen impacts</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-blue-600 font-medium text-sm">L2</span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-900">Detail Level:</span>
                        <span className="text-gray-700 ml-2">Specific provisions and mechanisms</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-purple-600 font-medium text-sm">L3</span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-900">Reference Level:</span>
                        <span className="text-gray-700 ml-2">Full text and legal documents</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Accessibility Features</h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    <ul className="space-y-2 text-gray-700">
                      <li className="flex items-center gap-2">
                        <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                        <span>Screen reader compatible</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                        <span>High contrast color options</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                        <span>Keyboard navigation support</span>
                      </li>
                    </ul>
                    <ul className="space-y-2 text-gray-700">
                      <li className="flex items-center gap-2">
                        <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                        <span>Mobile-first responsive design</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                        <span>Adjustable font sizes</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                        <span>Focus indicators and ARIA labels</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Limitations & Transparency */}
          <Card className="mb-8 border-orange-200 bg-orange-50">
            <CardHeader>
              <div className="flex items-center gap-3">
                <ExclamationTriangleIcon className="h-6 w-6 text-orange-600" />
                <h2 className="text-2xl font-semibold text-gray-900">Limitations & Important Notes</h2>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 text-gray-700">
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">AI-Generated Content</h3>
                  <p>
                    Summaries are created by AI and may not capture every nuance of complex legislation. 
                    Always refer to official sources for legal or professional purposes.
                  </p>
                </div>
                
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Data Freshness</h3>
                  <p>
                    We update our database regularly, but there may be a delay between official 
                    government actions and their appearance in our system.
                  </p>
                </div>
                
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Not Legal Advice</h3>
                  <p>
                    This platform provides educational information only and should not be considered 
                    legal advice or official government guidance.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Call to Action */}
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Ready to Explore Government Actions?
            </h2>
            <p className="text-lg text-gray-600 mb-6">
              Experience intelligent search and AI-powered summaries for yourself.
            </p>
            <a
              href="/"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
            >
              Try It Now
            </a>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}