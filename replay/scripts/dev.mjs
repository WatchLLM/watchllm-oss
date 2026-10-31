import { spawn } from 'node:child_process';

const isWindows = process.platform === 'win32';
const npm = isWindows ? 'npm.cmd' : 'npm';
const children = [
  spawn(npm, ['run', 'dev:backend'], { stdio: 'inherit', detached: !isWindows }),
  spawn(npm, ['run', 'dev:frontend'], { stdio: 'inherit', detached: !isWindows }),
];

let shuttingDown = false;
function stop(signal = 'SIGTERM') {
  if (shuttingDown) return;
  shuttingDown = true;
  for (const child of children) {
    if (child.killed || child.pid === undefined) continue;
    try {
      // npm launches the actual dev server as a descendant. On POSIX, signal
      // the process group so those descendants cannot outlive this runner.
      if (isWindows) child.kill(signal);
      else process.kill(-child.pid, signal);
    } catch (error) {
      if (error.code !== 'ESRCH') console.error(error);
    }
  }
}

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => stop(signal));
}

for (const child of children) {
  child.on('error', (error) => {
    console.error(error);
    stop();
    process.exitCode = 1;
  });
  child.on('exit', (code, signal) => {
    if (!shuttingDown) {
      process.exitCode = code ?? (signal ? 1 : 0);
      stop();
    }
  });
}
