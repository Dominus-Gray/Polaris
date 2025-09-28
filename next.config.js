/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: [
      'localhost',
      'polaris-migrate.preview.emergentagent.com',
      'images.unsplash.com',
      'via.placeholder.com'
    ],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  env: {
    API_URL: process.env.API_URL || 'http://localhost:8001',
    APP_URL: process.env.APP_URL || 'http://localhost:3000',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.API_URL || 'http://localhost:8001'}/api/:path*`,
      },
    ];
  },
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3000', 'polaris-migrate.preview.emergentagent.com']
    }
  }
};

module.exports = nextConfig;