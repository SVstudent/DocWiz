/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'storage.googleapis.com'],
  },
  experimental: {
    serverActions: true,
  },
};

module.exports = nextConfig;
