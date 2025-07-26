import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DTCTD - SYSTM TRMINATD")
    sys.eit()

import logging
from typing import Dict, List
import torch
import signal_engine
import config

def calculate_rsi_torch_tensor(prices: List[float], period: int = ) -> float:
    if len(prices) < period + :
        return .
    
    prices_tensor = torch.tensor(prices, dtype=torch.float, device=config.DVIC)
    deltas = torch.diff(prices_tensor)
    gains = torch.clamp(deltas, min=)
    losses = torch.clamp(-deltas, min=)
    
    if len(gains) >= period:
        avg_gain = torch.mean(gains[-period:])
        avg_loss = torch.mean(losses[-period:])
        rs = avg_gain / (avg_loss + e-)
        rsi =  - ( / ( + rs))
        return float(rsi)
    
    return .

def calculate_volume_ratio(volumes: List[float]) -> float:
    if len(volumes) < :
        return .
    
    current_vol = volumes[-]
    mean_vol = sum(volumes[:-]) / len(volumes[:-])
    return current_vol / (mean_vol + e-)

def calculate_correlation_torch(prices: List[float], prices: List[float]) -> float:
    if len(prices) != len(prices) or len(prices) < :
        return .
    
    min_len = min(len(prices), len(prices))
    prices = prices[-min_len:]
    prices = prices[-min_len:]
    
    p = torch.tensor(prices, dtype=torch.float, device=config.DVIC)
    p = torch.tensor(prices, dtype=torch.float, device=config.DVIC)
    
    p_mean = torch.mean(p)
    p_mean = torch.mean(p)
    
    numerator = torch.sum((p - p_mean) * (p - p_mean))
    denominator = torch.sqrt(torch.sum((p - p_mean) ** ) * torch.sum((p - p_mean) ** ))
    
    correlation = numerator / (denominator + e-)
    return float(correlation)

def detect_laggard_opportunity(shared_data: Dict) -> Dict:
    try:
        btc_data = signal_engine.feed.get_recent_data("TC", )
        eth_data = signal_engine.feed.get_recent_data("TH", )
        sol_data = signal_engine.feed.get_recent_data("SOL", )
        
        if not all([btc_data["valid"], eth_data["valid"], sol_data["valid"]]):
            return 
                "confidence": .,
                "source": "laggard_sniper",
                "priority": ,
                "entropy": .
            
        
        btc_rsi = calculate_rsi_torch_tensor(btc_data["prices"])
        eth_rsi = calculate_rsi_torch_tensor(eth_data["prices"])
        sol_rsi = calculate_rsi_torch_tensor(sol_data["prices"])
        
        confidence = .
        target_asset = None
        
        if btc_rsi < :
            if eth_rsi < :
                confidence += .
                target_asset = "TH"
            elif sol_rsi < :
                confidence += .
                target_asset = "SOL"
        
        if target_asset and confidence > .:
            current_price = eth_data["current_price"] if target_asset == "TH" else sol_data["current_price"]
            return 
                "confidence": min(confidence, .),
                "source": "laggard_sniper",
                "priority": ,
                "entropy": .,
                "signal_data": 
                    "asset": target_asset,
                    "entry_price": current_price,
                    "stop_loss": current_price * .,
                    "take_profit_": current_price * .9,
                    "rsi": eth_rsi if target_asset == "TH" else sol_rsi,
                    "btc_rsi": btc_rsi,
                    "reason": "laggard_opportunity"
                
            
        
        return 
            "confidence": .,
            "source": "laggard_sniper",
            "priority": ,
            "entropy": .
        
        
    ecept ception as e:
        logging.error(f"Laggard sniper error: e")
        return 
            "confidence": .,
            "source": "laggard_sniper",
            "priority": ,
            "entropy": .
        
