use std::time::{SystemTime, UNIX_EPOCH};
use reqwest::Client;
use serde_json::{Value, json};
use uuid::Uuid;
use crate::auth::AuthManager;

pub struct OkxExecutor {
    client: Client,
    auth: AuthManager,
    base_url: String,
}

impl OkxExecutor {
    pub async fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let auth = AuthManager::new()?;
        let testnet = std::env::var("OKX_TESTNET")
            .map_err(|_| "OKX_TESTNET environment variable required")?;
        
        if testnet == "true" {
            return Err("Production does not allow testnet".into());
        }
        
        let base_url = "https://www.okx.com";
        
        Ok(OkxExecutor {
            client: Client::builder()
                .timeout(std::time::Duration::from_millis(5000))
                .build()?,
            auth,
            base_url: base_url.to_string(),
        })
    }
    
    pub async fn execute_short_order(&mut self, signal_data: &Value) -> Result<Value, Box<dyn std::error::Error>> {
        let best_signal = signal_data.get("best_signal")
            .ok_or("PRODUCTION ERROR: No best_signal in signal data")?;
            
        let asset = best_signal.get("asset")
            .and_then(|v| v.as_str())
            .ok_or("PRODUCTION ERROR: No asset in signal data")?;
            
        let entry_price = best_signal.get("entry_price")
            .and_then(|v| v.as_f64())
            .ok_or("PRODUCTION ERROR: No entry_price in signal data")?;
            
        if entry_price <= 0.0 {
            return Err("PRODUCTION ERROR: Invalid entry price".into());
        }
        
        let account_balance = self.get_okx_account_balance().await?;
        let inst_id = format!("{}-USDT", asset);
        let size = self.calculate_position_size(entry_price, account_balance)?;
        
        let order_data = json!({
            "instId": inst_id,
            "tdMode": "cross",
            "side": "sell",
            "ordType": "market",
            "sz": size.to_string(),
            "clOrdId": format!("hft_prod_{}", Uuid::new_v4())
        });
        
        let response = self.place_okx_order(&order_data).await?;
        
        let order_id = response.get("data")
            .and_then(|d| d.as_array())
            .and_then(|arr| arr.first())
            .and_then(|order| order.get("ordId"))
            .and_then(|id| id.as_str())
            .ok_or("PRODUCTION ERROR: Order placement failed")?;
        
        tokio::time::sleep(tokio::time::Duration::from_millis(200)).await;
        
        let stop_loss = entry_price * 1.015;
        self.place_okx_stop_loss(&inst_id, stop_loss, size).await?;
        self.place_okx_take_profit_ladder(&inst_id, entry_price, size).await?;
        
        Ok(json!({
            "order_id": order_id,
            "asset": asset,
            "side": "sell",
            "quantity": size,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit_1": entry_price * 0.99,
            "status": "filled",
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
    
    async fn place_okx_stop_loss(&self, inst_id: &str, stop_price: f64, size: f64) -> Result<(), Box<dyn std::error::Error>> {
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
        
        self.place_okx_order(&order_data).await?;
        Ok(())
    }
    
    async fn place_okx_take_profit_ladder(&self, inst_id: &str, entry_price: f64, total_size: f64) -> Result<(), Box<dyn std::error::Error>> {
        let tp_levels = vec![
            (entry_price * 0.99, total_size * 0.5),
            (entry_price * 0.98, total_size * 0.3),
            (entry_price * 0.97, total_size * 0.2),
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
            
            self.place_okx_order(&order_data).await?;
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        }
        
        Ok(())
    }
    
    fn calculate_position_size(&self, entry_price: f64, account_balance: f64) -> Result<f64, Box<dyn std::error::Error>> {
        let position_percent = 0.005;
        let position_value = account_balance * position_percent;
        let size = position_value / entry_price;
        
        if size < 0.001 {
            return Err("Position size too small".into());
        }
        
        if position_value > 20000.0 {
            return Err("Position value exceeds maximum limit".into());
        }
        
        Ok(size)
    }
    
    async fn get_okx_account_balance(&self) -> Result<f64, Box<dyn std::error::Error>> {
        let url = format!("{}/api/v5/account/balance", self.base_url);
        let headers = self.auth.create_signed_headers("GET", "/api/v5/account/balance", "")?;
        
        let mut request = self.client.get(&url);
        for (key, value) in headers {
            request = request.header(key, value);
        }
        
        let response = request.send().await?;
        
        if !response.status().is_success() {
            return Err(format!("Account balance request failed: {}", response.status()).into());
        }
        
        let response_json: Value = response.json().await?;
        
        if let Some(data) = response_json.get("data").and_then(|d| d.as_array()).and_then(|arr| arr.first()) {
            if let Some(details) = data.get("details").and_then(|d| d.as_array()) {
                for detail in details {
                    if detail.get("ccy").and_then(|c| c.as_str()) == Some("USDT") {
                        if let Some(balance_str) = detail.get("eq").and_then(|b| b.as_str()) {
                            if let Ok(balance) = balance_str.parse::<f64>() {
                                if balance < 1000.0 {
                                    return Err("Insufficient account balance for trading".into());
                                }
                                return Ok(balance);
                            }
                        }
                    }
                }
            }
        }
        
        Err("Cannot retrieve valid account balance".into())
    }
}
