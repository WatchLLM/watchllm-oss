const args = process.argv.slice(2);

function readArg(name, fallback) {
  const index = args.indexOf(name);
  if (index === -1 || index + 1 >= args.length) {
    return fallback;
  }

  return args[index + 1];
}

const exitCode = Number(readArg('--exit', '0'));
const sleepMs = Number(readArg('--sleep-ms', '0'));
const language = readArg('--language', '');
const mode = readArg('--mode', '');

let stdin = '';

process.stdin.setEncoding('utf8');

process.stdin.on('data', (chunk) => {
  stdin += chunk;
});

process.stdin.on('end', () => {
  setTimeout(() => {
    process.stdout.write(JSON.stringify({
      ok: exitCode === 0,
      exitCode,
      language,
      mode,
      stdin,
      args
    }));

    process.exit(exitCode);
  }, sleepMs);
});
