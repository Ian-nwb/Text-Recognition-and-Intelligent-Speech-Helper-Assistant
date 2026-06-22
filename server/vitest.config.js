import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    // Tells Vitest to climb up one level and look inside tests/backend
    include: [path.resolve(__dirname, '../tests/backend/**/*.test.{js,ts}')],
  },
});