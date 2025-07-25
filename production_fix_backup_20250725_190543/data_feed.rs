use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message};
use futures_util::{SinkExt, StreamExt};
use serde_json::{Value, json};
use tokio;

#[derive(Debug, Clone)]
pub struct TickData {
    pub symbol: String,
    pub price: f64,
    pub volume: f64,
    pub timestamp: u64,
}

pub struct DataFeed {
    tick_data: Arc<Mutex<HashMap<String, TickData>>>,
    position_data: Arc<Mutex<HashMap<String, Value>>>,
    mode: String,
    ws_url: String,
    is_running: Arc<Mutex<bool>>,
}

impl DataFeed {
    pub async fn new() -> Result<Self, Box<dyn std::error::Error + Send + Sync>> {
        let mode = std::env::var("MODE").unwrap_or_else(|_| "dry".to_string());
        let testnet = std::env::var("OKX_TESTNET").unwrap_or_else(|_| "true".to_string()) == "true";
        
        let ws_url = if testnet {
            "wss://ws.okx.com:8443/ws/v5/public".to_string()
        } else {
            "wss://ws.okx.com:8443/ws/v5/public".to_string()
        };
        
        Ok(DataFeed {
            tick_data: Arc::new(Mutex::new(HashMap::new())),
            position_data: Arc::new(Mutex::new(HashMap::new())),
            mode,
            ws_url,
            is_running: Arc::new(Mutex::new(false)),
        })
    }
    
    pub async fn start(&mut self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let mut is_running = self.is_running.lock().unwrap();
        if *is_running {
            return Ok(());
        }
        *is_running = true;
        drop(is_running);
        
        if self.mode == "dry" {
            self.start_simulation().await?;
        } else {
            self.start_websocket().await?;
        }
        
        Ok(())
    }
    
    async fn start_simulation(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let tick_data = Arc::clone(&self.tick_data);
        let is_running = Arc::clone(&self.is_running);
        
        tokio::spawn(async move {
            let mut base_prices = HashMap::new();
            base_prices.insert("BTC".to_string(), 45000.0);
            base_prices.insert("ETH".to_string(), 2500.0);
            base_prices.insert("SOL".to_string(), 100.0);
            
            while *is_running.lock().unwrap() {
                let current_time = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_secs();
                
                for (symbol, &base_price) in &base_prices {
                    let volatility = match symbol.as_str() {
                        "BTC" => 0.002,
                        "ETH" => 0.003,
                        "SOL" => 0.005,
                        _ => 0.002,
                    };
                    
                    let noise: f64 = rand::random::<f64>() * 2.0 - 1.0;
                    let price = base_price * (1.0 + noise * volatility);
                    let volume = 1000000.0 + (rand::random::<f64>() * 500000.0);
                    
                    let tick = TickData {
                        symbol: symbol.clone(),
                        price,
                        volume,
                        timestamp: current_time,
                    };
                    
                    tick_data.lock().unwrap().insert(symbol.clone(), tick);
                }
                
                tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
            }
        });
        
        log::info!("Simulation data feed started");
        Ok(())
    }
    
    async fn start_websocket(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let tick_data = Arc::clone(&self.tick_data);
        let position_data = Arc::clone(&self.position_data);
        let is_running = Arc::clone(&self.is_running);
        let ws_url = self.ws_url.clone();
        
        tokio::spawn(async move {
            while *is_running.lock().unwrap() {
                match Self::websocket_connection(&ws_url, &tick_data, &position_data).await {
                    Ok(_) => {
                        log::info!("WebSocket connection ended normally");
                    }
                    Err(e) => {
                        log::error!("WebSocket error: {}", e);
                        tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
                    }
                }
            }
        });
        
        log::info!("WebSocket data feed started");
        Ok(())
    }
    
    async fn websocket_connection(
        ws_url: &str,
        tick_data: &Arc<Mutex<HashMap<String, TickData>>>,
        position_data: &Arc<Mutex<HashMap<String, Value>>>,
    ) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        
        let (ws_stream, _) = connect_async(ws_url).await?;
        let (mut write, mut read) = ws_stream.split();
        
