use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};
use serde_json::{Value, json};
use uuid::Uuid;

#[derive(Debug, Clone)]
pub struct Trade {
    pub id: String,
    pub asset: String,
    pub side: String,
    pub entry_price: f64,
    pub quantity: f64,
    pub stop_loss: f64,
    pub take_profit: f64,
    pub timestamp: u64,
    pub status: String,
    pub unrealized_pnl: f64,
    pub tp_levels: Vec<TpLevel>,
    pub is_breakeven: bool,
}

#[derive(Debug, Clone)]
pub struct TpLevel {
    pub price: f64,
    pub size: f64,
    pub filled: bool,
}

pub struct PositionManager {
    positions: HashMap<String, Trade>,
    closed_positions: Vec<Trade>,
    current_prices: HashMap<String, f64>,
}

impl PositionManager {
    pub fn new() -> Self {
        PositionManager {
            positions: HashMap::new(),
            closed_positions: Vec::new(),
            current_prices: HashMap::new(),
        }
    }
    
    pub async fn add_position(&mut self, asset: &str, execution_result: &Value) -> Result<(), Box<dyn std::error::Error>> {
        let trade_id = execution_result.get("order_id")
            .and_then(|v| v.as_str())
            .unwrap_or(&Uuid::new_v4().to_string())
            .to_string();
        let entry_price = execution_result.get("entry_price")
            .and_then(|v| v.as_f64())
            .unwrap_or(0.0);
        let quantity = execution_result.get("quantity")
            .and_then(|v| v.as_f64())
            .unwrap_or(0.0);
        let stop_loss = execution_result.get("stop_loss")
            .and_then(|v| v.as_f64())
            .unwrap_or(entry_price * 1.02);
        let take_profit = execution_result.get("take_profit")
            .and_then(|v| v.as_f64())
            .unwrap_or(entry_price * 0.99);
        
        let tp_levels = vec![
            TpLevel { price: entry_price * 0.99, size: quantity * 0.5, filled: false },
            TpLevel { price: entry_price * 0.98, size: quantity * 0.3, filled: false },
            TpLevel { price: entry_price * 0.97, size: quantity * 0.2, filled: false },
        ];
        
        let trade = Trade {
            id: trade_id,
            asset: asset.to_string(),
            side: "sell".to_string(),
            entry_price,
            quantity,
            stop_loss,
            take_profit,
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs(),
            status: "open".to_string(),
            unrealized_pnl: 0.0,
            tp_levels,
            is_breakeven: false,
        };
        
        self.positions.insert(asset.to_string(), trade);
        Ok(())
    }
    
    pub async fn update_positions(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        self.update_current_prices().await?;
        
        let mut positions_to_close = Vec::new();
        let assets: Vec<String> = self.positions.keys().cloned().collect();
        
        for asset in assets {
            if let Some(current_price) = self.current_prices.get(&asset).copied() {
                if let Some(position) = self.positions.get_mut(&asset) {
                    position.unrealized_pnl = self.calculate_pnl_static(position, current_price);
                    
                    if Self::should_close_position_static(position, current_price) {
                        positions_to_close.push(asset.clone());
                    } else {
                        Self::check_take_profit_levels_static(position, current_price).await?;
                        Self::update_trailing_stop_static(position, current_price).await?;
                    }
                }
            }
        }
        
        for asset in positions_to_close {
            self.close_position(&asset, "stop_triggered").await?;
        }
        
        Ok(())
    }
    
    async fn update_current_prices(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let mode = "live".to_string();
        
        // Simulate price updates
        let base_prices = [
            ("BTC".to_string(), 67500.0),
            ("ETH".to_string(), 3200.0),
            ("SOL".to_string(), 145.0),
        ];
        
        for (asset, base_price) in base_prices.iter() {
            let volatility = match asset.as_str() {
                "BTC" => 0.02,
                "ETH" => 0.03,
                "SOL" => 0.05,
                _ => 0.02,
            };
            let noise: f64 = rand::random::<f64>() * 2.0 - 1.0;
            let price = base_price * (1.0 + noise * volatility);
            self.current_prices.insert(asset.clone(), price);
        }
        
        Ok(())
    }
    
    fn calculate_pnl_static(position: &Trade, current_price: f64) -> f64 {
        if position.side == "sell" {
            (position.entry_price - current_price) * position.quantity
        } else {
            (current_price - position.entry_price) * position.quantity
        }
    }
    
    fn should_close_position_static(position: &Trade, current_price: f64) -> bool {
        if position.side == "sell" {
            current_price >= position.stop_loss
        } else {
            current_price <= position.stop_loss
        }
    }
    
    async fn check_take_profit_levels_static(position: &mut Trade, current_price: f64) -> Result<(), Box<dyn std::error::Error>> {
        let mut tp_hit = false;
        
        for tp_level in &mut position.tp_levels {
            if !tp_level.filled && current_price <= tp_level.price {
                tp_level.filled = true;
                tp_hit = true;
                log::info!(
                    "Take profit hit for {}: {:.2} (size: {:.4})",
                    position.asset, tp_level.price, tp_level.size
                );
            }
        }
        
        if tp_hit && !position.is_breakeven {
            let first_tp_filled = position.tp_levels.first().map(|tp| tp.filled).unwrap_or(false);
            if first_tp_filled {
                position.stop_loss = position.entry_price;
                position.is_breakeven = true;
            }
        }
        
        Ok(())
    }
    
    async fn update_trailing_stop_static(position: &mut Trade, current_price: f64) -> Result<(), Box<dyn std::error::Error>> {
        if position.side == "sell" && position.is_breakeven {
            let profit_distance = position.entry_price - current_price;
            if profit_distance > 0.0 {
                let trailing_stop = current_price + (profit_distance * 0.5);
                if trailing_stop < position.stop_loss {
                    position.stop_loss = trailing_stop;
                }
            }
        }
        
        Ok(())
    }
    
    async fn close_position(&mut self, asset: &str, reason: &str) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(mut position) = self.positions.remove(asset) {
            position.status = format!("closed_{}", reason);
            let current_price = self.current_prices.get(asset).copied().unwrap_or(position.entry_price);
            let final_pnl = Self::calculate_pnl_static(&position, current_price);
            
            log::info!(
                "Position closed for {} {} (PnL: {:.2})",
                asset, reason, final_pnl
            );
            
            self.closed_positions.push(position);
        }
        
        Ok(())
    }
    
    pub fn has_position(&self, asset: &str) -> Result<bool, Box<dyn std::error::Error>> {
        Ok(self.positions.contains_key(asset))
    }
    
    pub fn get_positions(&self) -> Vec<Value> {
        self.positions.values().map(|trade| {
            json!({
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
            })
        }).collect()
    }
    
    pub fn get_total_pnl(&self) -> f64 {
        self.positions.values().map(|p| p.unrealized_pnl).sum::<f64>() +
        self.closed_positions.iter().map(|p| p.unrealized_pnl).sum::<f64>()
    }
}
