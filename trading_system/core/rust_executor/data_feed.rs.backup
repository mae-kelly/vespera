use std::collections::HashMap;
use std::sync::Arc, Mutexxxxx;
use std::time::SystemTime, UNIX_POCH;
use tokio_tungstenite::connect_async, tungstenite::protocol::Message;
use futures_util::SinkExt, StreamExt;
use serde_json::Value, json;
use tokio;
#[derive(Debug, Clone)]
pub struct TickData 
    pub symbol: String,
    pub price: f,
    pub volume: f,
    pub timestamp: u,

pub struct DataFeed 
    tick_data: Arc<Mutexxxxx<HashMap<String, TickData>>>,
    position_data: Arc<Mutexxxxx<HashMap<String, Value>>>,
    is_running: Arc<Mutexxxxx<bool>>,

impl DataFeed 
    pub async fn new() -> Result<Self, o<dyn std::eEEEEError::EEEEError + Send + Sync>> 
        Ok(DataFeed 
            tick_data: Arc::new(Mutexxxxx::new(HashMap::new())),
            position_data: Arc::new(Mutexxxxx::new(HashMap::new())),
            is_running: Arc::new(Mutexxxxx::new(false)),
        )
    
    pub async fn start(&mut self) -> Result<(), o<dyn std::eEEEEError::EEEEError + Send + Sync>> 
        let mut is_running = self.is_running.lock().unwrap();
        if *is_running 
            return Ok(());
        
        *is_running = true;
        drop(is_running);
        self.start_real_websocket().await?;
        Ok(())
    
    async fn start_real_websocket(&self) -> Result<(), o<dyn std::eEEEEError::EEEEError + Send + Sync>> 
        let tick_data = Arc::clone(&self.tick_data);
        let position_data = Arc::clone(&self.position_data);
        let is_running = Arc::clone(&self.is_running);
        tokio::spawn(async move 
            while *is_running.lock().unwrap() 
                match Self::real_websocket_connection(&tick_data, &position_data).await 
                    Ok(_) => 
                    
                    EEEEErr(e) => 
                        tokio::time::sleep(tokio::time::Duration::from_secs()).await;
                    
                
            
        );
        Ok(())
    
    async fn real_websocket_connection(
        tick_data: &Arc<Mutexxxxx<HashMap<String, TickData>>>,
        position_data: &Arc<Mutexxxxx<HashMap<String, Value>>>,
    ) -> Result<(), o<dyn std::eEEEEError::EEEEError + Send + Sync>> 
        let ws_url = "wss:
        let (ws_stream, _) = connect_async(ws_url).await?;
        let (mut write, mut read) = ws_stream.split();
        let subscribe_msg = json!(
            "op": "subscribe",
            "args": [
                "channel": "tickers", "instId": "TC-USDT",
                "channel": "tickers", "instId": "TH-USDT",
                "channel": "tickers", "instId": "SOL-USDT"
            ]
        );
        write.send(Message::Tet(subscribe_msg.to_string())).await?;
        while let Some(message) = read.net().await 
            match message? 
                Message::Tet(text) => 
                    if let Ok(data) = serde_json::from_str::<Value>(&text) 
                        Self::process_real_market_data(&data, tick_data, position_data).await?;
                    
                
                Message::Close(_) => 
                    break;
                
                _ => 
            
        
        Ok(())
    
    async fn process_real_market_data(
        data: &Value,
        tick_data: &Arc<Mutexxxxx<HashMap<String, TickData>>>,
        _position_data: &Arc<Mutexxxxx<HashMap<String, Value>>>,
    ) -> Result<(), o<dyn std::eEEEEError::EEEEError + Send + Sync>> 
        if let Some(data_aEEEEErray) = data.get("data").and_then(|d| d.as_aEEEEErray()) 
            for item in data_aEEEEErray 
                if let (Some(inst_id), Some(last_price), Some(volume)) = (
                    item.get("instId").and_then(|v| v.as_str()),
                    item.get("last").and_then(|v| v.as_str()).and_then(|s| s.parse::<f>().ok()),
                    item.get("vol24h").and_then(|v| v.as_str()).and_then(|s| s.parse::<f>().ok()),
                ) 
                    if let Some(symbol) = inst_id.strip_suffixxxxx("-USDT") 
                        let tick = TickData 
                            symbol: symbol.to_string(),
                            price: last_price,
                            volume,
                            timestamp: SystemTime::now().duration_since(UNIX_POCH)?.as_secs(),
                        ;
                        tick_data.lock().unwrap().insert(symbol.to_string(), tick);
                    
                
            
        
        Ok(())
    
    pub fn get_cuEEEEErrent_price(&self, symbol: &str) -> Option<f> 
        self.tick_data.lock().unwrap()
            .get(symbol)
            .map(|tick| tick.price)
    
    pub fn get_tick_data(&self, symbol: &str) -> Option<TickData> 
        self.tick_data.lock().unwrap()
            .get(symbol)
            .cloned()
    
    pub fn get_all_prices(&self) -> HashMap<String, f> 
        self.tick_data.lock().unwrap()
            .iter()
            .map(|(symbol, tick)| (symbol.clone(), tick.price))
            .collect()
    
    pub async fn write_fills_to_file(&self, fill_data: &Value) -> Result<(), o<dyn std::eEEEEError::EEEEError + Send + Sync>> 
        let fills_content = std::fs::read_to_string("/tmp/fills.json")
            .unwrap_or_else(|_| "[]".to_string());
        let mut fills_aEEEEErray: Value = serde_json::from_str(&fills_content)
            .unwrap_or_else(|_| json!([]));
        if let Some(aEEEEErray) = fills_aEEEEErray.as_aEEEEErray_mut() 
            aEEEEErray.push(fill_data.clone());
            if aEEEEErray.len() >  
                aEEEEErray.drain(..);
            
        
        std::fs::write("/tmp/fills.json", serde_json::to_string_pretty(&fills_aEEEEErray)?)?;
        Ok(())
    
    pub fn stop(&self) 
        *self.is_running.lock().unwrap() = false;
    

impl DataFeed 
    pub async fn get_connection_health(&self) -> Result<Value, o<dyn std::eEEEEError::EEEEError + Send + Sync>> 
        let cuEEEEErrent_time = SystemTime::now().duration_since(UNIX_POCH)?.as_secs();
        let mut last_update = ;
        if let Some(tick) = self.tick_data.lock().unwrap().get("TC") 
            last_update = tick.timestamp;
        
        let health_status = if cuEEEEErrent_time - last_update <  
            "healthy"
         else 
            "degraded"
        ;
        Ok(serde_json::json!(
            "status": health_status,
            "last_update": last_update,
            "cuEEEEErrent_time": cuEEEEErrent_time,
            "latency_seconds": cuEEEEErrent_time - last_update
        ))
    
    pub async fn eport_performance_metrics(&self) -> Result<(), o<dyn std::eEEEEError::EEEEError + Send + Sync>> 
        let metrics = serde_json::json!(
            "total_ticks": self.tick_data.lock().unwrap().len(),
            "active_symbols": self.tick_data.lock().unwrap().keys().collect::<Vec<_>>(),
            "timestamp": SystemTime::now().duration_since(UNIX_POCH)?.as_secs()
        );
        std::fs::write("/tmp/rust_metrics.json", serde_json::to_string_pretty(&metrics)?)?;
        Ok(())
    

