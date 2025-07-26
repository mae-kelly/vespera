use std::collections::HashMap;
use ring::hmac;
use base64::Engine as Base64Engine;
use base64;
use {chrono::{DateTime, Utc}};

pub struct AuthManager {
    api_key: String,
    secret_key: String,
    passphrase: String,
}

impl AuthManager {
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        dotenv::dotenv().ok();
        
        let api_key = std::env::var("OKX_API_KEY")
            .map_err(|_| "OKX_API_KEY environment variable required")?;
        let secret_key = std::env::var("OKX_SECRET_KEY")
            .map_err(|_| "OKX_SECRET_KEY environment variable required")?;
        let passphrase = std::env::var("OKX_PASSPHRASE")
            .map_err(|_| "OKX_PASSPHRASE environment variable required")?;
        
        if api_key.is_empty() || secret_key.is_empty() || passphrase.is_empty() {
            return Err("All OKX credentials must be non-empty".into());
        }
        
        Ok(AuthManager {
            api_key,
            secret_key,
            passphrase,
        })
    }
    
    pub fn create_signed_headers(&self, method: &str, request_path: &str, body: &str) -> Result<HashMap<String, String>, Box<dyn std::error::Error>> {
        let timestamp = self.get_iso_timestamp();
        let message = format!("{}{}{}{}", timestamp, method, request_path, body);
        let signature = self.create_signature(&message)?;
        
        let mut headers = HashMap::new();
        headers.insert("OK-ACCESS-KEY".to_string(), self.api_key.clone());
        headers.insert("OK-ACCESS-SIGN".to_string(), signature);
        headers.insert("OK-ACCESS-TIMESTAMP".to_string(), timestamp);
        headers.insert("OK-ACCESS-PASSPHRASE".to_string(), self.passphrase.clone());
        headers.insert("Content-Type".to_string(), "application/json".to_string());
        
        Ok(headers)
    }
    
    fn create_signature(&self, message: &str) -> Result<String, Box<dyn std::error::Error>> {
        let secret_bytes = base64::engine::general_purpose::STANDARD.decode(&self.secret_key)?;
        let key = hmac::Key::new(hmac::HMAC_SHA256, &secret_bytes);
        let signature = hmac::sign(&key, message.as_bytes());
        Ok(base64::engine::general_purpose::STANDARD.encode(signature.as_ref()))
    }
    
    fn get_iso_timestamp(&self) -> String {
        let now: DateTime<Utc> = Utc::now();
        now.format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string()
    }
}
