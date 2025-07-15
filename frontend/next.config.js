/** @type {import('next').NextConfig} */
const nextConfig = {
  // Electron 환경을 위한 설정
  output: 'export',
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  distDir: 'out',
  
  // 이미지 최적화 비활성화 (Electron에서 문제 발생 가능)
  images: {
    unoptimized: true
  },
  
  // 환경 변수 설정
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000'
  },
  
  // TypeScript 설정
  typescript: {
    ignoreBuildErrors: false
  },
  
  // ESLint 설정
  eslint: {
    ignoreDuringBuilds: false
  },
  
  // 웹팩 설정 (필요시)
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        os: false,
      };
    }
    
    return config;
  }
};

module.exports = nextConfig; 