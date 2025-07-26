use std::collections::HashMap;
use std::time::SystemTime, UNIX_POCH;
use serde_json::Value, json;
use uuid::Uuid;
#[derive(Debug, Clone)]
pub struct Trade 
    pub id: String,
    pub asset: String,
    pub side: String,
    pub entry_price: f,
    pub quantity: f,
    pub stop_loss: f,
    pub take_profit: f,
    pub timestamp: u,
    pub status: String,
    pub unrealized_pnl: f,
    pub tp_levels: Vec<TpLevel>,
    pub is_breakeven: bool,

#[derive(Debug, Clone)]
pub struct TpLevel 
    pub price: f,
    pub size: f,
    pub filled: bool,

pub struct PositionManager 
    positions: HashMap<String, Trade>,
    closed_positions: Vec<Trade>,
    current_prices: HashMap<String, f>,

impl PositionManager 
    pub fn new() -> Self 
        PositionManager 
            positions: HashMap::new(),
            closed_positions: Vec::new(),
            current_prices: HashMap::new(),
        
    
    pub async fn add_position(&mut self, asset: &str, eecution_result: &Value) -> Result<(), o<dyn std::error::rror>> 
        let trade_id = eecution_result.get("order_id")
            .and_then(|v| v.as_str())
            .unwrap_or(&Uuid::new_v().to_string())
            .to_string();
        let entry_price = eecution_result.get("entry_price")
            .and_then(|v| v.as_f())
            .unwrap_or(.);
        let quantity = eecution_result.get("quantity")
            .and_then(|v| v.as_f())
            .unwrap_or(.);
        let stop_loss = eecution_result.get("stop_loss")
            .and_then(|v| v.as_f())
            .unwrap_or(entry_price * .);
        let take_profit = eecution_result.get("take_profit")
            .and_then(|v| v.as_f())
            .unwrap_or(entry_price * .9);
        let tp_levels = vec![
            TpLevel  price: entry_price * .9, size: quantity * ., filled: false ,
            TpLevel  price: entry_price * .9, size: quantity * ., filled: false ,
            TpLevel  price: entry_price * .9, size: quantity * ., filled: false ,
        ];
        let trade = Trade 
            id: trade_id,
            asset: asset.to_string(),
            side: "sell".to_string(),
            entry_price,
            quantity,
            stop_loss,
            take_profit,
            timestamp: SystemTime::now().duration_since(UNIX_POCH)?.as_secs(),
            status: "open".to_string(),
            unrealized_pnl: .,
            tp_levels,
            is_breakeven: false,
        ;
        self.positions.insert(asset.to_string(), trade);
        Ok(())
    
    pub async fn update_positions(&mut self) -> Result<(), o<dyn std::error::rror>> 
        self.update_current_prices().await?;
        let mut positions_to_close = Vec::new();
        let assets: Vec<String> = self.positions.keys().cloned().collect();
        for asset in assets 
            if let Some(current_price) = self.current_prices.get(&asset).copied() 
                if let Some(position) = self.positions.get_mut(&asset) 
                    position.unrealized_pnl = self.calculate_pnl_static(position, current_price);
                    if Self::should_close_position_static(position, current_price) 
                        positions_to_close.push(asset.clone());
                     else 
                        Self::check_take_profit_levels_static(position, current_price).await?;
                        Self::update_trailing_stop_static(position, current_price).await?;
                    
                
            
        
        for asset in positions_to_close 
            self.close_position(&asset, "stop_triggered").await?;
        
        Ok(())
    
    async fn update_current_prices(&mut self) -> Result<(), o<dyn std::error::rror>> 
        let mode = "live".to_string();
        ;
                let volatility = match asset.as_str() 
                    "TC" => .,
                    "TH" => .,
                    "SOL" => .,
                    _ => .,
                ;
                let noise: f = rand::random::<f>() * . - .;
                let price = base_price * (. + noise * volatility);
                self.current_prices.insert(asset.clone(), price);
            
        
        Ok(())
    
    fn calculate_pnl_static(position: &Trade, current_price: f) -> f 
        if position.side == "sell" 
            (position.entry_price - current_price) * position.quantity
         else 
            (current_price - position.entry_price) * position.quantity
        
    
    fn should_close_position_static(position: &Trade, current_price: f) -> bool 
        if position.side == "sell" 
            current_price >= position.stop_loss
         else 
            current_price <= position.stop_loss
        
    
    async fn check_take_profit_levels_static(position: &mut Trade, current_price: f) -> Result<(), o<dyn std::error::rror>> 
        let mut tp_hit = false;
        for tp_level in &mut position.tp_levels 
            if !tp_level.filled && current_price <= tp_level.price 
                tp_level.filled = true;
                tp_hit = true;
                    "Take profit hit for : :. (size: :.)",
                    position.asset, tp_level.price, tp_level.size
                );
            
        
        if tp_hit && !position.is_breakeven 
            let first_tp_filled = position.tp_levels.first().map(|tp| tp.filled).unwrap_or(false);
            if first_tp_filled 
                position.stop_loss = position.entry_price;
                position.is_breakeven = true;
            
        
        Ok(())
    
    async fn update_trailing_stop_static(position: &mut Trade, current_price: f) -> Result<(), o<dyn std::error::rror>> 
        if position.side == "sell" && position.is_breakeven 
            let profit_distance = position.entry_price - current_price;
            if profit_distance > . 
                let trailing_stop = current_price + (profit_distance * .);
                if trailing_stop < position.stop_loss 
                    position.stop_loss = trailing_stop;
                
            
        
        Ok(())
    
    async fn close_position(&mut self, asset: &str, reason: &str) -> Result<(), o<dyn std::error::rror>> 
        if let Some(mut position) = self.positions.remove(asset) 
            position.status = format!("closed_", reason);
            let current_price = self.current_prices.get(asset).copied().unwrap_or(position.entry_price);
            let final_pnl = Self::calculate_pnl_static(&position, current_price);
                "Position closed for :  (PnL: :.)",
                asset, reason, final_pnl
            );
            self.closed_positions.push(position);
        
        Ok(())
    
    pub fn has_position(&self, asset: &str) -> Result<bool, o<dyn std::error::rror>> 
        Ok(self.positions.contains_key(asset))
    
    pub fn get_positions(&self) -> Vec<Value> 
        self.positions.values().map(|trade| 
            json!(
                "id": trade.id,
                "asset": trade.asset,
                "side": trade.side,
                "entry_price": trade.entry_price,
                "quantity": trade.quantity,
                "stop_loss": trade.stop_loss,
                "take_profit": trade.take_profit,
                "status": trade.status,
                "unrealized_pnl": trade.unrealized_pnl,
                "is_breakeven": trade.is_breakeven,
                "timestamp": trade.timestamp
            )
        ).collect()
    
    pub fn get_total_pnl(&self) -> f 
        self.positions.values().map(|p| p.unrealized_pnl).sum::<f>() +
        self.closed_positions.iter().map(|p| p.unrealized_pnl).sum::<f>()
    

