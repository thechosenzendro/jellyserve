import svelte from '$svelte_path';
import resolve from '$resolve_path';

export default {
  input: '$js_input',
  output: {
    file: '$js_output',
    format: 'iife',
    name: 'app',
  },
  plugins: [
    svelte({
      include: '$frontend_path/**/*.svelte',
      emitCss: false
    }),
    resolve({ browser: true }),
  ],
};