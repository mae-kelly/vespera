import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pandas as pd
import asyncio
import json
import time
import logging
import hashlib
import hmac
import base64
import requests
import websockets
from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import Dict, List, Set, Optional, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import csv
import os
from decimal import Decimal
import aiohttp
from eth_abi import decode_abi
from sklearn.preprocessing import StandardScaler
import pickle
from collections import deque
import math

# GPU Detection - A100 preferred, M1 MPS fallback, NO CPU allowed
def get_optimal_device():
    if torch.cuda.is_available():
        device = torch.device("cuda")
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        torch.backends.cudnn.benchmark = True
        logging.info(f"🚀 CUDA GPU: {gpu_name} ({gpu_memory:.1f}GB)")
        return device
    
    # Try Apple M1/M2 MPS
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        try:
            device = torch.device("mps")
            # Test MPS functionality
            test_tensor = torch.zeros(1, device=device)
            test_tensor = test_tensor + 1
            logging.info("🍎 Apple M1/M2 MPS GPU detected and functional")
            return device
        except Exception as e:
            logging.error(f"MPS detected but not functional: {e}")
    
    # Try alternative MPS detection methods
    try:
        import platform
        if platform.system() == "Darwin":  # macOS
            # Force MPS if on Mac
            if torch.has_mps:
                device = torch.device("mps")
                logging.info("🍎 Forcing MPS on macOS")
                return device
    except:
        pass
    
    # Try direct MPS creation
    try:
        device = torch.device("mps")
        torch.zeros(1, device=device)
        logging.info("🍎 MPS device created successfully")
        return device
    except:
        pass
    
    raise RuntimeError("❌ NO GPU DETECTED - A100 CUDA or Apple M1 MPS required. CPU NOT ALLOWED.")

DEVICE = get_optimal_device()

# Verify GPU is working
try:
    test_tensor = torch.randn(100, 100, device=DEVICE)
    test_result = torch.mm(test_tensor, test_tensor.T)
    logging.info(f"✅ GPU verification passed on {DEVICE}")
except Exception as e:
    raise RuntimeError(f"❌ GPU test failed: {e}")

@dataclass
class TradeSignal:
    action: str
    confidence: float
    asset: str
    predicted_return: float
    risk_score: float
    position_size: float
    reasoning: str

class DeepTradingNetwork(nn.Module):
    def __init__(self, input_dim=256, hidden_dims=[1024, 512, 256], output_dim=5):
        super(DeepTradingNetwork, self).__init__()
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(inplace=True),
                nn.Dropout(0.15)
            ])
            prev_dim = hidden_dim
        
        self.feature_extractor = nn.Sequential(*layers)
        
        # Separate output heads
        self.action_head = nn.Linear(hidden_dims[-1], 3)  # buy, sell, hold
        self.confidence_head = nn.Linear(hidden_dims[-1], 1)
        self.return_head = nn.Linear(hidden_dims[-1], 1)
        self.risk_head = nn.Linear(hidden_dims[-1], 1)
        self.size_head = nn.Linear(hidden_dims[-1], 1)
        
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
            if module.bias is not None:
                torch.nn.init.constant_(module.bias, 0)
    
    def forward(self, x):
        features = self.feature_extractor(x)
        
        action_logits = self.action_head(features)
        confidence = torch.sigmoid(self.confidence_head(features))
        predicted_return = torch.tanh(self.return_head(features)) * 10.0  # Scale to ±10x
        risk_score = torch.sigmoid(self.risk_head(features))
        position_size = torch.sigmoid(self.size_head(features)) * 0.5  # Max 50% position
        
        return {
            'action_logits': action_logits,
            'confidence': confidence.squeeze(),
            'predicted_return': predicted_return.squeeze(),
            'risk_score': risk_score.squeeze(),
            'position_size': position_size.squeeze()
        }

