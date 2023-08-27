import svelte from '%jellyserve.rollup.svelte.path%';
import resolve from '%jellyserve.rollup.resolve.path%';

export default {
  input: '%jellyserve.component.template.js%',
  output: {
    file: '%jellyserve.component.compiled%',
    format: 'iife',
    name: 'app',
  },
  plugins: [
    svelte({
      include: '%jellyserve.frontend.path%/*.svelte',
    }),
    resolve({ browser: true }),
  ],
};