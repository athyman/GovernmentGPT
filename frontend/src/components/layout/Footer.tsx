import Link from 'next/link';

export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-1">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">G</span>
              </div>
              <span className="ml-3 text-xl font-bold text-gray-900">
                Government<span className="text-blue-600">GPT</span>
              </span>
            </div>
            <p className="mt-4 text-gray-600">
              Making government information accessible through AI-powered search and citizen-friendly summaries.
            </p>
          </div>

          {/* Navigation */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 tracking-wider uppercase">
              Platform
            </h3>
            <ul className="mt-4 space-y-3">
              <li>
                <Link href="/" className="text-base text-gray-600 hover:text-gray-900">
                  Search
                </Link>
              </li>
              <li>
                <Link href="/about" className="text-base text-gray-600 hover:text-gray-900">
                  About
                </Link>
              </li>
              <li>
                <Link href="/how-it-works" className="text-base text-gray-600 hover:text-gray-900">
                  How It Works
                </Link>
              </li>
              <li>
                <Link href="/donate" className="text-base text-green-600 hover:text-green-700 font-medium">
                  Donate
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 tracking-wider uppercase">
              Legal
            </h3>
            <ul className="mt-4 space-y-3">
              <li>
                <Link href="/privacy" className="text-base text-gray-600 hover:text-gray-900">
                  Privacy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-base text-gray-600 hover:text-gray-900">
                  Terms
                </Link>
              </li>
              <li>
                <a href="mailto:contact@governmentgpt.org" className="text-base text-gray-600 hover:text-gray-900">
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center text-center md:text-left">
            <div className="mb-4 md:mb-0">
              <p className="text-sm text-gray-500">
                © {new Date().getFullYear()} GovernmentGPT • Non-partisan civic platform
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Official data from Congress.gov, Federal Register, and GovTrack
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <p className="text-xs text-gray-400">
                Powered by AI for democratic transparency
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}