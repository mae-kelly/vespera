use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};
use ring::hmac;
use base64;
use chrono::{DateTime, Utc};

pub struct AuthManager {
    api_key: String,
    secret_key: String,
    passphrase: String,
}

impl AuthManager {
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        dotenv::dotenv().ok();
        
        let api_key = std::env::var("OKX_API_KEY").unwrap_or_default();
        let secret_key = std::env::var("OKX_SECRET_KEY").unwrap_or_default();
        let passphrase = std::env::var("OKX_PASSPHRASE").unwrap_or_default();
        
        if api_key.is_empty() || secret_key.is_empty() || passphrase.is_empty() {
            log::warn!("OKX credentials not fully configured - running in simulation mode");
        }
        
        Ok(AuthManager {
            api_key,
            secret_key,
            passphrase,
        })
    }
    
    pub fn create_signed_headers(
        &self,
        method: &str,
        request_path: &str,
        body: &str,
    ) -> Result<HashMap<String, String>, Box<dyn std::error::Error>> {
        
        let timestamp = self.get_iso8601_timestamp();
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
        if self.secret_key.is_empty() {
            return Ok("simulation_signature".to_string());
        }
        
        let secret_bytes = base64::decode(&self.secret_key)?;
        let key = hmac::Key::new(hmac::HMAC_SHA256, &secret_bytes);
        let signature = hmac::sign(&key, message.as_bytes());
        
        Ok(base64::encode(signature.as_ref()))
    }
    
    fn get_iso8601_timestamp(&self) -> String {
        let now = SystemTime::now();
        let datetime: DateTime<Utc> = now.into();
        datetime.format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string()
    }
    
    pub fn is_configured(&self) -> bool {
        !self.api_key.is_empty() && !self.secret_key.is_empty() && !self.passphrase.is_empty()
    }
}