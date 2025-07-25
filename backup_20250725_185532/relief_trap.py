import logging
from typing import Dict, List
import torch
import cupy as cp
import signal_engine
import config

def detect_relief_trap(shared_data: Dict) -> Dict:
    try:
        # Get recent data for analysis
        btc_data = signal_engine.feed.get_recent_data("BTC", 30)
        
        if not btc_data["valid"] or len(btc_data["prices"]) < 20:
            return {
                "confidence": 0.0,
                "source": "relief_trap",
                "priority": 3,
                "entropy": 0.0
            }
        
        prices = btc_data["prices"]
        volumes = btc_data["volumes"]
        current_price = btc_data["current_price"]
        
        # Calculate VWAP
        vwap = calculate_vwap(prices, volumes)
        
        # Check for price bounce >1.5% in 15min
        bounce_threshold = 0.015  # 1.5%
        lookback_minutes = 15
        
        if len(prices) >= lookback_minutes:
            price_15min_ago = prices[-lookback_minutes]
            price_bounce = (current_price - price_15min_ago) / price_15min_ago
            
            if price_bounce > bounce_threshold:
                # Price bounced >1.5%, now check other conditions
                
                # Calculate RSI divergence between 1m and 15m timeframes
                rsi_1m = calculate_rsi_short_term(prices[-5:])  # 1-min approximation
                rsi_15m = calculate_rsi_short_term(prices[-15:])  # 15-min approximation
                
                # RSI divergence calculation using torch.abs(RSI_1m - RSI_15m)
                if torch.cuda.is_available():
                    rsi_divergence = float(torch.abs(torch.tensor(rsi_1m) - torch.tensor(rsi_15m)))
                else:
                    rsi_divergence = abs(rsi_1m - rsi_15m)
                
                # Check if fails to reclaim VWAP
                fails_vwap_reclaim = current_price < vwap
                
                confidence = 0.0
                reason = []
                
                # Trigger conditions:
                # 1. Price bounces >1.5% in 15min ✓
                # 2. RSI divergence >10 points
                # 3. Fails to reclaim VWAP
                
                if rsi_divergence > 10:
                    confidence += 0.3
                    reason.append("rsi_divergence")
                
                if fails_vwap_reclaim:
                    confidence += 0.25
                    reason.append("failed_vwap_reclaim")
                
                # Additional confirmation: volume should be elevated during bounce
                volume_ratio = calculate_volume_ratio(volumes)
                if volume_ratio > 1.5:
                    confidence += 0.15
                    reason.append("elevated_volume")
                
                # Trend confirmation: overall trend should be down
                if len(prices) >= 30:
                    trend_start = prices[-30]
                    overall_trend = (current_price - trend_start) / trend_start
                    if overall_trend < -0.02:  # Overall down trend >2%
                        confidence += 0.1
                        reason.append("downtrend_context")
                
                if confidence > 0.2:
                    return {
                        "confidence": min(confidence, 1.0),
                        "source": "relief_trap",
                        "priority": 3,
                        "entropy": 0.0,
                        "signal_data": {
                            "asset": "BTC",
                            "entry_price": current_price,
                            "stop_loss": current_price * 1.015,
                            "take_profit_1": current_price * 0.985,
                            "price_bounce_15min": price_bounce * 100,
                            "rsi_1m": rsi_1m,
                            "rsi_15m": rsi_15m,
                            "rsi_divergence": rsi_divergence,
                            "vwap": vwap,
                            "failed_vwap_reclaim": fails_vwap_reclaim,
                            "volume_ratio": volume_ratio,
                            "reason": " + ".join(reason)
                        }
                    }
        
        return {
            "confidence": 0.0,
            "source": "relief_trap",
            "priority": 3,
            "entropy": 0.0
        }
        
    except Exception as e:
        logging.error(f"Relief trap detector error: {e}")
        return {
            "confidence": 0.0,
            "source": "relief_trap",
            "priority": 3,
            "entropy": 0.0
        }

def calculate_rsi_short_term(prices: List[float], period: int = 14) -> float:
    """Calculate RSI for short-term analysis"""
    if len(prices) < 2:
        return 50.0
    
    # Simplified RSI for short price series
    if torch.cuda.is_available():
        prices_tensor = torch.tensor(prices, dtype=torch.float32, device='cuda')
        deltas = torch.diff(prices_tensor)
        gains = torch.clamp(deltas, min=0)
        losses = torch.clamp(-deltas, min=0)
        
        avg_gain = torch.mean(gains) if len(gains) > 0 else torch.tensor(0.0)
        avg_loss = torch.mean(losses) if len(losses) > 0 else torch.tensor(0.0)
        
        rs = avg_gain / (avg_loss + 1e-8)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    else:
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [max(0, d) for d in deltas]
        losses = [max(0, -d) for d in deltas]
        
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
    """Calculate Volume Weighted Average Price"""
    if len(prices) != len(volumes) or len(prices) == 0:
        return prices[-1] if prices else 0
    
    if torch.cuda.is_available():
        prices_cp = cp.array(prices)
        volumes_cp = cp.array(volumes)
        total_pv = cp.sum(prices_cp * volumes_cp)
        total_v = cp.sum(volumes_cp)
        return float(total_pv / (total_v + 1e-8))
    else:
        total_pv = sum(p * v for p, v in zip(prices, volumes))
        total_v = sum(volumes)
        return total_pv / (total_v + 1e-8)

def calculate_volume_ratio(volumes: List[float]) -> float:
    """Calculate current volume vs average ratio"""
    if len(volumes) < 3:
        return 1.0
    
    current_vol = volumes[-1]
    avg_vol = sum(volumes[:-1]) / len(volumes[:-1])
    return current_vol / (avg_vol + 1e-8)
