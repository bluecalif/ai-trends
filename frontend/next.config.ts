import type { NextConfig } from "next";
import path from "path";
import fs from "fs";

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
    
    // Test if lib directory and files exist
    const libPath = path.resolve(cwd, "lib");
    const libPathWithDirname = path.resolve(dirname, "lib");
    console.log("  lib path (cwd):", libPath);
    console.log("  lib path (dirname):", libPathWithDirname);
    console.log("  lib directory exists (cwd):", fs.existsSync(libPath));
    console.log("  lib directory exists (dirname):", fs.existsSync(libPathWithDirname));
    
    // Check specific files
    const testFiles = ["constants.ts", "validators.ts", "providers.tsx"];
    testFiles.forEach((file) => {
      const filePath = path.resolve(libPath, file);
      const filePathWithDirname = path.resolve(libPathWithDirname, file);
      console.log(`  ${file} exists (cwd):`, fs.existsSync(filePath), "at", filePath);
      console.log(`  ${file} exists (dirname):`, fs.existsSync(filePathWithDirname), "at", filePathWithDirname);
    });
    
    // List lib directory contents
    if (fs.existsSync(libPath)) {
      try {
        const libContents = fs.readdirSync(libPath);
        console.log("  lib directory contents:", libContents);
      } catch (e) {
        console.log("  Error reading lib directory:", e);
      }
    }
    
    // Enhanced webpack resolve configuration
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": resolvedPath,
    };
    
    // Ensure extensions are properly configured
    if (!config.resolve.extensions) {
      config.resolve.extensions = [];
    }
    // Add TypeScript extensions if not already present
    const extensions = [".ts", ".tsx", ".js", ".jsx", ".json"];
    extensions.forEach((ext) => {
      if (!config.resolve.extensions.includes(ext)) {
        config.resolve.extensions.push(ext);
      }
    });
    
    console.log("  webpack resolve.extensions:", config.resolve.extensions);
    console.log("  webpack resolve.alias:", config.resolve.alias);
    
    return config;
  },
};

export default nextConfig;
