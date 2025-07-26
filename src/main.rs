use std::fs;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use serde_json::{Value, json};
use chrono::Utc;
use tokio;

mod auth;
mod okx_executor;
mod risk_engine;
mod position_manager;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();
    
    std::env::set_var("MODE", "live");
    std::env::set_var("OKX_TESTNET", "false");
    
    let confidence_threshold = 0.75;
    
    println!("🔴 PRODUCTION HFT EXECUTOR - LIVE TRADING ONLY");
    log::info!("PRODUCTION MODE ACTIVE");
    
    let mut okx_executor = okx_executor::OkxExecutor::new().await?;
    let mut risk_engine = risk_engine::RiskEngine::new();
    let mut position_manager = position_manager::PositionManager::new();
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
                
                let confidence = match signal_data.get("confidence").and_then(|v| v.as_f64()) {
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
                
                let signal_timestamp = match signal_data.get("timestamp").and_then(|v| v.as_f64()).map(|t| t as u64) {
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
                        let best_signal = match signal_data.get("best_signal") {
                            Some(s) => s,
                            None => {
                                log::error!("❌ PRODUCTION: No best_signal found");
                                continue;
                            }
                        };
                        
                        let asset = match best_signal.get("asset").and_then(|v| v.as_str()) {
                            Some(a) => a,
                            None => {
                                log::error!("❌ PRODUCTION: No asset in signal");
                                continue;
                            }
                        };
                        
                        let entry_price = match best_signal.get("entry_price").and_then(|v| v.as_f64()) {
                            Some(p) if p > 0.0 => p,
                            _ => {
                                log::error!("❌ PRODUCTION: Invalid entry price");
                                continue;
                            }
                        };
                        
                        if position_manager.has_position(asset)? {
                            log::warn!("❌ PRODUCTION: Position already exists for {}", asset);
                            continue;
                        }
                        
                        let risk_check = risk_engine.validate_trade_risk(asset, entry_price, confidence).await?;
                        
                        if !risk_check.approved {
                            log::warn!("❌ RISK: {}", risk_check.reason);
                            continue;
                        }
                        
                        log::info!("🔴 EXECUTING PRODUCTION TRADE: confidence={:.3}, age={}s", confidence, age_seconds);
                        
                        match okx_executor.execute_short_order(&signal_data).await {
                            Ok(fill_data) => {
                                log::info!("✅ PRODUCTION EXECUTION SUCCESSFUL");
                                
                                position_manager.add_position(asset, &fill_data).await?;
                                risk_engine.record_trade_result(asset, 0.0);
                                
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
                                    .map_err(|_| "Cannot read fills file")?;
                                let mut fills_array: Value = serde_json::from_str(&fills_content)
                                    .map_err(|_| "Cannot parse fills JSON")?;
                                
                                if let Some(array) = fills_array.as_array_mut() {
                                    array.push(production_fill);
                                    if array.len() > 1000 {
                                        array.drain(0..500);
                                    }
                                } else {
                                    return Err("Fills file not an array".into());
                                }
                                
                                fs::write("/tmp/fills.json", serde_json::to_string_pretty(&fills_array)?)?;
                                last_signal_timestamp = signal_timestamp;
                            }
                            Err(e) => {
                                log::error!("❌ PRODUCTION EXECUTION FAILED: {}", e);
                            }
                        }
                    } else {
                        log::warn!("❌ PRODUCTION: Signal too old ({}s)", age_seconds);
                    }
                }
            }
        }
        
        position_manager.update_positions().await?;
        let positions = position_manager.get_positions();
        risk_engine.evaluate_positions(&positions).await?;
        
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
