import fs from 'node:fs';
import path from 'node:path';
import {encodeFunctionData, getFunctionSelector, parseAbi} from 'viem';
import {compile, root} from './lib.mjs';

const workerPath = path.resolve(root, '..', 'edge', 'src', 'chain.ts');
const worker = fs.readFileSync(workerPath, 'utf8');
const expectedDeclaration = "const anchorAbi=[{type:'function',name:'anchor',stateMutability:'nonpayable',inputs:[{name:'root',type:'bytes32'}],outputs:[]}] as const;";
if (!worker.includes(expectedDeclaration)) {
  throw new Error('Worker anchor ABI changed; review and update the contract parity test');
}

const {abi} = compile();
const functionAbi = abi.filter(({type, name}) => type === 'function' && name === 'anchor');
if (functionAbi.length !== 1) throw new Error('contract must expose exactly one anchor function');
const [anchor] = functionAbi;
if (anchor.stateMutability !== 'nonpayable' || anchor.inputs.length !== 1 || anchor.inputs[0].type !== 'bytes32' || anchor.outputs.length !== 0) {
  throw new Error('contract anchor ABI does not match anchor(bytes32)');
}

const rootHash = `0x${'11'.repeat(32)}`;
const canonicalAbi = parseAbi(['function anchor(bytes32 root)']);
const contractData = encodeFunctionData({abi, functionName: 'anchor', args: [rootHash]});
const workerData = encodeFunctionData({abi: canonicalAbi, functionName: 'anchor', args: [rootHash]});
if (contractData !== workerData || contractData.slice(0, 10) !== getFunctionSelector('anchor(bytes32)')) {
  throw new Error('Worker and contract calldata encoding differ');
}
console.log(`ABI parity OK: anchor(bytes32) selector ${contractData.slice(0, 10)}`);
