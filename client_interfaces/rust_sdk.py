"""
rust_sdk.rs

Provides a Rust SDK for interacting with AquiMatrix.
Features:
1. Entry Creation: Helper functions to build entries.
2. Submission: Sends entries to REST API.
3. Querying: Fetches state and entries.
4. Authentication: Manages keys and signing.
"""

use reqwest::blocking::Client;
use serde_json::Value;

pub struct AquiMatrixClient {
    api_url: String,
    client: Client,
}

impl AquiMatrixClient {
    pub fn new(api_url: &str) -> Self {
        AquiMatrixClient {
            api_url: api_url.to_string(),
            client: Client::new(),
        }
    }

    pub fn submit_entry(&self, entry: &Value) -> Result<Value, reqwest::Error> {
        let url = format!("{}/entries", self.api_url);
        let resp = self.client.post(&url).json(entry).send()?;
        resp.json()
    }

    pub fn get_state(&self, address: &str) -> Result<Value, reqwest::Error> {
        let url = format!("{}/state/{}", self.api_url, address);
        let resp = self.client.get(&url).send()?;
        resp.json()
    }

    pub fn get_entry(&self, entry_hash: &str) -> Result<Value, reqwest::Error> {
        let url = format!("{}/entries/{}", self.api_url, entry_hash);
        let resp = self.client.get(&url).send()?;
        resp.json()
    }

    // Placeholder for key management and signing
    pub fn create_entry(&self, transaction_data: &Value, predecessor_hashes: &[String], timestamp: u64, public_key: &str, signature: &str) -> Value {
        // Construct entry JSON
        serde_json::json!({
            "transaction_data": transaction_data,
            "predecessor_hashes": predecessor_hashes,
            "timestamp": timestamp,
            "submitter_public_key": public_key,
            "signature": signature,
            "hash": "hash_placeholder"
        })
    }
}
