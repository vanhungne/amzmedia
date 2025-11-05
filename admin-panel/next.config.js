/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    JWT_SECRET: process.env.JWT_SECRET || 'your-secret-key-change-in-production',
  },
}

module.exports = nextConfig

