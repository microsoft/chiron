import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: './dist',
    emptyOutDir: true,
    sourcemap: true
  },
  server: {
    port: 5173,
    host: true,
  }
  //   proxy: {
  //     '/ask': 'http://localhost:5000',
  //     '/chat': 'http://localhost:5000'
  //   }
  // }
})
