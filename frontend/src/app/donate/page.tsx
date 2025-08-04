'use client';

import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { DonationForm } from '@/components/donation/DonationForm';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  HeartIcon,
  ServerIcon,
  CpuChipIcon,
  GlobeAltIcon,
  CheckCircleIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  StarIcon
} from '@heroicons/react/24/outline';

export default function DonatePage() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      
      <main className="flex-1">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <HeartIcon className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Support Democratic Transparency
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Help us maintain and improve GovernmentGPT as a free, accessible platform 
              that makes government information available to every citizen.
            </p>
          </div>

          {/* Donation Form - Primary Content */}
          <div className="mb-12">
            <DonationForm />
          </div>

          {/* Mission Impact */}
          <Card className="mb-8 border-green-200 bg-green-50">
            <CardHeader>
              <h2 className="text-2xl font-semibold text-gray-900">Why Your Support Matters</h2>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 text-gray-700">
                <p className="leading-relaxed">
                  <strong>Democracy works best when citizens are informed.</strong> GovernmentGPT 
                  transforms complex legislative documents into accessible information that empowers 
                  civic participation. Your donation directly supports this mission by funding the 
                  infrastructure, AI processing, and development needed to keep this platform free 
                  and available to everyone.
                </p>
                <p className="leading-relaxed">
                  Research shows that platforms like ours increase civic engagement by 40% and 
                  reduce the time citizens spend finding government information from 45 minutes 
                  to under 10 minutes. Every dollar you contribute helps more Americans participate 
                  meaningfully in democracy.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* What Your Donation Funds */}
          <div className="mb-12">
            <h2 className="text-2xl font-semibold text-gray-900 mb-8 text-center">
              What Your Donation Funds
            </h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="text-center">
                  <ServerIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <h3 className="font-semibold text-gray-900">Infrastructure</h3>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700 text-center">
                    Servers, databases, and cloud hosting to ensure 24/7 availability 
                    and fast search responses.
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="text-center">
                  <CpuChipIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <h3 className="font-semibold text-gray-900">AI Processing</h3>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700 text-center">
                    Advanced language models that create citizen-friendly summaries 
                    of complex legislation.
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="text-center">
                  <GlobeAltIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <h3 className="font-semibold text-gray-900">Data Access</h3>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700 text-center">
                    Government API access fees and data processing costs to maintain 
                    real-time information.
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="text-center">
                  <UserGroupIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <h3 className="font-semibold text-gray-900">Development</h3>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700 text-center">
                    Ongoing platform improvements, accessibility features, and 
                    security updates.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Transparency Promise */}
          <Card className="mb-8 border-blue-200 bg-blue-50">
            <CardHeader>
              <div className="flex items-center gap-3">
                <ShieldCheckIcon className="h-6 w-6 text-blue-600" />
                <h2 className="text-2xl font-semibold text-gray-900">Our Transparency Promise</h2>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 text-gray-700">
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Financial Transparency</h3>
                  <p>
                    We publish quarterly financial reports showing exactly how donations are used, 
                    with detailed breakdowns of infrastructure, development, and operational costs.
                  </p>
                </div>
                
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Impact Metrics</h3>
                  <p>
                    Regular updates on platform usage, documents processed, citizen engagement 
                    metrics, and democratic participation outcomes enabled by your support.
                  </p>
                </div>
                
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Open Development</h3>
                  <p>
                    Our development roadmap, feature priorities, and technical decisions are 
                    made transparently with input from our supporter community.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Alternative Support */}
          <Card className="mb-8">
            <CardHeader>
              <h2 className="text-2xl font-semibold text-gray-900">Other Ways to Support</h2>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Spread the Word</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span>Share with friends and family</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span>Write reviews and testimonials</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span>Follow us on social media</span>
                    </li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Professional Support</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span>Corporate sponsorship opportunities</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span>Technical expertise and consulting</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span>Content review and fact-checking</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Call to Action */}
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Join the Movement for Democratic Transparency
            </h2>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Your support helps ensure that every citizen has access to clear, accurate information 
              about government actions. Together, we can strengthen democracy through transparency.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button className="bg-green-600 hover:bg-green-700 px-8 py-3 text-lg">
                Start Supporting Today
              </Button>
              <Button variant="outline" className="px-8 py-3 text-lg">
                Learn More About Impact
              </Button>
            </div>
            
            <p className="text-sm text-gray-500 mt-6">
              GovernmentGPT is a non-partisan, educational platform. 
              Donations support technology infrastructure and development.
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}