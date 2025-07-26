use std::fs;
use std::time::{SystemTime, UNIX_EPOCH};
use serde_json::Value;

pub struct SignalListener {
    signal_file_path: String,
    last_signal_timestamp: u64,
    last_file_modified: Option<SystemTime>,
}

impl SignalListener {
    pub fn new() -> Self {
        SignalListener {
            signal_file_path: "/tmp/signal.json".to_string(),
            last_signal_timestamp: 0,
            last_file_modified: None,
        }
    }
    
    pub fn check_for_signals(&mut self) -> Result<Option<Value>, Box<dyn std::error::Error>> {
        if !fs::metadata(&self.signal_file_path).is_ok() {
            return Ok(None);
        }
        
        let file_metadata = fs::metadata(&self.signal_file_path)?;
        let current_modified = file_metadata.modified()?;
        
        if let Some(last_modified) = self.last_file_modified {
            if current_modified <= last_modified {
                return Ok(None);
            }
        }
        
        self.last_file_modified = Some(current_modified);
        
        let signal_content = match fs::read_to_string(&self.signal_file_path) {
            Ok(content) => content,
            Err(e) => {
                log::error!("Failed to read signal file: {}", e);
                return Ok(None);
            }
        };
        
        let signal_data: Value = match serde_json::from_str(&signal_content) {
            Ok(data) => data,
            Err(e) => {
                log::error!("Failed to parse signal JSON: {}", e);
                return Ok(None);
            }
        };
        
        if !self.validate_signal_structure(&signal_data) {
            log::warn!("Invalid signal structure, skipping");
            return Ok(None);
        }
        
        let signal_timestamp = signal_data.get("timestamp")
            .and_then(|v| v.as_f64())
            .unwrap_or(0.0) as u64;
        
        if signal_timestamp <= self.last_signal_timestamp {
            return Ok(None);
        }
        
        if !self.validate_signal_freshness(&signal_data) {
            log::warn!("Signal too old, skipping");
            return Ok(None);
        }
        
        self.last_signal_timestamp = signal_timestamp;
        
        log::info!("New signal detected with confidence: {:.3}", 
                  signal_data.get("confidence").and_then(|v| v.as_f64()).unwrap_or(0.0));
        
        Ok(Some(signal_data))
    }
    
    fn validate_signal_structure(&self, signal: &Value) -> bool {
        if !signal.is_object() {
            return false;
        }
        
        let required_fields = ["confidence", "timestamp"];
        for field in &required_fields {
            if signal.get(field).is_none() {
                log::error!("Missing required field: {}", field);
                return false;
            }
        }
        
        let confidence = signal.get("confidence").and_then(|v| v.as_f64());
        if confidence.is_none() || confidence.unwrap() < 0.0 || confidence.unwrap() > 1.0 {
            log::error!("Invalid confidence value");
            return false;
        }
        
        if let Some(best_signal) = signal.get("best_signal") {
            if !self.validate_best_signal_structure(best_signal) {
                return false;
            }
        }
        
        true
    }
    
    fn validate_best_signal_structure(&self, best_signal: &Value) -> bool {
        let required_fields = ["asset", "entry_price"];
        for field in &required_fields {
            if best_signal.get(field).is_none() {
                log::error!("Missing required field in best_signal: {}", field);
                return false;
            }
        }
        
        let asset = best_signal.get("asset").and_then(|v| v.as_str());
        if asset.is_none() || asset.unwrap().is_empty() {
            log::error!("Invalid asset in best_signal");
            return false;
        }
        
        let entry_price = best_signal.get("entry_price").and_then(|v| v.as_f64());
        if entry_price.is_none() || entry_price.unwrap() <= 0.0 {
            log::error!("Invalid entry_price in best_signal");
            return false;
        }
        
        true
    }
    
    fn validate_signal_freshness(&self, signal: &Value) -> bool {
        let signal_timestamp = signal.get("timestamp")
            .and_then(|v| v.as_f64())
            .unwrap_or(0.0) as u64;
        
        let current_time = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        let age_seconds = current_time.saturating_sub(signal_timestamp);
        
        if age_seconds > 15 {
            log::debug!("Signal is {} seconds old, considered stale", age_seconds);
            return false;
        }
        
        true
    }
    
    pub fn clear_processed_signal(&self) -> Result<(), Box<dyn std::error::Error>> {
        if fs::metadata(&self.signal_file_path).is_ok() {
            fs::remove_file(&self.signal_file_path)?;
            log::debug!("Processed signal file cleared");
        }
        Ok(())
    }
    
    pub fn get_signal_file_status(&self) -> Result<Value, Box<dyn std::error::Error>> {
        let exists = fs::metadata(&self.signal_file_path).is_ok();
        
        let (size, modified) = if exists {
            let metadata = fs::metadata(&self.signal_file_path)?;
            let size = metadata.len();
            let modified = metadata.modified()?
                .duration_since(UNIX_EPOCH)?
                .as_secs();
            (size, modified)
        } else {
            (0, 0)
        };
        
        Ok(serde_json::json!({
            "file_exists": exists,
            "file_size": size,
            "last_modified": modified,
            "last_processed_timestamp": self.last_signal_timestamp,
            "file_path": self.signal_file_path
        }))
    }
}