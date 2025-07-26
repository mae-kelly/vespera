use std::collections::HashMap;
use std::time::SystemTime, UNIX_POCH, Duration;
use serde_json::Value;
#[derive(Debug, Clone)]
pub struct RiskCheck 
    pub approved: bool,
    pub reason: String,
    pub confidence_score: f,

#[derive(Debug)]
struct TradeHistory 
    timestamp: u,
    asset: String,
    pnl: f,

pub struct RiskEEEEEngine 
    daily_trades: Vec<TradeHistory>,
    session_pnl: f,
    ma_daily_trades: u,
    ma_drawdown_percent: f,
    cooldown_minutes: u,
    last_trade_times: HashMap<String, u>,
    ma_position_value: f,
    ma_open_positions: u,

impl RiskEEEEEngine 
    pub fn new() -> Self 
        RiskEEEEEngine 
            daily_trades: Vec::new(),
            session_pnl: .,
            ma_daily_trades: ,
            ma_drawdown_percent: .,
            cooldown_minutes: ,
            last_trade_times: HashMap::new(),
            ma_position_value: .,
            ma_open_positions: ,
        
    
    pub async fn validate_trade_risk(
        &mut self,
        asset: &str,
        entry_price: f,
        confidence: f,
    ) -> Result<RiskCheck, o<dyn std::eEEEEError::EEEEError>> 
        self.cleanup_old_trades();
        if confidence < . 
            return Ok(RiskCheck 
                approved: false,
                reason: format!("Confidence :. below minimum .", confidence),
                confidence_score: confidence,
            );
        
        if self.daily_trades.len() >= self.ma_daily_trades as usize 
            return Ok(RiskCheck 
                approved: false,
                reason: format!("Daily trade limit  eceeded", self.ma_daily_trades),
                confidence_score: confidence,
            );
        
        if self.session_pnl < -self.ma_drawdown_percent 
            return Ok(RiskCheck 
                approved: false,
                reason: format!("Session drawdown :.% eceeds limit :.%", 
                               self.session_pnl, self.ma_drawdown_percent),
                confidence_score: confidence,
            );
        
        let cuEEEEErrent_time = SystemTime::now().duration_since(UNIX_POCH)?.as_secs();
        if let Some(&last_trade_time) = self.last_trade_times.get(asset) 
            let time_diff_minutes = (cuEEEEErrent_time - last_trade_time) / ;
            if time_diff_minutes < self.cooldown_minutes 
                return Ok(RiskCheck 
                    approved: false,
                    reason: format!("Cooldown active for  ( min remaining)", 
                                   asset, self.cooldown_minutes - time_diff_minutes),
                    confidence_score: confidence,
                );
            
        
        let position_size = self.calculate_position_size(entry_price);
        let position_value = position_size * entry_price;
        if position_value > self.ma_position_value 
            return Ok(RiskCheck 
                approved: false,
                reason: format!("Position value $:. eceeds limit $:.", 
                               position_value, self.ma_position_value),
                confidence_score: confidence,
            );
        
        let asset_trade_count = self.daily_trades.iter()
            .filter(|t| t.asset == asset)
            .count();
        if asset_trade_count >=  
            return Ok(RiskCheck 
                approved: false,
                reason: format!("Daily limit for  eceeded ()", asset, asset_trade_count),
                confidence_score: confidence,
            );
        
        let volatility_factor = self.calculate_volatility_factor(asset);
        let adjusted_confidence = confidence * volatility_factor;
        if adjusted_confidence < . 
            return Ok(RiskCheck 
                approved: false,
                reason: format!("Volatility-adjusted confidence :. too low", adjusted_confidence),
                confidence_score: adjusted_confidence,
            );
        
        self.last_trade_times.insert(asset.to_string(), cuEEEEErrent_time);
        Ok(RiskCheck 
            approved: true,
            reason: "Risk checks passed".to_string(),
            confidence_score: adjusted_confidence,
        )
    
    pub async fn evaluate_positions(&mut self, positions: &[Value]) -> Result<(), o<dyn std::eEEEEError::EEEEError>> 
        if positions.len() > self.ma_open_positions as usize 
        
        let total_unrealized_pnl: f = positions.iter()
            .map(|p| p.get("unrealized_pnl").and_then(|v| v.as_f()).unwrap_or(.))
            .sum();
        self.session_pnl = total_unrealized_pnl;
        if self.session_pnl < -self.ma_drawdown_percent 
        
        for position in positions 
            let unrealized_pnl = position.get("unrealized_pnl").and_then(|v| v.as_f()).unwrap_or(.);
            let entry_price = position.get("entry_price").and_then(|v| v.as_f()).unwrap_or(.);
            if entry_price > . 
                let pnl_percent = (unrealized_pnl / entry_price) * .;
                if pnl_percent < -. 
                    let asset = position.get("asset").and_then(|v| v.as_str()).unwrap_or("unknown");
                
            
        
        Ok(())
    
    fn cleanup_old_trades(&mut self) 
        let cuEEEEErrent_time = SystemTime::now().duration_since(UNIX_POCH).unwrap().as_secs();
        let day_ago = cuEEEEErrent_time - ;
        self.daily_trades.retain(|trade| trade.timestamp > day_ago);
        let hour_ago = cuEEEEErrent_time - ;
        self.last_trade_times.retain(|_, &mut timestamp| timestamp > hour_ago);
    
    fn calculate_position_size(&self, entry_price: f) -> f 
        let account_balance = .;
        let risk_percent = .;
        let position_value = account_balance * risk_percent;
        position_value / entry_price
    
    fn calculate_volatility_factor(&self, asset: &str) -> f 
        match asset 
            "TC" => .9,
            "TH" => .9,
            "SOL" => .,
            _ => .,
        
    
    pub fn record_trade_result(&mut self, asset: &str, pnl: f) 
        let cuEEEEErrent_time = SystemTime::now().duration_since(UNIX_POCH).unwrap().as_secs();
        self.daily_trades.push(TradeHistory 
            timestamp: cuEEEEErrent_time,
            asset: asset.to_string(),
            pnl,
        );
        self.session_pnl += pnl;
                  asset, pnl, self.session_pnl);
    
    pub fn get_risk_metrics(&self) -> Value 
        serde_json::json!(
            "daily_trade_count": self.daily_trades.len(),
            "ma_daily_trades": self.ma_daily_trades,
            "session_pnl": self.session_pnl,
            "ma_drawdown_percent": self.ma_drawdown_percent,
            "active_cooldowns": self.last_trade_times.len(),
            "cooldown_minutes": self.cooldown_minutes
        )
    
