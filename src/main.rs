use std::fs;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use serde_json::{Value, json};
use chrono::{DateTime, Utc};
use tokio;

mod auth;
mod okx_executor;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();
    
    let mode = std::env::var("MODE").unwrap_or_else(|_| "dry".to_string());
    let confidence_threshold = 0.7;
    let retry_attempts = 3u32;
    
    println!("🦀 HFT Executor starting in {} mode (OKX-ONLY)", mode);
    log::info!("OKX-focused execution with sub-millisecond targeting");
    
    // Initialize OKX executor
    let mut okx_executor = okx_executor::OkxExecutor::new().await?;
    
    let mut iteration = 0;
    let mut last_signal_timestamp = 0u64;
    
    loop {
        iteration += 1;
        let loop_start = SystemTime::now();
        
        // Check for high-quality signals with retry logic
        for attempt in 1..=retry_attempts {
            if let Ok(signal_content) = fs::read_to_string("/tmp/signal.json") {
                if let Ok(signal_data) = serde_json::from_str::<Value>(&signal_content) {
                    let confidence = signal_data.get("confidence")
                        .and_then(|v| v.as_f64())
                        .unwrap_or(0.0);
                    
                    let signal_timestamp = signal_data.get("timestamp")
                        .and_then(|v| v.as_f64())
                        .unwrap_or(0.0) as u64;
                    
                    // Avoid processing same signal twice
                    if signal_timestamp <= last_signal_timestamp {
                        break;
                    }
                    
                    // Validate signal freshness (<15s requirement)
                    let current_time = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
                    let age_seconds = current_time.saturating_sub(signal_timestamp);
                    
                    // Process high-confidence, fresh signals
                    if age_seconds <= 15 && confidence >= confidence_threshold {
                        log::info!("🎯 High confidence signal: {:.3} (age: {}s)", confidence, age_seconds);
                        
                        // Check multi-feed health
                        let feed_health = signal_data.get("best_signal")
                            .and_then(|s| s.get("feed_health"))
                            .and_then(|h| h.get("active_feeds"))
                            .and_then(|f| f.as_u64())
                            .unwrap_or(0);
                        
                        if feed_health >= 2 {
                            log::info!("📡 Multi-feed confirmation: {} active feeds", feed_health);
                            
                            // Execute on OKX with enhanced logic
                            match okx_executor.execute_short_order(&signal_data).await {
                                Ok(fill_data) => {
                                    log::info!("✅ OKX execution successful: {}", 
                                             fill_data.get("asset").and_then(|v| v.as_str()).unwrap_or("Unknown"));
                                    
                                    // Write fills with enhanced metadata
                                    let enhanced_fill = json!({
                                        "timestamp": Utc::now().timestamp(),
                                        "asset": fill_data.get("asset"),
                                        "side": "sell",
                                        "entry_price": fill_data.get("entry_price"),
                                        "stop_loss": fill_data.get("stop_loss"),
                                        "take_profit_1": fill_data.get("take_profit_1"),
                                        "take_profit_2": fill_data.get("take_profit_2"),
                                        "take_profit_3": fill_data.get("take_profit_3"),
                                        "quantity": fill_data.get("quantity"),
                                        "confidence": confidence,
                                        "mode": mode.clone(),
                                        "status": fill_data.get("status"),
                                        "order_id": fill_data.get("order_id"),
                                        "execution_time_us": loop_start.elapsed().unwrap_or(Duration::from_secs(0)).as_micros(),
                                        "feed_sources": signal_data.get("best_signal")
                                            .and_then(|s| s.get("feed_sources")),
                                        "feed_health": feed_health,
                                        "exchange": "OKX"
                                    });
                                    
                                    // Update fills file
                                    let fills_content = fs::read_to_string("/tmp/fills.json")
                                        .unwrap_or_else(|_| "[]".to_string());
                                    let mut fills_array: Value = serde_json::from_str(&fills_content)
                                        .unwrap_or_else(|_| json!([]));
                                    
                                    if let Some(array) = fills_array.as_array_mut() {
                                        array.push(enhanced_fill);
                                        if array.len() > 1000 {
                                            array.drain(0..500);
                                        }
                                    }
                                    
                                    fs::write("/tmp/fills.json", serde_json::to_string_pretty(&fills_array)?)?;
                                    
                                    last_signal_timestamp = signal_timestamp;
                                }
                                Err(e) => {
                                    log::error!("❌ OKX execution failed: {}", e);
                                }
                            }
                        } else {
                            log::warn!("⚠️ Insufficient feed redundancy: {} feeds", feed_health);
                        }
                    }
                }
                break; // Successfully read file
            } else if attempt < retry_attempts {
                tokio::time::sleep(Duration::from_millis(10)).await;
            }
        }
        
        // Enhanced performance logging
        if iteration % 60 == 0 {
            let now: DateTime<Utc> = Utc::now();
            let execution_time = loop_start.elapsed().unwrap_or(Duration::from_secs(0));
            log::info!("🚀 OKX System | Iteration: {} | Time: {} | Cycle: {}μs", 
                      iteration, 
                      now.format("%H:%M:%S UTC"),
                      execution_time.as_micros());
        }
        
        // Sub-millisecond targeting with adaptive sleep
        let execution_time = loop_start.elapsed().unwrap_or(Duration::from_secs(0));
        let target_cycle = Duration::from_micros(500); // Target 500μs cycles
        let sleep_duration = target_cycle.saturating_sub(execution_time);
        
        if sleep_duration > Duration::from_millis(0) {
            tokio::time::sleep(sleep_duration).await;
        }
    }
}
