/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      { source: '/api/books/:path*',         destination: `${process.env.BOOK_CATALOG_URL || 'http://book-catalog:5001'}/api/books/:path*` },
      { source: '/api/users/:path*',         destination: `${process.env.USER_SERVICE_URL || 'http://user-service:5002'}/api/users/:path*` },
      { source: '/auth/:path*',              destination: `${process.env.USER_SERVICE_URL || 'http://user-service:5002'}/auth/:path*` },
      { source: '/api/borrow/:path*',        destination: `${process.env.BORROWING_SERVICE_URL || 'http://borrowing-service:5003'}/api/borrow/:path*` },
      { source: '/api/notifications/:path*', destination: `${process.env.NOTIFICATION_SERVICE_URL || 'http://notification-service:5004'}/api/notifications/:path*` },
    ];
  },
};

module.exports = nextConfig;
