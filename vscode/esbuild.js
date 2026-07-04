const esbuild = require('esbuild');

const production = process.argv.includes('--production');
const watch = process.argv.includes('--watch');

/** @type {import('esbuild').BuildOptions} */
const options = {
  entryPoints: ['src/extension.ts'],
  bundle: true,
  outfile: 'dist/extension.js',
  external: ['vscode'],
  platform: 'node',
  target: 'node18',
  format: 'cjs',
  sourcemap: !production,
  minify: production,
  sourcesContent: false,
  logLevel: 'info'
};

async function main() {
  if (watch) {
    const context = await esbuild.context(options);
    await context.watch();
    console.log('Watching WatchLLM extension bundle...');
    return;
  }

  await esbuild.build(options);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