class RealDataCollector:
    def __init__(self):
        self.okx_api_key = os.getenv("OKX_API_KEY")
        self.okx_secret = os.getenv("OKX_SECRET_KEY")
        self.okx_passphrase = os.getenv("OKX_PASSPHRASE")
        
        if not all([self.okx_api_key, self.okx_secret, self.okx_passphrase]):
            raise RuntimeError("OKX API credentials required")
        
        self.base_url = "https://www.okx.com"
        self.session = requests.Session()
        self.rate_limiter = asyncio.Semaphore(10)
        
        # Ethereum connection for real wallet data
        self.eth_rpc = os.getenv("ETHEREUM_RPC_URL")
        if self.eth_rpc and "YOUR_KEY" not in self.eth_rpc:
            self.w3 = Web3(Web3.HTTPProvider(self.eth_rpc))
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            self.eth_enabled = self.w3.is_connected()
        else:
            self.eth_enabled = False
        
        self.etherscan_api = os.getenv("ETHERSCAN_API_KEY")
        
        logging.info(f"Real data collector initialized - ETH: {self.eth_enabled}")
    
    def _okx_signature(self, timestamp: str, method: str, request_path: str, body: str = "") -> str:
        message = f"{timestamp}{method}{request_path}{body}"
        signature = base64.b64encode(
            hmac.new(self.okx_secret.encode(), message.encode(), hashlib.sha256).digest()
        ).decode()
        return signature
    
    def _okx_headers(self, method: str, request_path: str, body: str = "") -> Dict[str, str]:
        timestamp = str(int(time.time() * 1000))
        signature = self._okx_signature(timestamp, method, request_path, body)
        return {
            "OK-ACCESS-KEY": self.okx_api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.okx_passphrase,
            "Content-Type": "application/json"
        }
    
    async def get_real_historical_data(self, symbols: List[str], days: int = 90) -> Dict[str, pd.DataFrame]:
        """Get REAL historical data from OKX API - NO SIMULATION"""
        logging.info(f"Fetching REAL historical data from OKX for {len(symbols)} symbols...")
        
        historical_data = {}
        
        for symbol in symbols:
            async with self.rate_limiter:
                try:
                    request_path = "/api/v5/market/history-candles"
                    params = {
                        "instId": f"{symbol}-USDT",
                        "bar": "1H",
                        "limit": str(min(days * 24, 1440))  # OKX limit
                    }
                    
                    headers = self._okx_headers("GET", request_path)
                    
                    response = self.session.get(
                        f"{self.base_url}{request_path}",
                        headers=headers,
                        params=params,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("code") == "0":
                            candles = data.get("data", [])
                            
                            if len(candles) > 0:
                                df = pd.DataFrame(candles, columns=[
                                    'timestamp', 'open', 'high', 'low', 'close', 'volume'
                                ])
                                
                                df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
                                for col in ['open', 'high', 'low', 'close', 'volume']:
                                    df[col] = df[col].astype(float)
                                
                                df = df.sort_values('timestamp').reset_index(drop=True)
                                historical_data[symbol] = df
                                
                                logging.info(f"Collected {len(df)} REAL data points for {symbol}")
                            else:
                                logging.error(f"No historical data returned for {symbol}")
                        else:
                            logging.error(f"OKX API error for {symbol}: {data}")
                    else:
                        logging.error(f"HTTP error {response.status_code} for {symbol}")
                    
                    await asyncio.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    logging.error(f"Failed to get data for {symbol}: {e}")
        
        if not historical_data:
            raise RuntimeError("Failed to collect any historical data from OKX")
        
        return historical_data
    
    async def get_real_wallet_transactions(self, wallet_addresses: List[str]) -> pd.DataFrame:
        """Get REAL wallet transaction data from Etherscan API - NO SIMULATION"""
        if not self.etherscan_api:
            logging.error("Etherscan API key required for real wallet data")
            return pd.DataFrame()
        
        logging.info(f"Fetching REAL wallet transactions for {len(wallet_addresses)} wallets...")
        
        all_transactions = []
        
        for wallet_address in wallet_addresses:
            try:
                # Get normal transactions
                url = "https://api.etherscan.io/api"
                params = {
                    "module": "account",
                    "action": "txlist",
                    "address": wallet_address,
                    "startblock": 0,
                    "endblock": 99999999,
                    "page": 1,
                    "offset": 1000,
                    "sort": "desc",
                    "apikey": self.etherscan_api
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        transactions = data.get("result", [])
                        
                        for tx in transactions[:100]:  # Last 100 transactions
                            all_transactions.append({
                                'wallet_address': wallet_address,
                                'tx_hash': tx.get('hash'),
                                'timestamp': int(tx.get('timeStamp', 0)),
                                'from_address': tx.get('from', '').lower(),
                                'to_address': tx.get('to', '').lower(),
                                'value_eth': float(tx.get('value', 0)) / 1e18,
                                'gas_used': int(tx.get('gasUsed', 0)),
                                'gas_price': int(tx.get('gasPrice', 0)),
                                'is_error': tx.get('isError') == '1'
                            })
                        
                        logging.info(f"Collected {len(transactions)} REAL transactions for {wallet_address[:10]}...")
                    else:
                        logging.error(f"Etherscan error for {wallet_address}: {data}")
                
                await asyncio.sleep(0.2)  # Etherscan rate limiting
                
            except Exception as e:
                logging.error(f"Failed to get transactions for {wallet_address}: {e}")
        
        if not all_transactions:
            logging.error("No real wallet transaction data collected")
            return pd.DataFrame()
        
        df = pd.DataFrame(all_transactions)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        logging.info(f"Collected {len(df)} REAL wallet transactions total")
        return df
    
    async def get_current_market_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get current REAL market data from OKX"""
        current_data = {}
        
        for symbol in symbols:
            async with self.rate_limiter:
                try:
                    # Get ticker data
                    request_path = "/api/v5/market/ticker"
                    params = {"instId": f"{symbol}-USDT"}
                    headers = self._okx_headers("GET", request_path)
                    
                    response = self.session.get(
                        f"{self.base_url}{request_path}",
                        headers=headers,
                        params=params,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("code") == "0" and data.get("data"):
                            ticker = data["data"][0]
                            current_data[symbol] = {
                                'price': float(ticker.get('last', 0)),
                                'volume_24h': float(ticker.get('vol24h', 0)),
                                'change_24h': float(ticker.get('chg24h', 0)),
                                'high_24h': float(ticker.get('high24h', 0)),
                                'low_24h': float(ticker.get('low24h', 0)),
                                'timestamp': time.time()
                            }
                    
                    await asyncio.sleep(0.05)  # Small delay
                    
                except Exception as e:
                    logging.error(f"Failed to get current data for {symbol}: {e}")
        
        return current_data

class FeatureEngineer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.lookback_window = 48  # 48 hours
        
    def create_features_from_real_data(self, price_data: Dict[str, pd.DataFrame], 
                                      wallet_data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Create ML features from REAL API data only"""
        logging.info("Engineering features from real data...")
        
        all_features = []
        all_targets = []
        
        for symbol, df in price_data.items():
            if len(df) < self.lookback_window + 1:
                continue
            
            # Calculate technical indicators on REAL data
            df = df.copy()
            df['returns'] = df['close'].pct_change()
            df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
            
            # Moving averages
            for window in [5, 10, 20]:
                df[f'ma_{window}'] = df['close'].rolling(window).mean()
                df[f'ma_ratio_{window}'] = df['close'] / df[f'ma_{window}']
            
            # Volatility
            for window in [5, 10, 20]:
                df[f'volatility_{window}'] = df['returns'].rolling(window).std()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['close'].ewm(span=12).mean()
            exp2 = df['close'].ewm(span=26).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(20).mean()
            bb_std = df['close'].rolling(20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Create feature vectors
            feature_columns = [
                'returns', 'log_returns', 'ma_ratio_5', 'ma_ratio_10', 'ma_ratio_20',
                'volatility_5', 'volatility_10', 'volatility_20', 'rsi', 'macd',
                'macd_signal', 'bb_position', 'volume_ratio'
            ]
            
            # Create sequences
            for i in range(self.lookback_window, len(df) - 1):
                features = []
                
                # Price-based features
                for col in feature_columns:
                    if col in df.columns:
                        window_data = df[col].iloc[i-self.lookback_window:i].values
                        if not np.isnan(window_data).any():
                            features.extend([
                                np.mean(window_data),
                                np.std(window_data),
                                np.min(window_data),
                                np.max(window_data),
                                window_data[-1]  # Current value
                            ])
                        else:
                            features.extend([0, 0, 0, 0, 0])
                    else:
                        features.extend([0, 0, 0, 0, 0])
                
                # Add wallet sentiment if available
                current_time = df.iloc[i]['timestamp']
                wallet_features = self._get_wallet_features_at_time(wallet_data, current_time)
                features.extend(wallet_features)
                
                # Calculate future return as target
                future_return = (df.iloc[i+1]['close'] - df.iloc[i]['close']) / df.iloc[i]['close']
                
                if len(features) > 0 and not np.isnan(future_return):
                    all_features.append(features)
                    all_targets.append([
                        1 if future_return > 0.001 else (2 if future_return < -0.001 else 0),  # Action
                        min(abs(future_return) * 10, 1.0),  # Confidence
                        future_return,  # Return
                        min(abs(future_return) * 5, 1.0)  # Risk
                    ])
        
        if not all_features:
            raise RuntimeError("No valid features created from real data")
        
        features_array = np.array(all_features, dtype=np.float32)
        targets_array = np.array(all_targets, dtype=np.float32)
        
        # Normalize features
        features_array = self.scaler.fit_transform(features_array)
        
        logging.info(f"Created {len(features_array)} feature vectors from real data")
        
        return features_array, targets_array
    
    def _get_wallet_features_at_time(self, wallet_data: pd.DataFrame, timestamp: pd.Timestamp) -> List[float]:
        """Extract wallet activity features at specific time"""
        if wallet_data.empty:
            return [0, 0, 0, 0]  # Default values if no wallet data
        
        # Look at wallet activity in last 24 hours
        recent_time = timestamp - pd.Timedelta(hours=24)
        recent_txs = wallet_data[wallet_data['datetime'] >= recent_time]
        
        if recent_txs.empty:
            return [0, 0, 0, 0]
        
        # Calculate wallet sentiment features
        total_volume = recent_txs['value_eth'].sum()
        tx_count = len(recent_txs)
        avg_gas_price = recent_txs['gas_price'].mean()
        error_rate = recent_txs['is_error'].mean()
        
        return [total_volume, tx_count, avg_gas_price / 1e9, error_rate]  # Normalize gas price

class MLTradingSystem:
    def __init__(self):
        self.model = DeepTradingNetwork().to(DEVICE)
        self.optimizer = optim.AdamW(self.model.parameters(), lr=0.001, weight_decay=0.01)
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=1000)
        
        self.data_collector = RealDataCollector()
        self.feature_engineer = FeatureEngineer()
        
        self.training_data = deque(maxlen=10000)  # Keep last 10k training samples
        self.model_trained = False
        
        # Trading state
        self.positions = {}
        self.capital = 1000.0
        self.trade_history = []
        
        logging.info("ML Trading System initialized")
    
    async def initial_training(self):
        """Perform initial training on historical data"""
        logging.info("Starting initial training on REAL historical data...")
        
        # Collect real historical data
        symbols = ["BTC", "ETH", "SOL", "LINK", "UNI", "AAVE"]
        price_data = await self.data_collector.get_real_historical_data(symbols, days=90)
        
        if not price_data:
            raise RuntimeError("Failed to collect historical price data")
        
        # Load alpha wallets and get their transaction history
        wallet_addresses = []
        try:
            with open("alpha_wallets.json", "r") as f:
                wallets = json.load(f)["wallets"]
                wallet_addresses = [w["address"] for w in wallets[:10]]  # Top 10 wallets
        except FileNotFoundError:
            logging.warning("No alpha wallets found")
        
        wallet_data = await self.data_collector.get_real_wallet_transactions(wallet_addresses)
        
        # Create features from real data
        features, targets = self.feature_engineer.create_features_from_real_data(price_data, wallet_data)
        
        # Convert to tensors
        X = torch.tensor(features, dtype=torch.float32, device=DEVICE)
        y = torch.tensor(targets, dtype=torch.float32, device=DEVICE)
        
        # Create data loader
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=128, shuffle=True)
        
        # Training loop
        self.model.train()
        num_epochs = 100
        
        for epoch in range(num_epochs):
            total_loss = 0
            
            for batch_features, batch_targets in dataloader:
                self.optimizer.zero_grad()
                
                # Forward pass
                outputs = self.model(batch_features)
                
                # Calculate losses
                action_loss = F.cross_entropy(
                    outputs['action_logits'], 
                    batch_targets[:, 0].long()
                )
                confidence_loss = F.mse_loss(outputs['confidence'], batch_targets[:, 1])
                return_loss = F.mse_loss(outputs['predicted_return'], batch_targets[:, 2])
                risk_loss = F.mse_loss(outputs['risk_score'], batch_targets[:, 3])
                
                total_loss_batch = action_loss + confidence_loss + return_loss + risk_loss
                
                # Backward pass
                total_loss_batch.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                
                total_loss += total_loss_batch.item()
            
            self.scheduler.step()
            
            if epoch % 10 == 0:
                avg_loss = total_loss / len(dataloader)
                logging.info(f"Epoch {epoch}/{num_epochs}, Loss: {avg_loss:.4f}")
        
        self.model_trained = True
        logging.info("Initial training completed on REAL data")
        
        # Save model
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scaler': self.feature_engineer.scaler
        }, 'trained_model.pth')
    
    async def generate_trading_signal(self, symbol: str) -> Optional[TradeSignal]:
        """Generate trading signal using trained model"""
        if not self.model_trained:
            return None
        
        try:
            # Get current market data
            current_data = await self.data_collector.get_current_market_data([symbol])
            if symbol not in current_data:
                return None
            
            # Get recent historical data for feature engineering
            recent_data = await self.data_collector.get_real_historical_data([symbol], days=7)
            if symbol not in recent_data or len(recent_data[symbol]) < 48:
                return None
            
            # Create features
            df = recent_data[symbol]
            wallet_data = pd.DataFrame()  # Could add recent wallet data here
            
            features, _ = self.feature_engineer.create_features_from_real_data({symbol: df}, wallet_data)
            
            if len(features) == 0:
                return None
            
            # Use latest feature vector
            feature_vector = torch.tensor(features[-1:], dtype=torch.float32, device=DEVICE)
            
            # Generate prediction
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(feature_vector)
                
                action_probs = F.softmax(outputs['action_logits'], dim=1)
                action_idx = torch.argmax(action_probs, dim=1).item()
                action_confidence = torch.max(action_probs, dim=1)[0].item()
                
                actions = ["buy", "hold", "sell"]
                action = actions[action_idx]
                
                confidence = outputs['confidence'].item()
                predicted_return = outputs['predicted_return'].item()
                risk_score = outputs['risk_score'].item()
                position_size = outputs['position_size'].item()
                
                # Only generate signals with high confidence
                if confidence > 0.75 and action != "hold":
                    return TradeSignal(
                        action=action,
                        confidence=confidence,
                        asset=symbol,
                        predicted_return=predicted_return,
                        risk_score=risk_score,
                        position_size=position_size,
                        reasoning=f"ML_prediction_conf_{confidence:.3f}"
                    )
        
        except Exception as e:
            logging.error(f"Signal generation error for {symbol}: {e}")
        
        return None
    
    async def execute_trade(self, signal: TradeSignal) -> bool:
        """Execute trade based on ML signal"""
        try:
            # Get current price
            current_data = await self.data_collector.get_current_market_data([signal.asset])
            if signal.asset not in current_data:
                return False
            
            current_price = current_data[signal.asset]['price']
            
            # Calculate position size
            position_value = self.capital * signal.position_size
            
            # For paper trading mode
            if os.getenv("MODE", "paper") == "paper":
                logging.info(f"📄 PAPER ML TRADE: {signal.action} {signal.asset} @ ${current_price:.2f}")
                logging.info(f"   Confidence: {signal.confidence:.3f}, Predicted Return: {signal.predicted_return:.3f}")
                return True
            else:
                # Real trading would execute here via OKX API
                logging.info(f"🔴 LIVE ML TRADE: {signal.action} {signal.asset} @ ${current_price:.2f}")
                return True
                
        except Exception as e:
            logging.error(f"Trade execution error: {e}")
            return False
    
    async def continuous_learning(self):
        """Continuously retrain model on new data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Retrain every hour
                
                if len(self.trade_history) > 10:  # Need some trade history
                    logging.info("Retraining model on recent data...")
                    
                    # Get fresh data
                    symbols = ["BTC", "ETH", "SOL"]
                    recent_data = await self.data_collector.get_real_historical_data(symbols, days=7)
                    
                    if recent_data:
                        # Quick retrain on recent data
                        features, targets = self.feature_engineer.create_features_from_real_data(recent_data, pd.DataFrame())
                        
                        if len(features) > 0:
                            X = torch.tensor(features, dtype=torch.float32, device=DEVICE)
                            y = torch.tensor(targets, dtype=torch.float32, device=DEVICE)
                            
                            # Fine-tune model
                            self.model.train()
                            for _ in range(10):  # Quick fine-tuning
                                self.optimizer.zero_grad()
                                outputs = self.model(X)
                                
                                action_loss = F.cross_entropy(outputs['action_logits'], y[:, 0].long())
                                confidence_loss = F.mse_loss(outputs['confidence'], y[:, 1])
                                return_loss = F.mse_loss(outputs['predicted_return'], y[:, 2])
                                risk_loss = F.mse_loss(outputs['risk_score'], y[:, 3])
                                
                                total_loss = action_loss + confidence_loss + return_loss + risk_loss
                                total_loss.backward()
                                self.optimizer.step()
                            
                            logging.info("Model retrained on fresh data")
                
            except Exception as e:
                logging.error(f"Continuous learning error: {e}")
    
    async def run_trading_system(self):
        """Main trading loop"""
        logging.info("Starting ML-based trading system...")
        
        # Initial training
        await self.initial_training()
        
        # Start continuous learning
        learning_task = asyncio.create_task(self.continuous_learning())
        
        # Main trading loop
        symbols = ["BTC", "ETH", "SOL"]
        
        while True:
            try:
                for symbol in symbols:
                    signal = await self.generate_trading_signal(symbol)
                    if signal:
                        await self.execute_trade(signal)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logging.info("Shutting down ML trading system...")
                learning_task.cancel()
                break
            except Exception as e:
                logging.error(f"Trading loop error: {e}")
                await asyncio.sleep(60)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    required_vars = ["OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE"]
    for var in required_vars:
        if not os.getenv(var):
            logging.error(f"Required environment variable {var} not set")
            return
    
    system = MLTradingSystem()
    await system.run_trading_system()

if __name__ == "__main__":
    asyncio.run(main())
