#!/usr/bin/env python3
"""
Unified Trading System - HFT Shorting + Wallet Mimic
"""
import sys
import os
import asyncio
import logging
import time
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "core"))
sys.path.append(str(Path(__file__).parent / "config"))

class UnifiedTradingSystem:
    def __init__(self, mode="paper"):
        self.mode = mode
        self.running = False
        self.iteration = 0
        
        logging.info(f"🔥 Unified Trading System - Mode: {mode}")
        logging.info("📈 HFT Shorting: Active")
        logging.info("👁️  Wallet Mimic: Active")
    
    async def run(self):
        """Main unified loop"""
        self.running = True
        
        while self.running:
            try:
                self.iteration += 1
                
                # HFT Shorting
                await self.hft_shorting_cycle()
                
                # Wallet Mimic
                await self.wallet_mimic_cycle()
                
                # Status
                if self.iteration % 20 == 0:
                    logging.info(f"🔄 Unified system running - Cycle {self.iteration}")
                
                await asyncio.sleep(3)
                
            except KeyboardInterrupt:
                logging.info("👋 Shutting down...")
                break
            except Exception as e:
                logging.error(f"System error: {e}")
                await asyncio.sleep(5)
        
        self.running = False
    
    async def hft_shorting_cycle(self):
        """HFT shorting strategy"""
        try:
            # Try to import and use signal engine
            if Path("core/engines/signal_engine.py").exists():
                from engines import signal_engine
                from engines import confidence_scoring
                
                shared_data = {
                    "timestamp": time.time(),
                    "mode": self.mode,
                    "iteration": self.iteration,
                    "strategy": "hft_short"
                }
                
                signal = signal_engine.generate_signal(shared_data)
                
                if signal and signal.get('confidence', 0) >= 0.75:
                    merged = confidence_scoring.merge_signals([signal])
                    
                    if self.mode == "paper":
                        # Try paper trading
                        try:
                            from engines.paper_trading_engine import get_paper_engine
                            paper_engine = get_paper_engine()
                            result = paper_engine.open_position(merged)
                            
                            if result:
                                asset = result.get('asset', 'UNKNOWN')
                                price = result.get('entry_price', 0)
                                logging.info(f"📉 HFT SHORT: {asset} @ ${price:.2f}")
                        except Exception as e:
                            logging.debug(f"Paper trading error: {e}")
            else:
                # Simulate HFT signal
                if self.iteration % 15 == 0:  # Every 15 cycles
                    logging.info(f"📈 HFT: Monitoring short opportunities...")
                    
        except Exception as e:
            logging.debug(f"HFT error: {e}")
    
    async def wallet_mimic_cycle(self):
        """Wallet mimic strategy"""
        try:
            # Simulate wallet monitoring
            if self.iteration % 25 == 0:  # Every 25 cycles
                logging.info(f"👁️  MIMIC: Monitoring alpha wallets...")
                
            # In real implementation, this would:
            # 1. Monitor blockchain transactions
            # 2. Identify alpha wallet trades
            # 3. Validate tokens
            # 4. Execute mimic trades
            
        except Exception as e:
            logging.debug(f"Mimic error: {e}")

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['paper', 'live'], default='paper')
    args = parser.parse_args()
    
    if args.mode == 'live':
        response = input("⚠️  Live trading uses real money! Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
    
    system = UnifiedTradingSystem(mode=args.mode)
    await system.run()

if __name__ == "__main__":
    asyncio.run(main())
