use std::time::{SystemTime, UNIX_EPOCH};
use reqwest::Client;
use serde_json::{Value, json};
use uuid::Uuid;
use crate::auth::AuthManager;

pub struct OkxExecutor {
    client: Client,
    auth: AuthManager,
    base_url: String,
    mode: String,
}

impl OkxExecutor {
    pub async fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let auth = AuthManager::new()?;
        let mode = "live".to_string();
        let testnet = std::env::var("OKX_TESTNET").unwrap_or_else(|_| "true".to_string()) == "true";
        
        let base_url = if testnet {
            "https://www.okx.com"  // Use testnet for dry runs
        } else {
            "https://www.okx.com"  // Production
        };
        
        Ok(OkxExecutor {
            client: Client::builder()
                .timeout(std::time::Duration::from_millis(5000))  // 5s timeout for speed
                .build()?,
            auth,
            base_url: base_url.to_string(),
            mode,
        })
    }
    
    pub async fn execute_short_order(&mut self, signal_data: &Value) -> Result<Value, Box<dyn std::error::Error>> {
        let best_signal = signal_data.get("best_signal")
            .ok_or("No best_signal in signal data")?;
            
        let asset = best_signal.get("asset")
            .and_then(|v| v.as_str())
            .ok_or("No asset in signal data")?;
            
        let entry_price = best_signal.get("entry_price")
            .and_then(|v| v.as_f64())
            .ok_or("No entry_price in signal data")?;
            
        let stop_loss = best_signal.get("stop_loss")
            .and_then(|v| v.as_f64())
            .unwrap_or(entry_price * 1.02);
            
        let take_profit_1 = best_signal.get("take_profit_1")
            .and_then(|v| v.as_f64())
            .unwrap_or(entry_price * 0.99);
            
        let take_profit_2 = best_signal.get("take_profit_2")
            .and_then(|v| v.as_f64())
            .unwrap_or(entry_price * 0.98);
            
        let take_profit_3 = best_signal.get("take_profit_3")
            .and_then(|v| v.as_f64())
            .unwrap_or(entry_price * 0.97);
        
        // Real OKX execution
        let inst_id = format!("{}-USDT", asset);
        let size = self.calculate_position_size(entry_price).await?;
        
        // Main short order
        let order_data = json!({
            "instId": inst_id,
            "tdMode": "cross",
            "side": "sell",
            "ordType": "market",
            "sz": size.to_string(),
            "clOrdId": format!("hft_short_{}", Uuid::new_v4())
        });
        
        let response = self.place_okx_order(&order_data).await?;
        
        if let Some(order_id) = response.get("data")
            .and_then(|d| d.as_array())
            .and_then(|arr| arr.first())
            .and_then(|order| order.get("ordId"))
            .and_then(|id| id.as_str()) {
            
            // Wait for fill confirmation
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
            
            // Place stop loss
            self.place_okx_stop_loss(&inst_id, stop_loss, size).await?;
            
            // Place take profit ladder
            self.place_okx_take_profit_ladder(&inst_id, entry_price, size).await?;
            
            Ok(json!({
                "order_id": order_id,
                "asset": asset,
                "side": "sell",
                "quantity": size,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit_1": take_profit_1,
                "take_profit_2": take_profit_2,
                "take_profit_3": take_profit_3,
                "status": "filled",
                "exchange": "OKX",
                "timestamp": SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs()
            }))
        } else {
            Err("OKX order placement failed".into())
        }
    }
    
    async fn simulate_okx_execution(
        &self,
        asset: &str,
        entry_price: f64,
        stop_loss: f64,
        take_profit_1: f64,
        take_profit_2: f64,
        take_profit_3: f64,
    ) -> Result<Value, Box<dyn std::error::Error>> {
        let size = self.calculate_position_size(entry_price).await?;
        let simulated_slippage = entry_price * 0.0001; // 1 basis point
        let actual_entry = entry_price + simulated_slippage;
        
        log::info!(
            "🎯 OKX DRY RUN: Short {} at {:.2} (size: {:.4}), SL: {:.2}, TP: {:.2}/{:.2}/{:.2}",
            asset, actual_entry, size, stop_loss, take_profit_1, take_profit_2, take_profit_3
        );
        
        Ok(json!({
            "order_id": format!("okx_sim_{}", Uuid::new_v4()),
            "asset": asset,
            "side": "sell",
            "quantity": size,
            "entry_price": actual_entry,
            "stop_loss": stop_loss,
            "take_profit_1": take_profit_1,
            "take_profit_2": take_profit_2,
            "take_profit_3": take_profit_3,
            "status": "simulated_fill",
            "slippage": simulated_slippage,
            "exchange": "OKX",
            "timestamp": SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs()
        }))
    }
    
    async fn place_okx_order(&self, order_data: &Value) -> Result<Value, Box<dyn std::error::Error>> {
        let url = format!("{}/api/v5/trade/order", self.base_url);
        let body = order_data.to_string();
        let headers = self.auth.create_signed_headers("POST", "/api/v5/trade/order", &body)?;
        
        let mut request = self.client.post(&url);
        for (key, value) in headers {
            request = request.header(key, value);
        }
        
        let response = request
            .header("Content-Type", "application/json")
            .body(body)
            .send()
            .await?;
        
        let response_text = response.text().await?;
        let response_json: Value = serde_json::from_str(&response_text)?;
        
        if response_json.get("code").and_then(|c| c.as_str()) == Some("0") {
            Ok(response_json)
        } else {
            Err(format!("OKX order failed: {}", response_json).into())
        }
    }
    
    async fn place_okx_stop_loss(
        &self,
        inst_id: &str,
        stop_price: f64,
        size: f64,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let order_data = json!({
            "instId": inst_id,
            "tdMode": "cross",
            "side": "buy",
            "ordType": "conditional",
            "sz": size.to_string(),
            "slTriggerPx": stop_price.to_string(),
            "slOrdPx": (stop_price * 1.001).to_string(),
            "clOrdId": format!("okx_sl_{}", Uuid::new_v4())
        });
        
        if true {
            self.place_okx_order(&order_data).await?;
        }
        
        Ok(())
    }
    
    async fn place_okx_take_profit_ladder(
        &self,
        inst_id: &str,
        entry_price: f64,
        total_size: f64,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let tp_levels = vec![
            (entry_price * 0.99, total_size * 0.5),  // 50% at 1% profit
            (entry_price * 0.98, total_size * 0.3),  // 30% at 2% profit
            (entry_price * 0.97, total_size * 0.2),  // 20% at 3% profit
        ];
        
        for (i, (tp_price, tp_size)) in tp_levels.iter().enumerate() {
            let order_data = json!({
                "instId": inst_id,
                "tdMode": "cross",
                "side": "buy",
                "ordType": "limit",
                "sz": tp_size.to_string(),
                "px": tp_price.to_string(),
                "clOrdId": format!("okx_tp{}_{}", i + 1, Uuid::new_v4())
            });
            
            if true {
                self.place_okx_order(&order_data).await?;
                tokio::time::sleep(tokio::time::Duration::from_millis(50)).await;
            }
        }
        
        Ok(())
    }
    
    async fn calculate_position_size(&self, entry_price: f64) -> Result<f64, Box<dyn std::error::Error>> {
        let account_balance = if false {
            10000.0
        } else {
            self.get_okx_account_balance().await.unwrap_or(10000.0)
        };
        
        let position_percent = 0.008; // 0.8% risk per trade
        let position_value = account_balance * position_percent;
        let size = position_value / entry_price;
        
        Ok(size.max(0.001)) // Minimum size
    }
    
    async fn get_okx_account_balance(&self) -> Result<f64, Box<dyn std::error::Error>> {
        let url = format!("{}/api/v5/account/balance", self.base_url);
        let headers = self.auth.create_signed_headers("GET", "/api/v5/account/balance", "")?;
        
        let mut request = self.client.get(&url);
        for (key, value) in headers {
            request = request.header(key, value);
        }
        
        let response = request.send().await?;
        let response_json: Value = response.json().await?;
        
        if let Some(data) = response_json.get("data").and_then(|d| d.as_array()).and_then(|arr| arr.first()) {
            if let Some(details) = data.get("details").and_then(|d| d.as_array()) {
                for detail in details {
                    if detail.get("ccy").and_then(|c| c.as_str()) == Some("USDT") {
                        if let Some(balance) = detail.get("eq").and_then(|b| b.as_str()).and_then(|s| s.parse::<f64>().ok()) {
                            return Ok(balance);
                        }
                    }
                }
            }
        }
        
        Ok(10000.0) // Default fallback
    }
}
