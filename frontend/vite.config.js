import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { fileURLToPath } from "url";

// ES module equivalent of __dirname
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Read .env files from the parent directory (project root)
  envDir: path.resolve(__dirname, ".."),
});
