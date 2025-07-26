use std::fs;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use serde_json::{Value, json};
use tokio;

#[tokio::main] 
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();
    
    let mode = std::env::var("MODE").unwrap_or_else(|_| "dry".to_string());
    println!("🦀 Minimal Rust HFT Executor starting in {} mode", mode);
    
    let mut iteration = 0;
    
    loop {
        iteration += 1;
        
        // Check for signal file
        if let Ok(signal_content) = fs::read_to_string("/tmp/signal.json") {
            if let Ok(signal_data) = serde_json::from_str::<Value>(&signal_content) {
                let confidence = signal_data.get("confidence")
                    .and_then(|v| v.as_f64())
                    .unwrap_or(0.0);
                
                if confidence > 0.7 {
                    log::info!("High confidence signal detected: {:.3}", confidence);
                    
                    // Simulate trade execution in dry mode
                    let fill_data = json!({
                        "timestamp": SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs(),
                        "asset": signal_data.get("best_signal").and_then(|s| s.get("asset")).unwrap_or(&json!("BTC")),
                        "side": "sell",
                        "entry_price": signal_data.get("best_signal").and_then(|s| s.get("entry_price")).unwrap_or(&json!(45000)),
                        "quantity": 0.001,
                        "confidence": confidence,
                        "mode": mode.clone(),
                        "status": if mode == "dry" { "simulated" } else { "filled" }
                    });
                    
                    // Write to fills file
                    let fills_content = fs::read_to_string("/tmp/fills.json")
                        .unwrap_or_else(|_| "[]".to_string());
                    let mut fills_array: Value = serde_json::from_str(&fills_content)
                        .unwrap_or_else(|_| json!([]));
                    
                    if let Some(array) = fills_array.as_array_mut() {
                        array.push(fill_data);
                        if array.len() > 100 {
                            array.drain(0..50);
                        }
                    }
                    
                    fs::write("/tmp/fills.json", serde_json::to_string_pretty(&fills_array)?)?;
                    log::info!("Trade execution logged");
                }
            }
        }
        
        if iteration % 30 == 0 {
            log::info!("Rust executor iteration: {}", iteration);
        }
        
        tokio::time::sleep(Duration::from_secs(1)).await;
    }
}
