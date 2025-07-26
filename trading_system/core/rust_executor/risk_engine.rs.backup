use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH, Duration};
use serde_json::Value;

#[derive(Debug, Clone)]
pub struct RiskCheck {
    pub approved: bool,
    pub reason: String,
    pub confidence_score: f64,
}

#[derive(Debug)]
struct TradeHistory {
    timestamp: u64,
    asset: String,
    pnl: f64,
}

pub struct RiskEngine {
    daily_trades: Vec<TradeHistory>,
    session_pnl: f64,
    max_daily_trades: u32,
    max_drawdown_percent: f64,
    cooldown_minutes: u64,
    last_trade_times: HashMap<String, u64>,
    max_position_value: f64,
    max_open_positions: u32,
}

impl RiskEngine {
    pub fn new() -> Self {
        RiskEngine {
            daily_trades: Vec::new(),
            session_pnl: 0.0,
            max_daily_trades: 10,
            max_drawdown_percent: 3.0,
            cooldown_minutes: 15,
            last_trade_times: HashMap::new(),
            max_position_value: 20000.0,
            max_open_positions: 3,
        }
    }
    
    pub async fn validate_trade_risk(
        &mut self,
        asset: &str,
        entry_price: f64,
        confidence: f64,
    ) -> Result<RiskCheck, Box<dyn std::error::Error>> {
        self.cleanup_old_trades();
        
        if confidence < 0.75 {
            return Ok(RiskCheck {
                approved: false,
                reason: format!("Confidence {:.3} below minimum 0.75", confidence),
                confidence_score: confidence,
            });
        }
        
        if self.daily_trades.len() >= self.max_daily_trades as usize {
            return Ok(RiskCheck {
                approved: false,
                reason: format!("Daily trade limit {} exceeded", self.max_daily_trades),
                confidence_score: confidence,
            });
        }
        
        if self.session_pnl < -self.max_drawdown_percent {
            return Ok(RiskCheck {
                approved: false,
                reason: format!("Session drawdown {:.1}% exceeds limit {:.1}%", 
                               self.session_pnl, self.max_drawdown_percent),
                confidence_score: confidence,
            });
        }
        
        let current_time = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
        if let Some(&last_trade_time) = self.last_trade_times.get(asset) {
            let time_diff_minutes = (current_time - last_trade_time) / 60;
            if time_diff_minutes < self.cooldown_minutes {
                return Ok(RiskCheck {
                    approved: false,
                    reason: format!("Cooldown active for {} ({} min remaining)", 
                                   asset, self.cooldown_minutes - time_diff_minutes),
                    confidence_score: confidence,
                });
            }
        }
        
        let position_size = self.calculate_position_size(entry_price);
        let position_value = position_size * entry_price;
        if position_value > self.max_position_value {
            return Ok(RiskCheck {
                approved: false,
                reason: format!("Position value ${:.0} exceeds limit ${:.0}", 
                               position_value, self.max_position_value),
                confidence_score: confidence,
            });
        }
        
        let asset_trade_count = self.daily_trades.iter()
            .filter(|t| t.asset == asset)
            .count();
        if asset_trade_count >= 3 {
            return Ok(RiskCheck {
                approved: false,
                reason: format!("Daily limit for {} exceeded ({})", asset, asset_trade_count),
                confidence_score: confidence,
            });
        }
        
        let volatility_factor = self.calculate_volatility_factor(asset);
        let adjusted_confidence = confidence * volatility_factor;
        if adjusted_confidence < 0.7 {
            return Ok(RiskCheck {
                approved: false,
                reason: format!("Volatility-adjusted confidence {:.3} too low", adjusted_confidence),
                confidence_score: adjusted_confidence,
            });
        }
        
        self.last_trade_times.insert(asset.to_string(), current_time);
        Ok(RiskCheck {
            approved: true,
            reason: "Risk checks passed".to_string(),
            confidence_score: adjusted_confidence,
        })
    }
    
    pub async fn evaluate_positions(&mut self, positions: &[Value]) -> Result<(), Box<dyn std::error::Error>> {
        if positions.len() > self.max_open_positions as usize {
            log::warn!("Too many open positions: {} > {}", positions.len(), self.max_open_positions);
        }
        
        let total_unrealized_pnl: f64 = positions.iter()
            .map(|p| p.get("unrealized_pnl").and_then(|v| v.as_f64()).unwrap_or(0.0))
            .sum();
        
        self.session_pnl = total_unrealized_pnl;
        
        if self.session_pnl < -self.max_drawdown_percent {
            log::warn!("Session drawdown exceeds limit: {:.1}%", self.session_pnl);
        }
        
        for position in positions {
            let unrealized_pnl = position.get("unrealized_pnl").and_then(|v| v.as_f64()).unwrap_or(0.0);
            let entry_price = position.get("entry_price").and_then(|v| v.as_f64()).unwrap_or(0.0);
            
            if entry_price > 0.0 {
                let pnl_percent = (unrealized_pnl / entry_price) * 100.0;
                if pnl_percent < -5.0 {
                    let asset = position.get("asset").and_then(|v| v.as_str()).unwrap_or("unknown");
                    log::warn!("Large loss detected for {}: {:.1}%", asset, pnl_percent);
                }
            }
        }
        
        Ok(())
    }
    
    fn cleanup_old_trades(&mut self) {
        let current_time = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        let day_ago = current_time - 86400;
        self.daily_trades.retain(|trade| trade.timestamp > day_ago);
        
        let hour_ago = current_time - 3600;
        self.last_trade_times.retain(|_, &mut timestamp| timestamp > hour_ago);
    }
    
    fn calculate_position_size(&self, entry_price: f64) -> f64 {
        let account_balance = 10000.0;
        let risk_percent = 0.008;
        let position_value = account_balance * risk_percent;
        position_value / entry_price
    }
    
    fn calculate_volatility_factor(&self, asset: &str) -> f64 {
        match asset {
            "BTC" => 0.95,
            "ETH" => 0.90,
            "SOL" => 0.85,
            _ => 0.80,
        }
    }
    
    pub fn record_trade_result(&mut self, asset: &str, pnl: f64) {
        let current_time = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        self.daily_trades.push(TradeHistory {
            timestamp: current_time,
            asset: asset.to_string(),
            pnl,
        });
        self.session_pnl += pnl;
        
        log::info!("Trade recorded for {}: PnL {:.2}, Session PnL: {:.2}", 
                  asset, pnl, self.session_pnl);
    }
    
    pub fn get_risk_metrics(&self) -> Value {
        serde_json::json!({
            "daily_trade_count": self.daily_trades.len(),
            "max_daily_trades": self.max_daily_trades,
            "session_pnl": self.session_pnl,
            "max_drawdown_percent": self.max_drawdown_percent,
            "active_cooldowns": self.last_trade_times.len(),
            "cooldown_minutes": self.cooldown_minutes
        })
    }
}
