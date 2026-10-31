import fs from 'node:fs';
import path from 'node:path';
import solc from 'solc';

export const root = path.resolve(import.meta.dirname, '..');
export const sourcePath = path.join(root, 'contracts', 'WebProofAnchor.sol');
export const artifactPath = path.join(root, 'artifacts', 'WebProofAnchor.json');

export function compile() {
  const source = fs.readFileSync(sourcePath, 'utf8');
  const input = {
    language: 'Solidity',
    sources: {'WebProofAnchor.sol': {content: source}},
    settings: {
      optimizer: {enabled: true, runs: 200},
      outputSelection: {'*': {'*': ['abi', 'evm.bytecode.object', 'evm.deployedBytecode.object']}},
    },
  };
  const output = JSON.parse(solc.compile(JSON.stringify(input)));
  const errors = (output.errors ?? []).filter(({severity}) => severity === 'error');
  if (errors.length) throw new Error(errors.map(({formattedMessage}) => formattedMessage).join('\n'));
  const contract = output.contracts['WebProofAnchor.sol'].WebProofAnchor;
  return {
    contractName: 'WebProofAnchor',
    compiler: solc.version(),
    abi: contract.abi,
    bytecode: `0x${contract.evm.bytecode.object}`,
    deployedBytecode: `0x${contract.evm.deployedBytecode.object}`,
  };
}

export function writeArtifact(artifact) {
  fs.mkdirSync(path.dirname(artifactPath), {recursive: true});
  fs.writeFileSync(artifactPath, `${JSON.stringify(artifact, null, 2)}\n`);
}
