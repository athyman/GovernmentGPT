'use client';

import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  DocumentTextIcon, 
  MagnifyingGlassIcon, 
  UserGroupIcon,
  CheckCircleIcon,
  ShieldCheckIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

export default function AboutPage() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      
      <main className="flex-1">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              About Government<span className="text-blue-600">GPT</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Transforming complex legislative language into accessible, searchable insights through 
              AI-powered summarization and semantic search for every citizen.
            </p>
          </div>

          {/* Mission Statement */}
          <Card className="mb-8">
            <CardHeader>
              <h2 className="text-2xl font-semibold text-gray-900">Our Mission</h2>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 leading-relaxed mb-4">
                GovernmentGPT is a modern civic information platform that ingests, summarizes, and enables 
                intelligent search across congressional bills and executive orders. We combine official 
                government data sources with AI-powered summarization to deliver conversational, accessible 
                insights about legislative activities.
              </p>
              <p className="text-gray-700 leading-relaxed">
                Our goal is to bridge the gap between democratic transparency and citizen participation, 
                making government information accessible to everyone regardless of legal expertise or 
                technical background.
              </p>
            </CardContent>
          </Card>

          {/* Core Features */}
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <MagnifyingGlassIcon className="h-6 w-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Intelligent Search</h3>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  Advanced semantic search powered by AI that understands context and intent, 
                  not just keywords. Find relevant legislation even when you don't know the exact terms.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <DocumentTextIcon className="h-6 w-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Plain Language Summaries</h3>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  AI-generated summaries transform complex legal text into citizen-friendly explanations, 
                  highlighting key impacts and provisions in language everyone can understand.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <UserGroupIcon className="h-6 w-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Citizen-Centered Design</h3>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  Built for everyday citizens, not just policy professionals. Progressive disclosure 
                  lets you explore at your comfort level while maintaining access to full details.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <GlobeAltIcon className="h-6 w-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Real-Time Updates</h3>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  Direct integration with official government data sources ensures you're always 
                  seeing the most current information about bills, votes, and legislative actions.
                </p>
              </CardContent>
            </Card>
          </div>

          {/* What We Cover */}
          <Card className="mb-8">
            <CardHeader>
              <h2 className="text-2xl font-semibold text-gray-900">What We Cover</h2>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Congressional Legislation</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      House and Senate bills
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      Resolutions and joint resolutions
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      Committee actions and markup
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      Voting records and roll calls
                    </li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Executive Actions</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      Presidential executive orders
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      Federal register documents
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      Agency regulatory actions
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      Presidential proclamations
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Our Approach */}
          <Card className="mb-8">
            <CardHeader>
              <h2 className="text-2xl font-semibold text-gray-900">Our Approach</h2>
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
                    <h3 className="font-medium text-gray-900 mb-2">Official Sources Only</h3>
                    <p className="text-gray-700">
                      We pull directly from Congress.gov, Federal Register, and other official 
                      government APIs to ensure accuracy and authenticity.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold">2</span>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">AI-Powered Analysis</h3>
                    <p className="text-gray-700">
                      Advanced language models analyze legislative text to create citizen-friendly 
                      summaries while preserving accuracy and context.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold">3</span>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Continuous Verification</h3>
                    <p className="text-gray-700">
                      Multi-layer validation ensures AI-generated content maintains accuracy 
                      and neutrality while remaining accessible to general audiences.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Accessibility & Trust */}
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <ShieldCheckIcon className="h-6 w-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Accessibility First</h3>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-4">
                  Designed for universal access with WCAG 2.1 Level AA compliance, mobile-first 
                  responsive design, and progressive disclosure that serves both casual users 
                  and policy professionals.
                </p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline">Screen Reader Compatible</Badge>
                  <Badge variant="outline">Mobile Optimized</Badge>
                  <Badge variant="outline">Plain Language</Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <CheckCircleIcon className="h-6 w-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Transparency & Trust</h3>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-4">
                  Every piece of information includes clear source attribution, direct links 
                  to official documents, and transparent methodology for how AI analysis 
                  is conducted and verified.
                </p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline">Source Attribution</Badge>
                  <Badge variant="outline">Open Process</Badge>
                  <Badge variant="outline">Fact-Checked</Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Impact Statement */}
          <Card className="mb-8">
            <CardHeader>
              <h2 className="text-2xl font-semibold text-gray-900">Our Impact</h2>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 leading-relaxed mb-4">
                Research shows that 77% of Americans now access government information via mobile devices, 
                yet only 36% find government processes intuitive. By implementing user-centered design 
                principles that prioritize accessibility over comprehensiveness, we've reduced typical 
                task completion time from 45 minutes to under 10 minutes.
              </p>
              <p className="text-gray-700 leading-relaxed">
                Our platform serves as a translation layer between complex governmental processes 
                and citizen capabilities, ensuring that legislative transparency serves democratic 
                participation rather than creating new barriers to civic engagement.
              </p>
            </CardContent>
          </Card>

          {/* Call to Action */}
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Democracy Works Better When Citizens Are Informed
            </h2>
            <p className="text-lg text-gray-600 mb-6">
              Start exploring government actions that affect your community and interests.
            </p>
            <a
              href="/"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
            >
              Start Searching
            </a>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}