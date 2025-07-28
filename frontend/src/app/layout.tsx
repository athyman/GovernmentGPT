import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { QueryProvider } from '@/lib/query-provider';
import { Toaster } from '@/components/ui/toaster';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'GovernmentGPT - Understand Government Actions',
  description: 'Intelligent search and AI-powered summaries of congressional bills and executive orders. Making government more accessible to citizens.',
  keywords: 'government, legislation, bills, executive orders, AI, civic engagement, transparency',
  authors: [{ name: 'GovernmentGPT Team' }],
  creator: 'GovernmentGPT',
  publisher: 'GovernmentGPT',
  robots: {
    index: true,
    follow: true,
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
  },
  themeColor: '#0ea5e9',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    title: 'GovernmentGPT - Understand Government Actions',
    description: 'Intelligent search and AI-powered summaries of congressional bills and executive orders.',
    siteName: 'GovernmentGPT',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'GovernmentGPT - Making government more accessible',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'GovernmentGPT - Understand Government Actions',
    description: 'Intelligent search and AI-powered summaries of congressional bills and executive orders.',
    images: ['/og-image.png'],
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full antialiased`}>
        <QueryProvider>
          <div className="min-h-full">
            {children}
          </div>
          <Toaster />
        </QueryProvider>
      </body>
    </html>
  );
}