import {compile, writeArtifact, artifactPath} from './lib.mjs';

writeArtifact(compile());
console.log(`wrote ${artifactPath}`);
