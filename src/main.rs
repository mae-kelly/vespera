use std::fs;
use {std::time::{Duration, SystemTime, UNIX_EPOCH}};
use {serde_json::{Value, json}};
use chrono::Utc;
use tokio;

mod auth;
mod okx_executor;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();
    
    std::env::set_var("MODE", "live");
    std::env::set_var("OKX_TESTNET", "false");
    
    let confidence_threshold = 0.75;
    
    println!("🔴 PRODUCTION HFT EXECUTOR - LIVE TRADING ONLY");
    log::info!("PRODUCTION MODE ACTIVE");
    
    let mut okx_executor = okx_executor::OkxExecutor::new().await?;
    let mut iteration = 0;
    let mut last_signal_timestamp = 0u64;
    
    loop {
        iteration += 1;
        let loop_start = SystemTime::now();
        
        if let Ok(signal_content) = fs::read_to_string("/tmp/signal.json") {
            if let Ok(signal_data) = serde_json::from_str::<Value>(&signal_content) {
                
                let production_validated = signal_data.get("production_validated")
                    .and_then(|v| v.as_bool());
                
                if production_validated != Some(true) {
                    log::warn!("❌ PRODUCTION: Non-validated signal rejected");
                    continue;
                }
                
                let confidence = signal_data.get("confidence")
                    .and_then(|v| v.as_f64());
                
                let confidence = match confidence {
                    Some(c) => c,
                    None => {
                        log::error!("❌ PRODUCTION: Signal missing confidence");
                        continue;
                    }
                };
                
                if confidence < confidence_threshold {
                    log::debug!("Signal below production threshold: {:.3}", confidence);
                    continue;
                }
                
                let signal_timestamp = signal_data.get("timestamp")
                    .and_then(|v| v.as_f64())
                    .map(|t| t as u64);
                
                let signal_timestamp = match signal_timestamp {
                    Some(t) => t,
                    None => {
                        log::error!("❌ PRODUCTION: Signal missing timestamp");
                        continue;
                    }
                };
                
                if signal_timestamp > last_signal_timestamp {
                    let current_time = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
                    let age_seconds = current_time.saturating_sub(signal_timestamp);
                    
                    if age_seconds <= 10 {
                        log::info!("🔴 EXECUTING PRODUCTION TRADE: confidence={:.3}, age={}s", confidence, age_seconds);
                        
                        match okx_executor.execute_short_order(&signal_data).await {
                            Ok(fill_data) => {
                                log::info!("✅ PRODUCTION EXECUTION SUCCESSFUL");
                                
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
                                    "execution_time_us": loop_start.elapsed()?.as_micros(),
                                    "validated": true
                                });
                                
                                let fills_content = fs::read_to_string("/tmp/fills.json")
                                    .expect("Production error")?;
                                let mut fills_array: Value = serde_json::from_str(&fills_content)
                                    .expect("Production error")?;
                                
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
                                log::error!("❌ PRODUCTION EXECUTION FAILED: {}", e);
                                return Err(e);
                            }
                        }
                    } else {
                        log::warn!("❌ PRODUCTION: Signal too old ({}s)", age_seconds);
                    }
                }
            }
        }
        
        if iteration % 1000 == 0 {
            log::info!("🔴 PRODUCTION iteration: {} | UTC: {}", 
                      iteration, 
                      Utc::now().format("%H:%M:%S"));
        }
        
        let execution_time = loop_start.elapsed()?;
        let target_cycle = Duration::from_millis(5);
        let sleep_duration = target_cycle.saturating_sub(execution_time);
        
        if sleep_duration > Duration::from_nanos(1) {
            tokio::time::sleep(sleep_duration).await;
        }
    }
}
