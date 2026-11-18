import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: { license: { fileName: 'THIRD_PARTY_LICENSES.md' } },
  server: {
    host: '127.0.0.1',
    proxy: { '/api': 'http://127.0.0.1:8501' },
  },
});
