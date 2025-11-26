import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 9835,
    host: '0.0.0.0',
    strictPort: true // 强制使用指定端口
  },
  preview: {
    port: 9835,
    host: '0.0.0.0'
  }
})