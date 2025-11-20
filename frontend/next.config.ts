import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Use webpack with process.cwd() for Vercel build environment
  // Vercel sets Root Directory to 'frontend', so process.cwd() points to 'frontend'
  webpack: (config) => {
    // Debug logging to understand the build environment
    const cwd = process.cwd();
    const dirname = __dirname;
    const resolvedPath = path.resolve(cwd);
    const resolvedDirname = path.resolve(dirname);
    
    console.log("[Next.js Config] Debug Info:");
    console.log("  process.cwd():", cwd);
    console.log("  __dirname:", dirname);
    console.log("  path.resolve(process.cwd()):", resolvedPath);
    console.log("  path.resolve(__dirname):", resolvedDirname);
    console.log("  Setting @ alias to:", resolvedPath);
    
    // Test if lib directory exists
    const libPath = path.resolve(cwd, "lib");
    const libPathWithDirname = path.resolve(dirname, "lib");
    console.log("  lib path (cwd):", libPath);
    console.log("  lib path (dirname):", libPathWithDirname);
    
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": resolvedPath,
    };
    
    return config;
  },
};

export default nextConfig;
