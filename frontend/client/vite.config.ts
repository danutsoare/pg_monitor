import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      usePolling: true, // Needed for Docker container file watching
    },
    host: true, // Needed for Docker container exposure
    strictPort: true,
    port: 5173, // Default Vite port
    proxy: {
      '/api': {
        target: 'http://backend:8000', // Target the backend service name from docker-compose
        changeOrigin: true, // Recommended for virtual hosted sites
        // secure: false, // Uncomment if your backend is not using HTTPS (likely in dev)
        // rewrite: (path) => path.replace(/^\/api/, ''), // Uncomment if backend doesn't expect /api prefix
      }
    }
  }
}) 