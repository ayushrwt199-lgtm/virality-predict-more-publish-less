import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  tanstackStart: {
    server: { entry: "server" },
  },
  vite: {
    server: {
      port: 5173,
      host: true,
      proxy: {
        "/api": {
          target: "http://localhost:8000",
          changeOrigin: true,
        },
        "/health": {
          target: "http://localhost:8000",
          changeOrigin: true,
        },
        "/docs": {
          target: "http://localhost:8000",
          changeOrigin: true,
        },
        "/openapi.json": {
          target: "http://localhost:8000",
          changeOrigin: true,
        },
      },
    },
  },
});
