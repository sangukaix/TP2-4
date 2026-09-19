import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react()],
    // TP2-4 기본 개발 포트는 8200·8212입니다. 배포에서는 Nginx가 /api와 /ai를 라우팅합니다.
    server: {
      // Tailscale Funnel의 공개 HTTPS 호스트만 추가로 허용합니다.
      // 모든 호스트 허용 대신 *.ts.net으로 제한해 DNS rebinding 범위를 넓히지 않습니다.
      allowedHosts: ['.ts.net'],
      proxy: {
        '/api': {
          target: env.VITE_BACKEND_PROXY_TARGET || 'http://127.0.0.1:8200',
          changeOrigin: true,
        },
        '/ai': {
          target: env.VITE_AI_PROXY_TARGET || 'http://127.0.0.1:8212',
          changeOrigin: true,
        },
      },
    },
  }
})
