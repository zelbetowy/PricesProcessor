import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        port: Number(process.env.VITE_PORT) || 7070,
        proxy: {
            '/api': {  // Œcie¿ka do API
                target: 'http://backend:8080',  // Wskazuje na kontener backendu
                changeOrigin: true,
                secure: false,
            },
        },
    },
});