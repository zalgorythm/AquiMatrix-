/**
 * javascript_sdk.js
 *
 * Provides a JavaScript SDK for interacting with AquiMatrix.
 * Features:
 * 1. Entry Creation: Helper functions to build entries.
 * 2. Submission: Sends entries to REST API.
 * 3. Querying: Fetches state and entries.
 * 4. Authentication: Manages keys and signing.
 */

class AquiMatrixClient {
  constructor(apiUrl = "http://localhost:9000") {
    this.apiUrl = apiUrl;
  }

  async submitEntry(entry) {
    const response = await fetch(`${this.apiUrl}/entries`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entry),
    });
    if (!response.ok) {
      throw new Error(`Failed to submit entry: ${response.statusText}`);
    }
    return await response.json();
  }

  async getState(address) {
    const response = await fetch(`${this.apiUrl}/state/${address}`);
    if (!response.ok) {
      throw new Error(`Failed to get state: ${response.statusText}`);
    }
    return await response.json();
  }

  async getEntry(entryHash) {
    const response = await fetch(`${this.apiUrl}/entries/${entryHash}`);
    if (!response.ok) {
      throw new Error(`Failed to get entry: ${response.statusText}`);
    }
    return await response.json();
  }

  // Placeholder for key management and signing
  createEntry(transactionData, predecessorHashes, timestamp, publicKey, signature) {
    return {
      transaction_data: transactionData,
      predecessor_hashes: predecessorHashes,
      timestamp: timestamp,
      submitter_public_key: publicKey,
      signature: signature,
      hash: this.computeHash(transactionData, predecessorHashes, timestamp, publicKey),
    };
  }

  computeHash(transactionData, predecessorHashes, timestamp, publicKey) {
    // Placeholder for hash computation
    return "hash_placeholder";
  }
}

export default AquiMatrixClient;
