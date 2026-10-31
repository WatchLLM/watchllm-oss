# WebProof Base anchor contract

`WebProofAnchor` is the minimal on-chain sink used by `webproof/edge`. Its exact write ABI is:

```solidity
function anchor(bytes32 root) external;
```

The immutable `operator` must be the address derived from the Worker's dedicated `EVM_PRIVATE_KEY`. Only that address can anchor. A nonzero root is recorded once with its first block and timestamp and emits `Anchored`; an authorized replay is a successful no-op. This makes queue retries and transaction replacements idempotent without allowing arbitrary accounts to add roots.

There is deliberately no owner, proxy, withdrawal path, self-destruct, or mutable operator. Key rotation and upgrades require a reviewed redeployment plus an explicit Worker configuration change. The deployer has no authority unless it is also passed as the operator. The contract accepts no ETH.

## Local verification

```bash
npm ci
npm run build
npm run check:abi
npm test
```

`check:abi` compiles Solidity and compares `anchor(bytes32)` calldata against the literal ABI in `../edge/src/chain.ts`. Tests run against an in-memory Base-compatible EVM and cover authorization, zero operator/root, storage/event provenance, and replay idempotency. Generated `artifacts/` are ignored build output.

## Reviewed deployment procedure

No deployment is performed by build or test scripts. After reviewing source, compiler version, operator derivation, network, and funded accounts:

```bash
CHAIN=base-sepolia \
RPC_URL=https://... \
DEPLOYER_PRIVATE_KEY=0x... \
OPERATOR_ADDRESS=0x... \
npm run deploy
```

Mainnet additionally requires `CONFIRM_MAINNET_DEPLOY=YES`. Use a dedicated, minimally funded Worker operator; the deployer can be separate. The script validates RPC chain ID, waits for two confirmations, and reads back the immutable operator. Independently verify source/bytecode and the resulting address before replacing the zero `ANCHOR_CONTRACT_ADDRESS` placeholder. Never commit keys or RPC credentials.
