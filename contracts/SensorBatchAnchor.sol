// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title SensorBatchAnchor
/// @notice Off-chain tutulan IoT verilerinin batch hash'lerini Monad testnet üzerinde saklar.
contract SensorBatchAnchor {
    struct Batch {
        uint256 startTs;
        uint256 endTs;
        uint256 recordCount;
        bytes32 batchHash;
        uint256 anchoredAt;
        address submitter;
    }

    Batch[] public batches;

    event BatchAnchored(
        uint256 indexed batchId,
        uint256 startTs,
        uint256 endTs,
        uint256 recordCount,
        bytes32 batchHash,
        address indexed submitter
    );

    function anchorBatch(
        uint256 startTs,
        uint256 endTs,
        uint256 recordCount,
        bytes32 batchHash
    ) external returns (uint256 batchId) {
        require(endTs >= startTs, "invalid range");
        require(recordCount > 0, "recordCount=0");
        require(batchHash != bytes32(0), "empty hash");

        batchId = batches.length;
        batches.push(
            Batch({
                startTs: startTs,
                endTs: endTs,
                recordCount: recordCount,
                batchHash: batchHash,
                anchoredAt: block.timestamp,
                submitter: msg.sender
            })
        );

        emit BatchAnchored(batchId, startTs, endTs, recordCount, batchHash, msg.sender);
    }

    function getBatch(uint256 batchId) external view returns (Batch memory) {
        return batches[batchId];
    }
}
