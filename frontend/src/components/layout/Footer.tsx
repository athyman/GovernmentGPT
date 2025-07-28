import Link from 'next/link';

export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-government-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">G</span>
              </div>
              <span className="ml-3 text-xl font-bold text-gray-900">
                Government<span className="text-government-600">GPT</span>
              </span>
            </div>
            <p className="mt-4 text-gray-600 max-w-md">
              Making government more accessible through AI-powered search and summarization 
              of congressional bills and executive orders.
            </p>
            <div className="mt-6">
              <p className="text-sm text-gray-500">
                © {new Date().getFullYear()} GovernmentGPT. Made for civic transparency.
              </p>
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 tracking-wider uppercase">
              Product
            </h3>
            <ul className="mt-4 space-y-4">
              <li>
                <Link href="/search" className="text-base text-gray-600 hover:text-gray-900">
                  Search Documents
                </Link>
              </li>
              <li>
                <Link href="/recent" className="text-base text-gray-600 hover:text-gray-900">
                  Recent Actions
                </Link>
              </li>
              <li>
                <Link href="/api" className="text-base text-gray-600 hover:text-gray-900">
                  API Access
                </Link>
              </li>
              <li>
                <Link href="/how-it-works" className="text-base text-gray-600 hover:text-gray-900">
                  How It Works
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 tracking-wider uppercase">
              Resources
            </h3>
            <ul className="mt-4 space-y-4">
              <li>
                <Link href="/about" className="text-base text-gray-600 hover:text-gray-900">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-base text-gray-600 hover:text-gray-900">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-base text-gray-600 hover:text-gray-900">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-base text-gray-600 hover:text-gray-900">
                  Contact
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-6">
              <p className="text-sm text-gray-500">
                Data sources:
              </p>
              <div className="flex items-center space-x-4 text-sm text-gray-400">
                <span>Congress.gov</span>
                <span>•</span>
                <span>GovTrack</span>
                <span>•</span>
                <span>Federal Register</span>
              </div>
            </div>
            
            <div className="mt-4 md:mt-0 flex items-center space-x-4">
              <p className="text-sm text-gray-500">
                Powered by AI for democratic transparency
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}