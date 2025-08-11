import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'OpenBank Transfers',
        short_name: 'Transfers',
        start_url: '/',
        display: 'standalone',
        background_color: '#ffffff',
        theme_color: '#0d9488',
        icons: []
      }
    })
  ],
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8080',
      '/accounts': 'http://localhost:8080',
      '/transfers': 'http://localhost:8080',
      '/kyc': 'http://localhost:8080',
      '/admin': 'http://localhost:8080',
      '/hooks': 'http://localhost:8080',
      '/notifications': 'http://localhost:8080',
      '/health': 'http://localhost:8080'
    }
  },
  build: { outDir: 'dist' }
})