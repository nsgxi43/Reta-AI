import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://reta-backend-83946652910.us-central1.run.app",
  },
};

export default nextConfig;
