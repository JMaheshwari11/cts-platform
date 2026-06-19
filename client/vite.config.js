import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
  build: {
    chunkSizeWarningLimit: 700,
    rolldownOptions: {
      output: {
        advancedChunks: {
          groups: [
            { name: "vendor-echarts",  test: /echarts|zrender[\\/]/ },
            { name: "vendor-react",    test: /react|react-dom|scheduler[\\/]/ },
            { name: "vendor-router",   test: /react-router|@remix-run[\\/]/ },
            { name: "vendor-query",    test: /[\\/]node_modules[\\/]@tanstack[\\/]/ },
            { name: "vendor-state",    test: /[\\/]node_modules[\\/]zustand[\\/]/ },
            { name: "vendor-http",     test: /[\\/]node_modules[\\/]axios[\\/]/ },
            { name: "vendor-icons",    test: /[\\/]node_modules[\\/]lucide-react[\\/]/ },
            { name: "vendor-leaflet",  test: /leaflet|react-leaflet[\\/]/ },
            { name: "vendor-misc",     test: /[\\/]node_modules[\\/]/ },
            { name: "charts-shared",   test: /[\\/]src[\\/]components[\\/]charts[\\/]/ },
            { name: "simulator-ui",    test: /[\\/]src[\\/]components[\\/]simulator[\\/]/ },
            { name: "maps",            test: /[\\/]src[\\/]components[\\/]maps[\\/]/ },
          ],
        },
      },
    },
  },
})
