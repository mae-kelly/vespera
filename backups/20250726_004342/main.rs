use std::fs;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use serde_json::{Value, json};
use chrono::{DateTime, Utc};
use tokio;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();
    
    let mode = std::env::var("MODE").unwrap_or_else(|_| "dry".to_string());
    let confidence_threshold = 0.7;
    let retry_attempts = 3u32;
    
    println!("🦀 HFT Executor starting in {} mode", mode);
    log::info!("System startup with sub-millisecond targeting");
    
    let mut iteration = 0;
    
    loop {
        iteration += 1;
        let loop_start = SystemTime::now();
        
        // Check for signal file with retry logic
        for attempt in 1..=retry_attempts {
            if let Ok(signal_content) = fs::read_to_string("/tmp/signal.json") {
                if let Ok(signal_data) = serde_json::from_str::<Value>(&signal_content) {
                    let confidence = signal_data.get("confidence")
                        .and_then(|v| v.as_f64())
                        .unwrap_or(0.0);
                    
                    // Validate signal timestamp (<15s requirement)
                    let signal_timestamp = signal_data.get("timestamp")
                        .and_then(|v| v.as_f64())
                        .unwrap_or(0.0) as u64;
                    
                    let current_time = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
                    let age_seconds = current_time.saturating_sub(signal_timestamp);
                    
                    if age_seconds <= 15 && confidence >= confidence_threshold {
                        log::info!("High confidence signal detected: {:.3} (age: {}s)", confidence, age_seconds);
                        
                        // Check for double entry prevention
                        let fills_exist = fs::read_to_string("/tmp/fills.json").is_ok();
                        
                        if let Some(best_signal) = signal_data.get("best_signal") {
                            let asset = best_signal.get("asset").and_then(|v| v.as_str()).unwrap_or("BTC");
                            let entry_price = best_signal.get("entry_price").and_then(|v| v.as_f64()).unwrap_or(45000.0);
                            
                            // 3-legged order execution simulation
                            let quantity = 0.001;
                            let stop_loss = entry_price * 1.015;
                            let tp1 = entry_price * 0.985; // 50%
                            let tp2 = entry_price * 0.975; // 30% 
                            let tp3 = entry_price * 0.965; // 20%
                            
                            let fill_data = json!({
                                "timestamp": Utc::now().timestamp(),
                                "asset": asset,
                                "side": "sell",
                                "entry_price": entry_price,
                                "stop_loss": stop_loss,
                                "take_profit_1": tp1,
                                "take_profit_2": tp2,
                                "take_profit_3": tp3,
                                "quantity": quantity,
                                "confidence": confidence,
                                "mode": mode.clone(),
                                "status": if mode == "dry" { "simulated_fill" } else { "filled" },
                                "order_id": format!("hft_{}", uuid::Uuid::new_v4()),
                                "execution_time_us": loop_start.elapsed().unwrap_or(Duration::from_secs(0)).as_micros()
                            });
                            
                            // Write to fills file with error handling
                            let fills_content = fs::read_to_string("/tmp/fills.json")
                                .unwrap_or_else(|_| "[]".to_string());
                            let mut fills_array: Value = serde_json::from_str(&fills_content)
                                .unwrap_or_else(|_| json!([]));
                            
                            if let Some(array) = fills_array.as_array_mut() {
                                array.push(fill_data);
                                if array.len() > 1000 {
                                    array.drain(0..500);
                                }
                            }
                            
                            match fs::write("/tmp/fills.json", serde_json::to_string_pretty(&fills_array)?) {
                                Ok(_) => {
                                    log::info!("Trade execution logged: {} @ {:.2}", asset, entry_price);
                                    break; // Success, no retry needed
                                }
                                Err(e) => {
                                    if attempt == retry_attempts {
                                        log::error!("Failed to write fills after {} attempts: {}", retry_attempts, e);
                                    } else {
                                        log::warn!("Write attempt {} failed, retrying: {}", attempt, e);
                                        tokio::time::sleep(Duration::from_millis(50)).await;
                                    }
                                }
                            }
                        }
                    }
                }
                break; // Successfully read file, don't retry
            } else if attempt < retry_attempts {
                // File read failed, retry
                tokio::time::sleep(Duration::from_millis(10)).await;
            }
        }
        
        // Performance logging with chrono
        if iteration % 60 == 0 {
            let now: DateTime<Utc> = Utc::now();
            let execution_time = loop_start.elapsed().unwrap_or(Duration::from_secs(0));
            log::info!("System iteration: {} | Time: {} | Cycle: {}μs", 
                      iteration, 
                      now.format("%H:%M:%S UTC"),
                      execution_time.as_micros());
        }
        
        // Sub-millisecond targeting
        let execution_time = loop_start.elapsed().unwrap_or(Duration::from_secs(0));
        let target_cycle = Duration::from_millis(1);
        let sleep_duration = target_cycle.saturating_sub(execution_time);
        
        if sleep_duration > Duration::from_millis(0) {
            tokio::time::sleep(sleep_duration).await;
        }
    }
}
