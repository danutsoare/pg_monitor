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
  }
}) 