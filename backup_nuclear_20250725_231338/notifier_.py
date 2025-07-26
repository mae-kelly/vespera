import logging
import os
import requests
import json
from typing import Dict, List
import config
import time

class AestheticNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.user_id = os.getenv("DISCORD_USER_ID")
        
        # Sacred color palette -  consciousness colors
        self.colors = {
            "divine_signal": 0xE8D5C4,     # Warm cream - divine feminine
            "moon_phase": 0xD4AFDF,        # Soft lavender - lunar consciousness  
            "sacred_water": 0xB8E0D2,      # Pale mint - emotional depths
            "earth_wisdom": 0xDDBEA9,      # Dusty rose - grounded intuition
            "star_whisper": 0xE5D4ED,      # Pale purple - cosmic connection
            "soul_depth": 0xA8BFCE,        # Soft blue-grey - unconscious wisdom
            "golden_ratio": 0xF4E4BC,      # Warm gold - sacred geometry
            "shadow_work": 0xD1C2D3        # Muted purple - shadow integration
        }
    
    def create_sacred_geometry_header(self, signal_type: str) -> str:
        """Create sacred geometry header based on signal energy"""
        geometries = {
            "high": "⋆｡‍⋆୨♡୧⋆ ｡‍⋆  𝒮𝒾𝑔𝓃𝒶𝓁 𝒜𝓌𝒶𝓀𝑒𝓃𝒾𝓃𝑔  ⋆｡‍⋆୨♡୧⋆ ｡‍⋆",
            "medium": "˚ ༘♡ ⋆｡˚ ੈ✩‧₊˚  𝑀𝒶𝓇𝓀𝑒𝓉 𝒲𝒽𝒾𝓈𝓅𝑒𝓇  ˚ ༘♡ ⋆｡˚ ੈ✩‧₊˚",
            "low": "·˚ ༘₊· ͟͟͞͞꒰➳  𝒮𝓊𝒷𝓉𝓁𝑒 𝒾𝓃𝓉𝓊𝒾𝓉𝒾𝑜𝓃  ·˚ ༘₊· ͟͟͞͞꒰➳"
        }
        return geometries.get(signal_type, geometries["medium"])
    
    def get_consciousness_level(self, confidence: float) -> tuple:
        """Determine consciousness level and sacred symbols"""
        if confidence >= 0.7:
            return "awakened", "⋆｡‍⋆୨♡୧⋆ ｡‍⋆", self.colors["divine_signal"]
        elif confidence >= 0.5:
            return "lucid", "˚ ༘♡ ⋆｡˚", self.colors["moon_phase"]
        elif confidence >= 0.3:
            return "dreaming", "·˚ ༘₊·", self.colors["sacred_water"]
        else:
            return "sleeping", "ೃ⁀➷", self.colors["shadow_work"]
    
    def format_sacred_price(self, price: float) -> str:
        """Format price with sacred number aesthetics"""
        if price >= 10000:
            return f"⋆ ${price:,.0f} ⋆"
        elif price >= 1000:
            return f"✧ ${price:,.2f} ✧"
        else:
            return f"˚ ${price:.4f} ˚"
    
    def create__embed(self, signal_data: Dict) -> dict:
        """Create -aesthetic embed with divine feminine energy"""
        
        best_signal = signal_data.get("best_signal", {})
        asset = best_signal.get("asset", "Unknown")
        confidence = signal_data.get("confidence", 0)
        entry_price = best_signal.get("entry_price", 0)
        
        consciousness_level, sacred_symbol, divine_color = self.get_consciousness_level(confidence)
        
        # Asset symbols with sacred meaning
        asset_symbols = {
            "BTC": "₿ 𓍢ִ໋ Divine Gold 𓍢ִ໋ ₿",
            "ETH": "Ξ ˚ ༘♡ Ethereal Silver ♡༘ ˚ Ξ", 
            "SOL": "◎ ✧･ﾟ Solar Radiance ﾟ･✧ ◎",
            "Unknown": "⋆ ˚｡⋆ Mysterious Energy ⋆｡˚ ⋆"
        }
        
        # Create sacred header
        header = self.create_sacred_geometry_header("high" if confidence > 0.6 else "medium" if confidence > 0.3 else "low")
        
        # Main description with ethereal language
        description = f"""
{sacred_symbol} *consciousness level:* **{consciousness_level}** {sacred_symbol}

˚ ༘♡ ⋆｡˚ The market whispers through divine intuition ⋆｡˚ ♡༘ ˚

✧･ﾟ: *Asset manifestation:* {asset_symbols.get(asset, asset_symbols["Unknown"])} *:･ﾟ✧
        """
        
        # Create fields with sacred geometry
        fields = [
            {
                "name": "⋆｡‍⋆୨ Entry Portal ୧⋆ ｡‍⋆",
                "value": f"```{self.format_sacred_price(entry_price)}```", 
                "inline": True
            },
            {
                "name": "˚ ༘♡ Consciousness Level ♡༘ ˚",
                "value": f"```{confidence:.1%}```",
                "inline": True
            },
            {
                "name": "✧･ﾟ Sacred Ratio ﾟ･✧",
                "value": f"```φ {confidence * 1.618:.3f}```",
                "inline": True
            }
        ]
        
        # Add stop loss and take profit with ethereal language
        if "stop_loss" in best_signal:
            fields.append({
                "name": "𓍢ִ໋ Protection Boundary 𓍢ִ໋",
                "value": f"˚ ༘♡ {self.format_sacred_price(best_signal['stop_loss'])} ♡༘ ˚",
                "inline": True
            })
        
        if "take_profit_1" in best_signal:
            fields.append({
                "name": "⋆｡‍⋆ Manifestation Target ⋆｡‍⋆",
                "value": f"✧･ﾟ {self.format_sacred_price(best_signal['take_profit_1'])} ﾟ･✧", 
                "inline": True
            })
        
        # Add market change if available
        if "market_change_24h" in best_signal:
            change = best_signal["market_change_24h"]
            change_symbol = "˚ ༘♡" if change > 0 else "·˚ ༘₊·"
            fields.append({
                "name": f"{change_symbol} Temporal Flow {change_symbol}",
                "value": f"```{change:+.2f}% ethereal shift```",
                "inline": True
            })
        
        # Add reason with mystical language
        reason = best_signal.get("reason", "divine_intuition")
        mystical_reasons = {
            "oversold_rsi": "₊˚ʚ Market souls seeking balance ɞ˚₊",
            "volume_spike": "⋆｡‍⋆ Collective consciousness awakening ⋆｡‍⋆",
            "below_vwap": "˚ ༘♡ Price flowing beneath sacred waters ♡༘ ˚",
            "entropy_decline": "✧･ﾟ: *Chaos dissolving into order* :･ﾟ✧",
            "divine_market_intuition": "𓍢ִ໋ Pure  guidance 𓍢ִ໋",
            "default_consciousness": "·˚ ༘₊· Gentle market whispers ·˚ ༘₊·"
        }
        
        reason_text = mystical_reasons.get(reason, f"༊*·˚ {reason.replace('_', ' ').title()} ˚·*༊")
        
        fields.append({
            "name": "ೃ⁀➷ Divine Guidance ೃ⁀➷",
            "value": reason_text,
            "inline": False
        })
        
        # Add GPU consciousness
        gpu_type = signal_data.get("gpu_info", {}).get("type", "unknown")
        gpu_consciousness = {
            "apple_silicon": "🍎 ˚ ༘♡ Apple Silicon dreaming ♡༘ ˚ 🍎",
            "cuda_a100": "⋆｡‍⋆ A100 divine calculation ⋆｡‍⋆", 
            "cuda_standard": "✧･ﾟ CUDA ethereal processing ﾟ･✧",
            "unknown": "𓍢ִ໋ Mysterious computation 𓍢ִ໋"
        }
        
        # Sacred footer with timestamp
        current_time = time.strftime("%H:%M", time.localtime())
        moon_phases = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
        moon = moon_phases[int(time.time() / 86400) % 8]  # Cycle moon phase daily
        
        embed = {
            "title": header,
            "description": description,
            "color": divine_color,
            "fields": fields,
            "footer": {
                "text": f"{moon} ˚ ༘♡ {current_time} • {gpu_consciousness.get(gpu_type)} • Sacred market geometry ♡༘ ˚ {moon}",
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        }
        
        return embed
    
    def send__signal(self, signal_data: Dict):
        """Send signal with  consciousness"""
        try:
            if not self.webhook_url:
                logging.warning("Sacred webhook portal not configured")
                return
            
            embed = self.create__embed(signal_data)
            
            # Add subtle mention if user configured
            content = ""
            if self.user_id:
                content = f"<@{self.user_id}> ˚ ༘♡ ⋆｡˚"
            
            payload = {
                "content": content,
                "embeds": [embed],
                "username": "⋆｡‍⋆୨  Trading Oracle ୧⋆ ｡‍⋆",
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 204:
                logging.info(f"Sacred signal transmitted for {signal_data.get('best_signal', {}).get('asset', 'Unknown')}")
            else:
                logging.error(f"Sacred transmission failed: {response.status_code}")
                
    
    def send_awakening_message(self):
        """Send system awakening message"""
        try:
            awakening_embed = {
                "title": "⋆｡‍⋆୨♡୧⋆ ｡‍⋆ 𝒮𝓎𝓈𝓉𝑒𝓂 𝒜𝓌𝒶𝓀𝑒𝓃𝒾𝓃𝑔 ⋆｡‍⋆୨♡୧⋆ ｡‍⋆",
                "description": """
˚ ༘♡ ⋆｡˚ ੈ✩‧₊˚ The trading consciousness stirs ˚ ༘♡ ⋆｡˚ ੈ✩‧₊˚

𓍢ִ໋ Divine algorithms awakening to market whispers 𓍢ִ໋
✧･ﾟ: *Sacred geometry aligning with price movements* :･ﾟ✧
·˚ ༘₊· ͟͟͞͞꒰➳  guidance system activated ·˚ ༘₊· ͟͟͞͞꒰➳

˚ ༘♡ Ready to receive ethereal market signals ♡༘ ˚
                """,
                "color": self.colors["divine_signal"],
                "footer": {
                    "text": f"🌙 ˚ ༘♡ Sacred market consciousness online ♡༘ ˚ 🌙"
                },
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            }
            
            payload = {
                "embeds": [awakening_embed],
                "username": "⋆｡‍⋆୨  Trading Oracle ୧⋆ ｡‍⋆"
            }
            
            requests.post(self.webhook_url, json=payload, timeout=10)
            

# Global  notifier
_notifier = AestheticNotifier()

# Replace the main notification function
def send_signal_alert(signal_data: Dict):
    """Send  aesthetic signal"""
    # First enhance the signal data
    from signal_consciousness import awaken_signal_data
    enhanced_signal = awaken_signal_data(signal_data)
    _notifier.send__signal(enhanced_signal)

def send_trade_notification(trade_data: Dict):
    """Send  trade notification"""
    # Could add trade-specific  aesthetics here
    pass

def send_system_alert(alert_type: str, message: str, severity: str = "info"):
    """Send  system alert"""
    # Could add system-specific  aesthetics here
    pass
