import svelte from '$svelte_path';
import resolve from '$resolve_path';
import css from '$css_path'

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
    }),
    resolve({ browser: true }),
    css({ output: "output.css" })
  ],
};