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
            Err(_) => return Ok(None),
        };
        
        let signal_data: Value = match serde_json::from_str(&signal_content) {
            Ok(data) => data,
            Err(_) => return Ok(None),
        };
        
        if !self.validate_signal_structure(&signal_data) {
            return Ok(None);
        }
        
        let signal_timestamp = signal_data.get("timestamp")
            .and_then(|v| v.as_f64())
            .unwrap_or(0.0) as u64;
        
        if signal_timestamp <= self.last_signal_timestamp {
            return Ok(None);
        }
        
        if !self.validate_signal_freshness(&signal_data) {
            return Ok(None);
        }
        
        self.last_signal_timestamp = signal_timestamp;
        
        log::info!("Valid signal detected: confidence={:.3}", 
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
                return false;
            }
        }
        
        let confidence = signal.get("confidence").and_then(|v| v.as_f64());
        if confidence.is_none() || confidence.unwrap() < 0.0 || confidence.unwrap() > 1.0 {
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
                return false;
            }
        }
        
        let asset = best_signal.get("asset").and_then(|v| v.as_str());
        if asset.is_none() || asset.unwrap().is_empty() {
            return false;
        }
        
        let entry_price = best_signal.get("entry_price").and_then(|v| v.as_f64());
        if entry_price.is_none() || entry_price.unwrap() <= 0.0 {
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
            log::warn!("Signal too old: {} seconds", age_seconds);
            return false;
        }
        
        true
    }
}
