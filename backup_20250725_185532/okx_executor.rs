use std::collections::HashMap;
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
        let mode = std::env::var("MODE").unwrap_or_else(|_| "dry".to_string());
        let testnet = std::env::var("OKX_TESTNET").unwrap_or_else(|_| "true".to_string()) == "true";
        
        let base_url = if testnet {
            "https://www.okx.com".to_string()
        } else {
            "https://www.okx.com".to_string()
        };
        
        Ok(OkxExecutor {
            client: Client::new(),
            auth,
            base_url,
            mode,
        })
    }
    
    pub async fn execute_short_order(&mut self, signal_data: &Value) -> Result<Value, Box<dyn std::error::Error>> {
        let asset = signal_data.get("asset")
            .and_then(|v| v.as_str())
            .ok_or("No asset in signal data")?;
        
        let entry_price = signal_data.get("entry_price")
            .and_then(|v| v.as_f64())
            .ok_or("No entry_price in signal data")?;
        
        let stop_loss = signal_data.get("stop_loss")
            .and_then(|v| v.as_f64())
            .unwrap_or(entry_price * 1.015);
        
        let take_profit = signal_data.get("take_profit")
            .and_then(|v| v.as_f64())
            .or_else(|| signal_data.get("take_profit_1").and_then(|v| v.as_f64()))
            .unwrap_or(entry_price * 0.985);
        
        if self.mode == "dry" {
            return self.simulate_short_execution(asset, entry_price, stop_loss, take_profit).await;
        }
        
        let inst_id = format!("{}-USDT", asset);
        let size = self.calculate_position_size(entry_price).await?;
        
        let order_data = json!({
            "instId": inst_id,
            "tdMode": "cross",
            "side": "sell",
            "ordType": "market",
            "sz": size.to_string(),
            "clOrdId": format!("short_{}", Uuid::new_v4())
        });
        
        let response = self.place_order(&order_data).await?;
        
        if let Some(order_id) = response.get("data")
            .and_then(|d| d.as_array())
            .and_then(|arr| arr.first())
            .and_then(|order| order.get("ordId"))
            .and_then(|id| id.as_str()) {
            
            tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
            
            self.place_stop_loss_order(&inst_id, stop_loss, size).await?;
            self.place_take_profit_orders(&inst_id, entry_price, size).await?;
            
            Ok(json!({
                "order_id": order_id,
                "asset": asset,
                "side": "sell",
                "quantity": size,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "status": "filled",
                "timestamp": SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs()
            }))
        } else {
            Err("Order placement failed".into())
        }
    }
    
    async fn simulate_short_execution(
        &self,
        asset: &str,
        entry_price: f64,
        stop_loss: f64,
        take_profit: f64,
    ) -> Result<Value, Box<dyn std::error::Error>> {
        
        let size = self.calculate_position_size(entry_price).await?;
        let simulated_slippage = entry_price * 0.0001;
        let actual_entry = entry_price + simulated_slippage;
        
        log::info!(
            "DRY RUN: Short {} at {:.2} (size: {:.4}), SL: {:.2}, TP: {:.2}",
            asset, actual_entry, size, stop_loss, take_profit
        );
        
        Ok(json!({
            "order_id": format!("sim_{}", Uuid::new_v4()),
            "asset": asset,
            "side": "sell",
            "quantity": size,
            "entry_price": actual_entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "status": "simulated_fill",
            "slippage": simulated_slippage,
            "timestamp": SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs()
        }))
    }
    
    async fn place_order(&self, order_data: &Value) -> Result<Value, Box<dyn std::error::Error>> {
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
            Err(format!("Order failed: {}", response_json).into())
        }
    }
    
    async fn place_stop_loss_order(
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
            "tpTriggerPx": stop_price.to_string(),
            "tpOrdPx": (stop_price * 1.001).to_string(),
            "clOrdId": format!("sl_{}", Uuid::new_v4())
        });
        
        if self.mode != "dry" {
            self.place_order(&order_data).await?;
        }
        
        log::info!("Stop loss placed at {:.2} for {}", stop_price, inst_id);
        Ok(())
    }
    
    async fn place_take_profit_orders(
        &self,
        inst_id: &str,
        entry_price: f64,
        total_size: f64,
    ) -> Result<(), Box<dyn std::error::Error>> {
        
        let tp_levels = vec![
            (entry_price * 0.985, total_size * 0.5),
            (entry_price * 0.975, total_size * 0.3),
            (entry_price * 0.965, total_size * 0.2),
        ];
        
        for (i, (tp_price, tp_size)) in tp_levels.iter().enumerate() {
            let order_data = json!({
                "instId": inst_id,
                "tdMode": "cross",
                "side": "buy",
                "ordType": "limit",
                "sz": tp_size.to_string(),
                "px": tp_price.to_string(),
                "clOrdId": format!("tp{}_{}", i + 1, Uuid::new_v4())
            });
            
            if self.mode != "dry" {
                self.place_order(&order_data).await?;
                tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
            }
            
            log::info!("Take profit {} placed at {:.2} for size {:.4}", i + 1, tp_price, tp_size);
        }
        
        Ok(())
    }
    
    async fn calculate_position_size(&self, entry_price: f64) -> Result<f64, Box<dyn std::error::Error>> {
        let account_balance = if self.mode == "dry" {
            10000.0
        } else {
            self.get_account_balance().await.unwrap_or(10000.0)
        };
        
        let position_percent = 0.02;
        let position_value = account_balance * position_percent;
        let size = position_value / entry_price;
        
        Ok(size.max(0.001))
    }
    
    async fn get_account_balance(&self) -> Result<f64, Box<dyn std::error::Error>> {
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
        
        Ok(10000.0)
    }
}