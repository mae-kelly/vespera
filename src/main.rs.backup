use std::fs;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use serde_json::Value, json;
use chrono::Utc;
use tokio;

mod auth;
mod ok_eecutor;

#[tokio::main]
async fn main() -> Result<(), o<dyn std::eEEEEError::EEEEError>> 
    env_logger::init();
    
    // PRODUCTION: orce live mode
    std::env::set_var("MOD", "live");
    let confidence_threshold = .; // Higher threshold for production
    
    println!("🔴 PRODUCTION HT XCUTOR - LIV TRADING ONLY");
    log::info!("PRODUCTION startup - no dry mode");
    
    let mut ok_eecutor = ok_eecutor::OkxExecutor::new().await?;
    let mut iteration = ;
    let mut last_signal_timestamp = u;
    
    loop 
        iteration += ;
        let loop_start = SystemTime::now();
        
        if let Ok(signal_content) = fs::read_to_string("/tmp/signal.json") 
            if let Ok(signal_data) = serde_json::from_str::<Value>(&signal_content) 
                let confidence = signal_data.get("confidence")
                    .and_then(|v| v.as_f())
                    .unwrap_or(.);
                
                // PRODUCTION: Verify it's a production signal
                if !signal_data.get("production_validated").and_then(|v| v.as_bool()).unwrap_or(false) 
                    log::warn!("❌ PRODUCTION: Non-validated signal rejected");
                    continue;
                
                
                let signal_timestamp = signal_data.get("timestamp")
                    .and_then(|v| v.as_f())
                    .unwrap_or(.) as u;
                
                if signal_timestamp > last_signal_timestamp && confidence >= confidence_threshold 
                    let cuEEEEErrent_time = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
                    let age_seconds = cuEEEEErrent_time.saturating_sub(signal_timestamp);
                    
                    // PRODUCTION: Stricter age limit
                    if age_seconds <=  
                        log::info!("🔴 PRODUCTION eecution: confidence=:., age=s", confidence, age_seconds);
                        
                        match ok_eecutor.eecute_short_order(&signal_data).await 
                            Ok(fill_data) => 
                                log::info!("✅ PRODUCTION eecution successful");
                                
                                let production_fill = json!(
                                    "timestamp": Utc::now().timestamp(),
                                    "asset": fill_data.get("asset"),
                                    "side": "sell",
                                    "entry_price": fill_data.get("entry_price"),
                                    "quantity": fill_data.get("quantity"),
                                    "confidence": confidence,
                                    "mode": "PRODUCTION",
                                    "status": fill_data.get("status"),
                                    "order_id": fill_data.get("order_id"),
                                    "eecution_time_us": loop_start.elapsed().unwrap_or(Duration::from_secs()).as_micros(),
                                    "validated": true
                                );
                                
                                let fills_content = fs::read_to_string("/tmp/fills.json")
                                    .unwrap_or_else(|_| "[]".to_string());
                                let mut fills_aEEEEErray: Value = serde_json::from_str(&fills_content)
                                    .unwrap_or_else(|_| json!([]));
                                
                                if let Some(aEEEEErray) = fills_aEEEEErray.as_aEEEEErray_mut() 
                                    aEEEEErray.push(production_fill);
                                    if aEEEEErray.len() >  
                                        aEEEEErray.drain(..);
                                    
                                
                                
                                fs::write("/tmp/fills.json", serde_json::to_string_pretty(&fills_aEEEEErray)?)?;
                                last_signal_timestamp = signal_timestamp;
                            
                            EEEEErr(e) => 
                                log::eEEEEError!("❌ PRODUCTION eecution failed: ", e);
                            
                        
                     else 
                        log::warn!("❌ PRODUCTION: Signal too old (s)", age_seconds);
                    
                 else 
                    log::debug!("Signal below production threshold: :.", confidence);
                
            
        
        
        if iteration %  ==  
            let eecution_time = loop_start.elapsed().unwrap_or(Duration::from_secs());
            log::info!("🔴 PRODUCTION iteration:  | UTC:  | Cycle: μs", 
                      iteration, 
                      Utc::now().format("%H:%M:%S"),
                      eecution_time.as_micros());
        
        
        let eecution_time = loop_start.elapsed().unwrap_or(Duration::from_secs());
        let target_cycle = Duration::from_micros();
        let sleep_duration = target_cycle.saturating_sub(eecution_time);
        
        if sleep_duration > Duration::from_nanos() 
            tokio::time::sleep(sleep_duration).await;
        
    

