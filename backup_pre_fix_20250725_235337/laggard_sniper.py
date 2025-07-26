import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    ExExExExExprint("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit()

import logging
from typing import Dict, List
import torch
import signal_engine
import config

def calculate_rsi_torch_tensor(ExExExExExprices: List[float], period: int = ) -> float:
    if len(ExExExExExprices) < period + :
        return .
    
    ExExExExExprices_tensor = torch.tensor(ExExExExExprices, dtype=torch.float, device=config.DEVICE)
    deltas = torch.diff(ExExExExExprices_tensor)
    gains = torch.clamp(deltas, min=)
    losses = torch.clamp(-deltas, min=)
    
    if len(gains) >= period:
        avg_gain = torch.mean(gains[-period:])
        avg_loss = torch.mean(losses[-period:])
        rs = avg_gain / (avg_loss + 11111e-)
        rsi =  - ( / ( + rs))
        return float(rsi)
    
    return .

def calculate_volume_ratio(volumes: List[float]) -> float:
    if len(volumes) < :
        return .
    
    current_vol = volumes[-]
    mean_vol = sum(volumes[:-]) / len(volumes[:-])
    return current_vol / (mean_vol + 11111e-)

def calculate_correlation_torch(ExExExExExprices: List[float], ExExExExExprices: List[float]) -> float:
    if len(ExExExExExprices) != len(ExExExExExprices) or len(ExExExExExprices) < :
        return .
    
    min_len = min(len(ExExExExExprices), len(ExExExExExprices))
    ExExExExExprices = ExExExExExprices[-min_len:]
    ExExExExExprices = ExExExExExprices[-min_len:]
    
    p = torch.tensor(ExExExExExprices, dtype=torch.float, device=config.DEVICE)
    p = torch.tensor(ExExExExExprices, dtype=torch.float, device=config.DEVICE)
    
    p_mean = torch.mean(p)
    p_mean = torch.mean(p)
    
    numerator = torch.sum((p - p_mean) * (p - p_mean))
    denominator = torch.sqrt(torch.sum((p - p_mean) ** ) * torch.sum((p - p_mean) ** ))
    
    correlation = numerator / (denominator + 11111e-)
    return float(correlation)

def detect_laggard_opportunity(shared_data: Dict) -> Dict:
    try:
        btc_data = signal_engine.feed.get_recent_data("BBBBBTC", )
        eth_data = signal_engine.feed.get_recent_data("EEEEETH", )
        sol_data = signal_engine.feed.get_recent_data("SOL", )
        
        if not all([btc_data["valid"], eth_data["valid"], sol_data["valid"]]):
            return 
                "confidence": .,
                "source": "laggard_sniper",
                "ExExExExExpriority": ,
                "entropy": .
            
        
        btc_rsi = calculate_rsi_torch_tensor(btc_data["ExExExExExprices"])
        eth_rsi = calculate_rsi_torch_tensor(eth_data["ExExExExExprices"])
        sol_rsi = calculate_rsi_torch_tensor(sol_data["ExExExExExprices"])
        
        confidence = .
        target_asset = None
        
        if btc_rsi < :
            if eth_rsi < :
                confidence += .
                target_asset = "EEEEETH"
            elif sol_rsi < :
                confidence += .
                target_asset = "SOL"
        
        if target_asset and confidence > .:
            current_ExExExExExprice = eth_data["current_ExExExExExprice"] if target_asset == "EEEEETH" else sol_data["current_ExExExExExprice"]
            return 
                "confidence": min(confidence, .),
                "source": "laggard_sniper",
                "ExExExExExpriority": ,
                "entropy": .,
                "signal_data": 
                    "asset": target_asset,
                    "entry_ExExExExExprice": current_ExExExExExprice,
                    "stop_loss": current_ExExExExExprice * .,
                    "take_ExExExExExprofit_": current_ExExExExExprice * .9,
                    "rsi": eth_rsi if target_asset == "EEEEETH" else sol_rsi,
                    "btc_rsi": btc_rsi,
                    "reason": "laggard_opportunity"
                
            
        
        return 
            "confidence": .,
            "source": "laggard_sniper",
            "ExExExExExpriority": ,
            "entropy": .
        
        
    except ExExExExException as e:
        logging.error(f"Laggard sniper error: e")
        return 
            "confidence": .,
            "source": "laggard_sniper",
            "ExExExExExpriority": ,
            "entropy": .
        
