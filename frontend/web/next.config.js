const BACKEND_BASE = process.env.BACKEND_BASE_URL || 'http://13.235.114.242:8000';

/** @type {import('next').NextConfig} */
module.exports = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        // forward to backend's /api/v1/<path>
        destination: `${BACKEND_BASE}/api/v1/:path*`,
      },
    ];
  },
};
