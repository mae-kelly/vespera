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
    is_running: Arc<Mutex<bool>>,
}
impl DataFeed {
    pub async fn new() -> Result<Self, Box<dyn std::error::Error + Send + Sync>> {
        Ok(DataFeed {
            tick_data: Arc::new(Mutex::new(HashMap::new())),
            position_data: Arc::new(Mutex::new(HashMap::new())),
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
        self.start_real_websocket().await?;
        Ok(())
    }
    async fn start_real_websocket(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let tick_data = Arc::clone(&self.tick_data);
        let position_data = Arc::clone(&self.position_data);
        let is_running = Arc::clone(&self.is_running);
        tokio::spawn(async move {
            while *is_running.lock().unwrap() {
                match Self::real_websocket_connection(&tick_data, &position_data).await {
                    Ok(_) => {
                    }
                    Err(e) => {
                        tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
                    }
                }
            }
        });
        Ok(())
    }
    async fn real_websocket_connection(
        tick_data: &Arc<Mutex<HashMap<String, TickData>>>,
        position_data: &Arc<Mutex<HashMap<String, Value>>>,
    ) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let ws_url = "wss:
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
                        Self::process_real_market_data(&data, tick_data, position_data).await?;
                    }
                }
                Message::Close(_) => {
                    break;
                }
                _ => {}
            }
        }
        Ok(())
    }
    async fn process_real_market_data(
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
        Ok(())
    }
    pub fn stop(&self) {
        *self.is_running.lock().unwrap() = false;
    }
}
impl DataFeed {
    pub async fn get_connection_health(&self) -> Result<Value, Box<dyn std::error::Error + Send + Sync>> {
        let current_time = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
        let mut last_update = 0;
        if let Some(tick) = self.tick_data.lock().unwrap().get("BTC") {
            last_update = tick.timestamp;
        }
        let health_status = if current_time - last_update < 30 {
            "healthy"
        } else {
            "degraded"
        };
        Ok(serde_json::json!({
            "status": health_status,
            "last_update": last_update,
            "current_time": current_time,
            "latency_seconds": current_time - last_update
        }))
    }
    pub async fn export_performance_metrics(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let metrics = serde_json::json!({
            "total_ticks": self.tick_data.lock().unwrap().len(),
            "active_symbols": self.tick_data.lock().unwrap().keys().collect::<Vec<_>>(),
            "timestamp": SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs()
        });
        std::fs::write("/tmp/rust_metrics.json", serde_json::to_string_pretty(&metrics)?)?;
        Ok(())
    }
}
