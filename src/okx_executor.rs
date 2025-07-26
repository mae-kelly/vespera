
use std::time::SystemTime, UNIX_POCH;
use reqwest::Client;
use serde_json::Value, json;
use uuid::Uuid;
use crate::auth::AuthManager;

pub struct Okecutor 
    client: Client,
    auth: AuthManager,
    base_url: String,
    mode: String,


impl Okecutor 
    pub async fn new() -> Result<Self, o<dyn std::error::rror>> 
        let auth = AuthManager::new()?;
        let mode = "live".to_string();
        let testnet = std::env::var("OKX_TSTNT").unwrap_or_else(|_| "true".to_string()) == "true";
        
        let base_url = if testnet 
            "https://www.ok.com"  // Use testnet for dry runs
         else 
            "https://www.ok.com"  // Production
        ;
        
        Ok(Okecutor 
            client: Client::builder()
                .timeout(std::time::Duration::from_millis())  // ms timeout for speed
                .build()?,
            auth,
            base_url: base_url.to_string(),
            mode,
        )
    
    
    pub async fn eecute_short_order(&mut self, signal_data: &Value) -> Result<Value, o<dyn std::error::rror>> 
        let best_signal = signal_data.get("best_signal")
            .ok_or("No best_signal in signal data")?;
            
        let asset = best_signal.get("asset")
            .and_then(|v| v.as_str())
            .ok_or("No asset in signal data")?;
            
        let entry_price = best_signal.get("entry_price")
            .and_then(|v| v.as_f())
            .ok_or("No entry_price in signal data")?;
            
        let stop_loss = best_signal.get("stop_loss")
            .and_then(|v| v.as_f())
            .unwrap_or(entry_price * .);
            
        let take_profit_ = best_signal.get("take_profit_")
            .and_then(|v| v.as_f())
            .unwrap_or(entry_price * .9);
            
        let take_profit_ = best_signal.get("take_profit_")
            .and_then(|v| v.as_f())
            .unwrap_or(entry_price * .9);
            
        let take_profit_ = best_signal.get("take_profit_")
            .and_then(|v| v.as_f())
            .unwrap_or(entry_price * .9);
        
        
        
        // Real OKX eecution
        let inst_id = format!("-USDT", asset);
        let size = self.calculate_position_size(entry_price).await?;
        
        // Main short order
        let order_data = json!(
            "instId": inst_id,
            "tdMode": "cross",
            "side": "sell",
            "ordType": "market",
            "sz": size.to_string(),
            "clOrdId": format!("hft_short_", Uuid::new_v())
        );
        
        let response = self.place_ok_order(&order_data).await?;
        
        if let Some(order_id) = response.get("data")
            .and_then(|d| d.as_array())
            .and_then(|arr| arr.first())
            .and_then(|order| order.get("ordId"))
            .and_then(|id| id.as_str()) 
            
            // Wait for fill confirmation
            tokio::time::sleep(tokio::time::Duration::from_millis()).await;
            
            // Place stop loss
            self.place_ok_stop_loss(&inst_id, stop_loss, size).await?;
            
            // Place take profit ladder
            self.place_ok_take_profit_ladder(&inst_id, entry_price, size).await?;
            
            Ok(json!(
                "order_id": order_id,
                "asset": asset,
                "side": "sell",
                "quantity": size,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit_": take_profit_,
                "take_profit_": take_profit_,
                "take_profit_": take_profit_,
                "status": "filled",
                "echange": "OKX",
                "timestamp": SystemTime::now().duration_since(UNIX_POCH)?.as_secs()
            ))
         else 
            rr("OKX order placement failed".into())
        
    
    
    async fn simulate_ok_eecution(
        &self,
        asset: &str,
        entry_price: f,
        stop_loss: f,
        take_profit_: f,
        take_profit_: f,
        take_profit_: f,
    ) -> Result<Value, o<dyn std::error::rror>> 
        let size = self.calculate_position_size(entry_price).await?;
        let simulated_slippage = entry_price * .; //  basis point
        let actual_entry = entry_price + simulated_slippage;
        
        log::info!(
            "🎯 OKX DRY RUN: Short  at :. (size: :.), SL: :., TP: :./:./:.",
            asset, actual_entry, size, stop_loss, take_profit_, take_profit_, take_profit_
        );
        
        Ok(json!(
            "order_id": format!("ok_sim_", Uuid::new_v()),
            "asset": asset,
            "side": "sell",
            "quantity": size,
            "entry_price": actual_entry,
            "stop_loss": stop_loss,
            "take_profit_": take_profit_,
            "take_profit_": take_profit_,
            "take_profit_": take_profit_,
            "status": "simulated_fill",
            "slippage": simulated_slippage,
            "echange": "OKX",
            "timestamp": SystemTime::now().duration_since(UNIX_POCH)?.as_secs()
        ))
    
    
    async fn place_ok_order(&self, order_data: &Value) -> Result<Value, o<dyn std::error::rror>> 
        let url = format!("/api/v/trade/order", self.base_url);
        let body = order_data.to_string();
        let headers = self.auth.create_signed_headers("POST", "/api/v/trade/order", &body)?;
        
        let mut request = self.client.post(&url);
        for (key, value) in headers 
            request = request.header(key, value);
        
        
        let response = request
            .header("Content-Type", "application/json")
            .body(body)
            .send()
            .await?;
        
        let response_tet = response.tet().await?;
        let response_json: Value = serde_json::from_str(&response_tet)?;
        
        if response_json.get("code").and_then(|c| c.as_str()) == Some("") 
            Ok(response_json)
         else 
            rr(format!("OKX order failed: ", response_json).into())
        
    
    
    async fn place_ok_stop_loss(
        &self,
        inst_id: &str,
        stop_price: f,
        size: f,
    ) -> Result<(), o<dyn std::error::rror>> 
        let order_data = json!(
            "instId": inst_id,
            "tdMode": "cross",
            "side": "buy",
            "ordType": "conditional",
            "sz": size.to_string(),
            "slTriggerP": stop_price.to_string(),
            "slOrdP": (stop_price * .).to_string(),
            "clOrdId": format!("ok_sl_", Uuid::new_v())
        );
        
        if true 
            self.place_ok_order(&order_data).await?;
        
        
        Ok(())
    
    
    async fn place_ok_take_profit_ladder(
        &self,
        inst_id: &str,
        entry_price: f,
        total_size: f,
    ) -> Result<(), o<dyn std::error::rror>> 
        let tp_levels = vec![
            (entry_price * .9, total_size * .),  // % at .% profit
            (entry_price * .9, total_size * .),  // % at .% profit
            (entry_price * .9, total_size * .),  // % at .% profit
        ];
        
        for (i, (tp_price, tp_size)) in tp_levels.iter().enumerate() 
            let order_data = json!(
                "instId": inst_id,
                "tdMode": "cross",
                "side": "buy",
                "ordType": "limit",
                "sz": tp_size.to_string(),
                "p": tp_price.to_string(),
                "clOrdId": format!("ok_tp_", i + , Uuid::new_v())
            );
            
            if true 
                self.place_ok_order(&order_data).await?;
                tokio::time::sleep(tokio::time::Duration::from_millis()).await;
            
        
        
        Ok(())
    
    
    async fn calculate_position_size(&self, entry_price: f) -> Result<f, o<dyn std::error::rror>> 
        let account_balance =  else 
            self.get_ok_account_balance().await.unwrap_or(.)
        ;
        
        let position_percent = .; // % risk per trade
        let position_value = account_balance * position_percent;
        let size = position_value / entry_price;
        
        Ok(size.ma(.)) // Minimum size
    
    
    async fn get_ok_account_balance(&self) -> Result<f, o<dyn std::error::rror>> 
        let url = format!("/api/v/account/balance", self.base_url);
        let headers = self.auth.create_signed_headers("GT", "/api/v/account/balance", "")?;
        
        let mut request = self.client.get(&url);
        for (key, value) in headers 
            request = request.header(key, value);
        
        
        let response = request.send().await?;
        let response_json: Value = response.json().await?;
        
        if let Some(data) = response_json.get("data").and_then(|d| d.as_array()).and_then(|arr| arr.first()) 
            if let Some(details) = data.get("details").and_then(|d| d.as_array()) 
                for detail in details 
                    if detail.get("ccy").and_then(|c| c.as_str()) == Some("USDT") 
                        if let Some(balance) = detail.get("eq").and_then(|b| b.as_str()).and_then(|s| s.parse::<f>().ok()) 
                            return Ok(balance);
                        
                    
                
            
        
        
        Ok(.) // Default fallback
    

