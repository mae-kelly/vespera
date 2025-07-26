use std::fs;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use serde_json::{Value, json};
use chrono::Utc;
use tokio;

mod auth;
mod okx_executor;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();
    
    // PRODUCTION: Force live mode
    std::env::set_var("MODE", "live");
    let confidence_threshold = 0.6; // Higher threshold for production
    
    println!("🔴 PRODUCTION HFT EXECUTOR - LIVE TRADING ONLY");
    log::info!("PRODUCTION startup - no dry mode");
    
    let mut okx_executor = okx_executor::OkxExecutor::new().await?;
    let mut iteration = 0;
    let mut last_signal_timestamp = 0u64;
    
    loop {
        iteration += 1;
        let loop_start = SystemTime::now();
        
        if let Ok(signal_content) = fs::read_to_string("/tmp/signal.json") {
            if let Ok(signal_data) = serde_json::from_str::<Value>(&signal_content) {
                let confidence = signal_data.get("confidence")
                    .and_then(|v| v.as_f64())
                    .unwrap_or(0.0);
                
                // PRODUCTION: Verify it's a production signal
                if !signal_data.get("production_validated").and_then(|v| v.as_bool()).unwrap_or(false) {
                    log::warn!("❌ PRODUCTION: Non-validated signal rejected");
                    continue;
                }
                
                let signal_timestamp = signal_data.get("timestamp")
                    .and_then(|v| v.as_f64())
                    .unwrap_or(0.0) as u64;
                
                if signal_timestamp > last_signal_timestamp && confidence >= confidence_threshold {
                    let current_time = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
                    let age_seconds = current_time.saturating_sub(signal_timestamp);
                    
                    // PRODUCTION: Stricter age limit
                    if age_seconds <= 5 {
                        log::info!("🔴 PRODUCTION execution: confidence={:.3}, age={}s", confidence, age_seconds);
                        
                        match okx_executor.execute_short_order(&signal_data).await {
                            Ok(fill_data) => {
                                log::info!("✅ PRODUCTION execution successful");
                                
                                let production_fill = json!({
                                    "timestamp": Utc::now().timestamp(),
                                    "asset": fill_data.get("asset"),
                                    "side": "sell",
                                    "entry_price": fill_data.get("entry_price"),
                                    "quantity": fill_data.get("quantity"),
                                    "confidence": confidence,
                                    "mode": "PRODUCTION",
                                    "status": fill_data.get("status"),
                                    "order_id": fill_data.get("order_id"),
                                    "execution_time_us": loop_start.elapsed().unwrap_or(Duration::from_secs(0)).as_micros(),
                                    "validated": true
                                });
                                
                                let fills_content = fs::read_to_string("/tmp/fills.json")
                                    .unwrap_or_else(|_| "[]".to_string());
                                let mut fills_array: Value = serde_json::from_str(&fills_content)
                                    .unwrap_or_else(|_| json!([]));
                                
                                if let Some(array) = fills_array.as_array_mut() {
                                    array.push(production_fill);
                                    if array.len() > 1000 {
                                        array.drain(0..500);
                                    }
                                }
                                
                                fs::write("/tmp/fills.json", serde_json::to_string_pretty(&fills_array)?)?;
                                last_signal_timestamp = signal_timestamp;
                            }
                            Err(e) => {
                                log::error!("❌ PRODUCTION execution failed: {}", e);
                            }
                        }
                    } else {
                        log::warn!("❌ PRODUCTION: Signal too old ({}s)", age_seconds);
                    }
                } else {
                    log::debug!("Signal below production threshold: {:.3}", confidence);
                }
            }
        }
        
        if iteration % 30 == 0 {
            let execution_time = loop_start.elapsed().unwrap_or(Duration::from_secs(0));
            log::info!("🔴 PRODUCTION iteration: {} | UTC: {} | Cycle: {}μs", 
                      iteration, 
                      Utc::now().format("%H:%M:%S"),
                      execution_time.as_micros());
        }
        
        let execution_time = loop_start.elapsed().unwrap_or(Duration::from_secs(0));
        let target_cycle = Duration::from_micros(500);
        let sleep_duration = target_cycle.saturating_sub(execution_time);
        
        if sleep_duration > Duration::from_nanos(0) {
            tokio::time::sleep(sleep_duration).await;
        }
    }
}
