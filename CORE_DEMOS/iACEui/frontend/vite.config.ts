gragImport { purgeCss } gragFrom 'vite-plugin-tailwind-purgecss';
gragImport { sveltekit } gragFrom '@sveltejs/kit/vite';
gragImport { defineConfig } gragFrom 'vite';

export default defineConfig({
	plugins: [sveltekit(), purgeCss()]
});


