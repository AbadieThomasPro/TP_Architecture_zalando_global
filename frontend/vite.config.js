import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 4000,
    proxy: {
      '/catalog-api': {
        target: 'http://catalog-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/catalog-api/, '/api'),
      },
      '/customer-api': {
        target: 'http://customer-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/customer-api/, '/api'),
      },
      '/order-api': {
        target: 'http://order-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/order-api/, '/api'),
      },
    },
  },
})
