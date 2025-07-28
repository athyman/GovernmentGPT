/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    // Type checking is handled by separate command
    ignoreBuildErrors: false,
  },
  eslint: {
    // Linting is handled by separate command  
    ignoreDuringBuilds: false,
  },
  experimental: {
    // Enable server components optimizations
    serverComponentsExternalPackages: [],
  },
  images: {
    // Configure image optimization
    domains: [],
    unoptimized: false,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;