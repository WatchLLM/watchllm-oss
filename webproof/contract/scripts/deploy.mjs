import {createPublicClient, createWalletClient, http, isAddress, zeroAddress} from 'viem';
import {base, baseSepolia} from 'viem/chains';
import {privateKeyToAccount} from 'viem/accounts';
import {compile} from './lib.mjs';

const network = process.env.CHAIN;
const chain = network === 'base-sepolia' ? baseSepolia : network === 'base-mainnet' ? base : undefined;
if (!chain) throw new Error('CHAIN must be base-sepolia or base-mainnet');
const rpcUrl = process.env.RPC_URL;
if (!rpcUrl) throw new Error('RPC_URL is required');
const privateKey = process.env.DEPLOYER_PRIVATE_KEY;
if (!/^0x[0-9a-fA-F]{64}$/.test(privateKey ?? '')) throw new Error('DEPLOYER_PRIVATE_KEY must be a 32-byte hex private key');
const operator = process.env.OPERATOR_ADDRESS;
if (!isAddress(operator ?? '') || operator === zeroAddress) throw new Error('OPERATOR_ADDRESS must be a nonzero EVM address');
if (network === 'base-mainnet' && process.env.CONFIRM_MAINNET_DEPLOY !== 'YES') {
  throw new Error('set CONFIRM_MAINNET_DEPLOY=YES after deployment review');
}

const account = privateKeyToAccount(privateKey);
const transport = http(rpcUrl, {timeout: 15_000, retryCount: 0});
const publicClient = createPublicClient({chain, transport});
const walletClient = createWalletClient({account, chain, transport});
const remoteChainId = await publicClient.getChainId();
if (remoteChainId !== chain.id) throw new Error(`RPC chain id ${remoteChainId} does not match ${chain.id}`);
const {abi, bytecode} = compile();
const hash = await walletClient.deployContract({abi, bytecode, args: [operator]});
console.log(`deployment transaction: ${hash}`);
const receipt = await publicClient.waitForTransactionReceipt({hash, confirmations: 2, timeout: 180_000});
if (receipt.status !== 'success' || !receipt.contractAddress) throw new Error('contract deployment reverted or returned no address');
const configuredOperator = await publicClient.readContract({address: receipt.contractAddress, abi, functionName: 'operator'});
if (configuredOperator.toLowerCase() !== operator.toLowerCase()) throw new Error('deployed operator verification failed');
console.log(`WebProofAnchor: ${receipt.contractAddress}`);
console.log(`operator: ${configuredOperator}`);
console.log('Review the verified address before setting ANCHOR_CONTRACT_ADDRESS.');
