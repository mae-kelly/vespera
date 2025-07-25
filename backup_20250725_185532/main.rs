use std::fs;
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::collections::HashMap;
use serde_json::{Value, json};
use chrono::{DateTime, Utc};
use tokio;

mod okx_executor;
mod auth;
mod position_manager;
mod risk_engine;
mod signal_listener;
mod data_feed;

use okx_executor::OkxExecutor;
use position_manager::PositionManager;
use risk_engine::RiskEngine;
use signal_listener::SignalListener;
use data_feed::DataFeed;

#[derive(Debug, Clone)]
struct Config {
    mode: String,
    confidence_threshold: f64,
    retry_attempts: u32,
    min_signal_age: u64,
}

impl Default for Config {
    fn default() -> Self {
        Config {
            mode: std::env::var("MODE").unwrap_or_else(|_| "dry".to_string()),
            confidence_threshold: 0.7,
            retry_attempts: 3,
            min_signal_age: 15,
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();
    
    let config = Config::default();
    log::info!("Starting Rust execution layer in {} mode", config.mode);
    
    let mut executor = OkxExecutor::new().await?;
    let mut position_manager = PositionManager::new();
    let mut risk_engine = RiskEngine::new();
    let mut signal_listener = SignalListener::new();
    let mut data_feed = DataFeed::new().await?;
    
    data_feed.start().await?;
    
    let mut last_signal_check = SystemTime::now();
    let mut iteration = 0;
    
    loop {
        iteration += 1;
        let loop_start = SystemTime::now();
        
        if let Ok(signal_data) = signal_listener.check_for_signals() {
            if let Some(signal) = signal_data {
                log::info!("Signal received: confidence {:.3}", signal.get("confidence").unwrap_or(&json!(0.0)));
                
                if should_process_signal(&signal, &config)? {
                    match process_signal(&signal, &mut executor, &mut position_manager, &mut risk_engine, &config).await {
                        Ok(result) => {
                            log::info!("Signal processed successfully: {:?}", result);
                        }
                        Err(e) => {
                            log::error!("Signal processing failed: {}", e);
                        }
                    }
                }
            }
        }
        
        position_manager.update_positions().await?;
        risk_engine.evaluate_positions(&position_manager.get_positions()).await?;
        
        if iteration % 60 == 0 {
            log_system_status(&position_manager, &risk_engine, iteration).await?;
        }
        
        let loop_duration = loop_start.elapsed().unwrap_or(Duration::from_secs(0));
        let sleep_duration = Duration::from_millis(1000).saturating_sub(loop_duration);
        
        if sleep_duration > Duration::from_millis(0) {
            tokio::time::sleep(sleep_duration).await;
        }
    }
}

fn should_process_signal(signal: &Value, config: &Config) -> Result<bool, Box<dyn std::error::Error>> {
    let confidence = signal.get("confidence")
        .and_then(|v| v.as_f64())
        .unwrap_or(0.0);
    
    if confidence < config.confidence_threshold {
        log::debug!("Signal confidence {:.3} below threshold {:.3}", confidence, config.confidence_threshold);
        return Ok(false);
    }
    
    let timestamp = signal.get("timestamp")
        .and_then(|v| v.as_f64())
        .unwrap_or(0.0) as u64;
    
    let current_time = SystemTime::now()
        .duration_since(UNIX_EPOCH)?
        .as_secs();
    
    if current_time.saturating_sub(timestamp) > config.min_signal_age {
        log::debug!("Signal too old: {} seconds", current_time.saturating_sub(timestamp));
        return Ok(false);
    }
    
    if let Ok(fills_content) = fs::read_to_string("/tmp/fills.json") {
        if let Ok(fills_data) = serde_json::from_str::<Value>(&fills_content) {
            if let Some(recent_fills) = fills_data.as_array() {
                for fill in recent_fills {
                    if let Some(fill_timestamp) = fill.get("timestamp").and_then(|v| v.as_f64()) {
                        if current_time.saturating_sub(fill_timestamp as u64) < 300 {
                            if let (Some(signal_asset), Some(fill_asset)) = (
                                signal.get("best_signal").and_then(|s| s.get("asset")).and_then(|a| a.as_str()),
                                fill.get("asset").and_then(|a| a.as_str())
                            ) {
                                if signal_asset == fill_asset {
                                    log::debug!("Duplicate signal for {} within cooldown period", signal_asset);
                                    return Ok(false);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    Ok(true)
}

async fn process_signal(
    signal: &Value,
    executor: &mut OkxExecutor,
    position_manager: &mut PositionManager,
    risk_engine: &mut RiskEngine,
    config: &Config,
) -> Result<Value, Box<dyn std::error::Error>> {
    
    let best_signal = signal.get("best_signal")
        .ok_or("No best_signal found in signal data")?;
    
    let asset = best_signal.get("asset")
        .and_then(|v| v.as_str())
        .ok_or("No asset specified in signal")?;
    
    let entry_price = best_signal.get("entry_price")
        .and_then(|v| v.as_f64())
        .ok_or("No entry_price specified in signal")?;
    
    let confidence = signal.get("confidence")
        .and_then(|v| v.as_f64())
        .unwrap_or(0.0);
    
    if position_manager.has_position(asset)? {
        log::warn!("Position already exists for {}, skipping", asset);
        return Ok(json!({"status": "skipped", "reason": "position_exists"}));
    }
    
    let risk_check = risk_engine.validate_trade_risk(asset, entry_price, confidence).await?;
    if !risk_check.approved {
        log::warn!("Trade rejected by risk engine: {}", risk_check.reason);
        return Ok(json!({"status": "rejected", "reason": risk_check.reason}));
    }
    
    let mut retry_count = 0;
    while retry_count < config.retry_attempts {
        match executor.execute_short_order(best_signal).await {
            Ok(execution_result) => {
                position_manager.add_position(asset, &execution_result).await?;
                
                let fill_data = json!({
                    "timestamp": SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs(),
                    "asset": asset,
                    "side": "sell",
                    "entry_price": entry_price,
                    "quantity": execution_result.get("quantity").unwrap_or(&json!(0.0)),
                    "confidence": confidence,
                    "mode": config.mode,
                    "status": "filled"
                });
                
                log_fill_to_file(&fill_data).await?;
                
                return Ok(json!({
                    "status": "executed",
                    "asset": asset,
                    "execution_result": execution_result
                }));
            }
            Err(e) => {
                retry_count += 1;
                log::warn!("Execution attempt {} failed: {}", retry_count, e);
                
                if retry_count < config.retry_attempts {
                    tokio::time::sleep(Duration::from_millis(1000)).await;
                }
            }
        }
    }
    
    Err(format!("Failed to execute after {} attempts", config.retry_attempts).into())
}

async fn log_fill_to_file(fill_data: &Value) -> Result<(), Box<dyn std::error::Error>> {
    let fills_path = "/tmp/fills.json";
    
    let mut fills_array = if let Ok(content) = fs::read_to_string(fills_path) {
        serde_json::from_str::<Value>(&content)
            .unwrap_or_else(|_| json!([]))
    } else {
        json!([])
    };
    
    if let Some(array) = fills_array.as_array_mut() {
        array.push(fill_data.clone());
        
        if array.len() > 1000 {
            array.drain(0..500);
        }
    }
    
    fs::write(fills_path, serde_json::to_string_pretty(&fills_array)?)?;
    Ok(())
}

async fn log_system_status(
    position_manager: &PositionManager,
    risk_engine: &RiskEngine,
    iteration: u32,
) -> Result<(), Box<dyn std::error::Error>> {
    
    let positions = position_manager.get_positions();
    let total_pnl = positions.iter()
        .map(|p| p.get("unrealized_pnl").and_then(|v| v.as_f64()).unwrap_or(0.0))
        .sum::<f64>();
    
    log::info!(
        "System Status - Iteration: {}, Active Positions: {}, Total PnL: {:.2}",
        iteration,
        positions.len(),
        total_pnl
    );
    
    Ok(())
}