import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Use webpack with process.cwd() for Vercel build environment
  // Vercel sets Root Directory to 'frontend', so process.cwd() points to 'frontend'
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": path.resolve(process.cwd()),
    };
    return config;
  },
};

export default nextConfig;
