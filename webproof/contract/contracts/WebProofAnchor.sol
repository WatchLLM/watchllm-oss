// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;

/// @title WebProofAnchor
/// @notice Records the first Base block and timestamp in which a WebProof Merkle root was anchored.
/// @dev The operator is immutable: rotate it by deploying a new contract and updating the Worker.
contract WebProofAnchor {
    error Unauthorized();
    error ZeroAddress();
    error ZeroRoot();

    address public immutable operator;
    mapping(bytes32 root => bool anchored) public isAnchored;
    mapping(bytes32 root => uint64 timestamp) public anchoredAt;
    mapping(bytes32 root => uint64 blockNumber) public anchoredInBlock;

    event Anchored(bytes32 indexed root, address indexed operator, uint64 timestamp, uint64 blockNumber);

    constructor(address operator_) {
        if (operator_ == address(0)) revert ZeroAddress();
        operator = operator_;
    }

    /// @notice Anchor a nonzero Merkle root. Replays are successful no-ops.
    /// @dev Idempotency protects retries/replacements from reverting after the first confirmation.
    function anchor(bytes32 root) external {
        if (msg.sender != operator) revert Unauthorized();
        if (root == bytes32(0)) revert ZeroRoot();
        if (isAnchored[root]) return;

        uint64 timestamp = uint64(block.timestamp);
        uint64 blockNumber = uint64(block.number);
        isAnchored[root] = true;
        anchoredAt[root] = timestamp;
        anchoredInBlock[root] = blockNumber;
        emit Anchored(root, msg.sender, timestamp, blockNumber);
    }
}