        let subscribe_msg = json!({
            "op": "subscribe",
            "args": [
                {"channel": "tickers", "instId": "BTC-USDT"},
                {"channel": "tickers", "instId": "ETH-USDT"},
                {"channel": "tickers", "instId": "SOL-USDT"}
            ]
        });
        
        write.send(Message::Text(subscribe_msg.to_string())).await?;
        
        while let Some(message) = read.next().await {
            match message? {
                Message::Text(text) => {
                    if let Ok(data) = serde_json::from_str::<Value>(&text) {
                        Self::process_websocket_message(&data, tick_data, position_data).await?;
                    }
                }
                Message::Close(_) => {
                    log::info!("WebSocket connection closed");
                    break;
                }
                _ => {}
            }
        }
        
        Ok(())
    }
    
    async fn process_websocket_message(
        data: &Value,
        tick_data: &Arc<Mutex<HashMap<String, TickData>>>,
        _position_data: &Arc<Mutex<HashMap<String, Value>>>,
    ) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        
        if let Some(data_array) = data.get("data").and_then(|d| d.as_array()) {
            for item in data_array {
                if let (Some(inst_id), Some(last_price), Some(volume)) = (
                    item.get("instId").and_then(|v| v.as_str()),
                    item.get("last").and_then(|v| v.as_str()).and_then(|s| s.parse::<f64>().ok()),
                    item.get("vol24h").and_then(|v| v.as_str()).and_then(|s| s.parse::<f64>().ok()),
                ) {
                    if let Some(symbol) = inst_id.strip_suffix("-USDT") {
                        let tick = TickData {
                            symbol: symbol.to_string(),
                            price: last_price,
                            volume,
                            timestamp: SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs(),
                        };
                        
                        tick_data.lock().unwrap().insert(symbol.to_string(), tick);
                    }
                }
            }
        }
        
        Ok(())
    }
    
    pub fn get_current_price(&self, symbol: &str) -> Option<f64> {
        self.tick_data.lock().unwrap()
            .get(symbol)
            .map(|tick| tick.price)
    }
    
    pub fn get_tick_data(&self, symbol: &str) -> Option<TickData> {
        self.tick_data.lock().unwrap()
            .get(symbol)
            .cloned()
    }
    
    pub fn get_all_prices(&self) -> HashMap<String, f64> {
        self.tick_data.lock().unwrap()
            .iter()
            .map(|(symbol, tick)| (symbol.clone(), tick.price))
            .collect()
    }
    
    pub async fn monitor_positions(&self, positions: &[Value]) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        for position in positions {
            if let Some(asset) = position.get("asset").and_then(|v| v.as_str()) {
                if let Some(current_price) = self.get_current_price(asset) {
                    let entry_price = position.get("entry_price").and_then(|v| v.as_f64()).unwrap_or(0.0);
                    let quantity = position.get("quantity").and_then(|v| v.as_f64()).unwrap_or(0.0);
                    
                    let unrealized_pnl = if entry_price > 0.0 {
                        (entry_price - current_price) * quantity
                    } else {
                        0.0
                    };
                    
                    let position_update = json!({
                        "asset": asset,
                        "current_price": current_price,
                        "unrealized_pnl": unrealized_pnl,
                        "timestamp": SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs()
                    });
                    
                    self.position_data.lock().unwrap().insert(asset.to_string(), position_update);
                }
            }
        }
        
        Ok(())
    }
    
    pub async fn write_fills_to_file(&self, fill_data: &Value) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let fills_content = std::fs::read_to_string("/tmp/fills.json")
            .unwrap_or_else(|_| "[]".to_string());
        
        let mut fills_array: Value = serde_json::from_str(&fills_content)
            .unwrap_or_else(|_| json!([]));
        
        if let Some(array) = fills_array.as_array_mut() {
            array.push(fill_data.clone());
            
            if array.len() > 1000 {
                array.drain(0..500);
            }
        }
        
        std::fs::write("/tmp/fills.json", serde_json::to_string_pretty(&fills_array)?)?;
        
        log::info!("Fill data written to file: {}", fill_data.get("asset").and_then(|v| v.as_str()).unwrap_or("unknown"));
        Ok(())
    }
    
    pub fn stop(&self) {
        *self.is_running.lock().unwrap() = false;
        log::info!("Data feed stopped");
    }
}
