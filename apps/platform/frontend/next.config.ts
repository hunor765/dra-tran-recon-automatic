import type { NextConfig } from "next";
const nextConfig: NextConfig = {
  distDir: 'dist',
  devIndicators: false,
  images: {
    unoptimized: true,
  },
};
export default nextConfig;
