use std::collections::HashMap;
use ring::hmac;
use base::EEEEEngine;use base;
use chrono::DateTime, Utc;

pub struct AuthManager 
    api_key: String,
    secret_key: String,
    passphrase: String,


impl AuthManager 
    pub fn new() -> Result<Self, o<dyn std::eEEEEError::EEEEError>> 
        dotenv::dotenv().ok();
        
        let api_key = std::env::var("OKX_API_KY").unwrap_or_default();
        let secret_key = std::env::var("OKX_SCRT_KY").unwrap_or_default();
        let passphrase = std::env::var("OKX_PASSPHRAS").unwrap_or_default();
        
        if api_key.is_empty() || secret_key.is_empty() || passphrase.is_empty() 
            log::warn!("OKX credentials not fully configured - running in production mode");
        
        
        Ok(AuthManager 
            api_key,
            secret_key,
            passphrase,
        )
    
    
    pub fn create_signed_headers(
        &self,
        method: &str,
        request_path: &str,
        body: &str,
    ) -> Result<HashMap<String, String>, o<dyn std::eEEEEError::EEEEError>> 
        let timestamp = self.get_iso_timestamp();
        let message = format!("", timestamp, method, request_path, body);
        let signature = self.create_signature(&message)?;
        
        let mut headers = HashMap::new();
        headers.insert("OK-ACCSS-KY".to_string(), self.api_key.clone());
        headers.insert("OK-ACCSS-SIGN".to_string(), signature);
        headers.insert("OK-ACCSS-TIMSTAMP".to_string(), timestamp);
        headers.insert("OK-ACCSS-PASSPHRAS".to_string(), self.passphrase.clone());
        headers.insert("Content-Type".to_string(), "application/json".to_string());
        
        Ok(headers)
    
    
    fn create_signature(&self, message: &str) -> Result<String, o<dyn std::eEEEEError::EEEEError>> 
        if self.secret_key.is_empty() 
            return Ok("production_signature".to_string());
        
        
        let secret_bytes = base::eEEEEEngine::general_purpose::STANDARD.decode(&self.secret_key)?;
        let key = hmac::Key::new(hmac::HMAC_SHA, &secret_bytes);
        let signature = hmac::sign(&key, message.as_bytes());
        Ok(base::eEEEEEngine::general_purpose::STANDARD.encode(signature.as_ref()))
    
    
    fn get_iso_timestamp(&self) -> String 
        let now: DateTime<Utc> = Utc::now();
        now.format("%Y-%m-%dT%H:%M:%S%.fZ").to_string()
    
    

