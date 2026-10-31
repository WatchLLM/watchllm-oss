import assert from 'node:assert/strict';
import {after, before, test} from 'node:test';
import ganache from 'ganache';
import {
  createPublicClient,
  createTestClient,
  createWalletClient,
  custom,
  decodeEventLog,
  getAddress,
  parseEventLogs,
  zeroAddress,
} from 'viem';
import {privateKeyToAccount} from 'viem/accounts';
import {compile} from '../scripts/lib.mjs';

const chain = {
  id: 84532,
  name: 'Local Base-compatible EVM',
  nativeCurrency: {name: 'Ether', symbol: 'ETH', decimals: 18},
  rpcUrls: {default: {http: ['http://127.0.0.1']}},
};
const operatorKey = `0x${'11'.repeat(32)}`;
const attackerKey = `0x${'22'.repeat(32)}`;
const operator = privateKeyToAccount(operatorKey);
const attacker = privateKeyToAccount(attackerKey);
let provider;
let publicClient;
let operatorWallet;
let attackerWallet;
let testClient;
let artifact;
let address;

before(async () => {
  provider = ganache.provider({
    chain: {chainId: chain.id},
    logging: {quiet: true},
    wallet: {accounts: [
      {secretKey: operatorKey, balance: `0x${(10n ** 20n).toString(16)}`},
      {secretKey: attackerKey, balance: `0x${(10n ** 20n).toString(16)}`},
    ]},
  });
  const transport = custom(provider);
  publicClient = createPublicClient({chain, transport});
  operatorWallet = createWalletClient({account: operator, chain, transport});
  attackerWallet = createWalletClient({account: attacker, chain, transport});
  testClient = createTestClient({chain, mode: 'ganache', transport});
  artifact = compile();
  const hash = await operatorWallet.deployContract({abi: artifact.abi, bytecode: artifact.bytecode, args: [operator.address]});
  ({contractAddress: address} = await publicClient.waitForTransactionReceipt({hash}));
  assert.ok(address);
});

after(async () => {
  await provider.disconnect();
});

async function anchor(root) {
  const hash = await operatorWallet.writeContract({address, abi: artifact.abi, functionName: 'anchor', args: [root]});
  return publicClient.waitForTransactionReceipt({hash});
}

test('constructor stores an immutable nonzero operator', async () => {
  assert.equal(await publicClient.readContract({address, abi: artifact.abi, functionName: 'operator'}), getAddress(operator.address));
  await assert.rejects(
    operatorWallet.deployContract({abi: artifact.abi, bytecode: artifact.bytecode, args: [zeroAddress]}),
  );
});

test('only the configured Worker operator can anchor', async () => {
  const root = `0x${'31'.repeat(32)}`;
  await assert.rejects(
    attackerWallet.writeContract({address, abi: artifact.abi, functionName: 'anchor', args: [root]}),
  );
  assert.equal(await publicClient.readContract({address, abi: artifact.abi, functionName: 'isAnchored', args: [root]}), false);
});

test('rejects the malformed zero root', async () => {
  await assert.rejects(
    operatorWallet.writeContract({address, abi: artifact.abi, functionName: 'anchor', args: [`0x${'00'.repeat(32)}`]}),
  );
});

test('records provenance and emits one indexed event', async () => {
  const root = `0x${'41'.repeat(32)}`;
  const receipt = await anchor(root);
  const logs = parseEventLogs({abi: artifact.abi, logs: receipt.logs, eventName: 'Anchored'});
  assert.equal(logs.length, 1);
  assert.equal(logs[0].args.root, root);
  assert.equal(logs[0].args.operator, getAddress(operator.address));
  assert.equal(logs[0].args.blockNumber, receipt.blockNumber);
  assert.equal(await publicClient.readContract({address, abi: artifact.abi, functionName: 'isAnchored', args: [root]}), true);
  assert.equal(await publicClient.readContract({address, abi: artifact.abi, functionName: 'anchoredInBlock', args: [root]}), receipt.blockNumber);
  assert.ok(await publicClient.readContract({address, abi: artifact.abi, functionName: 'anchoredAt', args: [root]}));
  assert.doesNotThrow(() => decodeEventLog({abi: artifact.abi, data: receipt.logs[0].data, topics: receipt.logs[0].topics}));
});

test('replay is an idempotent no-op preserving the first anchor', async () => {
  const root = `0x${'51'.repeat(32)}`;
  const first = await anchor(root);
  const timestamp = await publicClient.readContract({address, abi: artifact.abi, functionName: 'anchoredAt', args: [root]});
  const blockNumber = await publicClient.readContract({address, abi: artifact.abi, functionName: 'anchoredInBlock', args: [root]});
  await testClient.mine({blocks: 2});
  const second = await anchor(root);
  assert.equal(first.logs.length, 1);
  assert.equal(second.logs.length, 0);
  assert.equal(await publicClient.readContract({address, abi: artifact.abi, functionName: 'anchoredAt', args: [root]}), timestamp);
  assert.equal(await publicClient.readContract({address, abi: artifact.abi, functionName: 'anchoredInBlock', args: [root]}), blockNumber);
});
