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
import re

@dataclass
class AlphaWallet:
    address: str
    avg_multiplier: float
    avg_hold_time: int
    trades_per_day: float
    success_rate: float
    last_activity: float

@dataclass
class TokenTrade:
    token_address: str
    wallet_address: str
    amount_eth: float
    token_amount: float
    tx_hash: str
    timestamp: float
    confidence_score: float

class EthereumMonitor:
    def __init__(self):
        self.rpc_url = os.getenv("ETHEREUM_RPC_URL", "https://eth-mainnet.alchemyapi.io/v2/YOUR_KEY")
        self.ws_url = os.getenv("ETHEREUM_WS_URL", "wss://eth-mainnet.alchemyapi.io/v2/YOUR_KEY")
        
        if "YOUR_KEY" in self.rpc_url:
            raise RuntimeError("ETHEREUM_RPC_URL not configured")
        
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        if not self.w3.is_connected():
            raise RuntimeError("Failed to connect to Ethereum network")
        
        self.uniswap_v2_router = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
        self.uniswap_v3_router = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
        self.sushiswap_router = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
        
        self.dex_routers = {
            self.uniswap_v2_router.lower(),
            self.uniswap_v3_router.lower(),
            self.sushiswap_router.lower()
        }
        
        self.swap_method_ids = {
            "0x7ff36ab5",  # swapExactETHForTokens
            "0x18cbafe5",  # swapExactETHForTokensSupportingFeeOnTransferTokens
            "0x38ed1739",  # swapExactTokensForTokens
            "0xb6f9de95",  # swapExactETHForTokensOut
            "0x414bf389",  # exactInputSingle (Uniswap V3)
        }
        
        logging.info("Ethereum monitor initialized")
    
    async def monitor_pending_transactions(self, alpha_wallets: Set[str], callback):
        while True:
            try:
                async with websockets.connect(self.ws_url) as websocket:
                    subscribe_msg = {
                        "id": 1,
                        "method": "eth_subscribe",
                        "params": ["pendingTransactions"]
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    logging.info("WebSocket connected - monitoring pending transactions")
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            if "params" in data and "result" in data["params"]:
                                tx_hash = data["params"]["result"]
                                await self._process_pending_tx(tx_hash, alpha_wallets, callback)
                        except Exception as e:
                            logging.error(f"Transaction processing error: {e}")
                            
            except Exception as e:
                logging.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)
    
    async def _process_pending_tx(self, tx_hash: str, alpha_wallets: Set[str], callback):
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            from_address = tx["from"].lower()
            
            if from_address not in alpha_wallets:
                return
            
            to_address = tx.get("to")
            if not to_address:
                return
            
            to_address = to_address.lower()
            
            if to_address not in self.dex_routers:
                return
            
            input_data = tx["input"].hex()
            method_id = input_data[:10]
            
            if method_id not in self.swap_method_ids:
                return
            
            token_info = self._decode_swap_transaction(input_data, method_id)
            if token_info:
                token_info["wallet_address"] = from_address
                token_info["tx_hash"] = tx_hash
                token_info["timestamp"] = time.time()
                await callback(token_info)
                
        except Exception as e:
            logging.debug(f"TX processing error {tx_hash}: {e}")
    
    def _decode_swap_transaction(self, input_data: str, method_id: str) -> Optional[Dict]:
        try:
            if method_id == "0x7ff36ab5":  # swapExactETHForTokens
                decoded = decode_abi(
                    ['uint256', 'address[]', 'address', 'uint256'],
                    bytes.fromhex(input_data[10:])
                )
                amount_out_min, path, to, deadline = decoded
                if len(path) >= 2:
                    return {
                        "token_address": path[-1],
                        "eth_amount": 0.0,  # Will get from tx value
                        "method": "swapExactETHForTokens"
                    }
            
            elif method_id == "0x38ed1739":  # swapExactTokensForTokens
                decoded = decode_abi(
                    ['uint256', 'uint256', 'address[]', 'address', 'uint256'],
                    bytes.fromhex(input_data[10:])
                )
                amount_in, amount_out_min, path, to, deadline = decoded
                if len(path) >= 2 and path[0].lower() == "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":  # WETH
                    return {
                        "token_address": path[-1],
                        "eth_amount": amount_in / 10**18,
                        "method": "swapExactTokensForTokens"
                    }
        except Exception:
            pass
        
        return None
    
    def get_token_info(self, token_address: str) -> Dict:
        try:
            token_address = Web3.to_checksum_address(token_address)
            
            # Basic ERC20 ABI
            erc20_abi = [
                {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
            ]
            
            contract = self.w3.eth.contract(address=token_address, abi=erc20_abi)
            
            return {
                "address": token_address,
                "name": contract.functions.name().call(),
                "symbol": contract.functions.symbol().call(),
                "decimals": contract.functions.decimals().call(),
                "total_supply": contract.functions.totalSupply().call()
            }
        except Exception as e:
            logging.error(f"Token info error for {token_address}: {e}")
            return {}

class OKXDEXConnector:
    def __init__(self):
        self.api_key = os.getenv("OKX_API_KEY")
        self.secret_key = os.getenv("OKX_SECRET_KEY")
        self.passphrase = os.getenv("OKX_PASSPHRASE")
        
        if not all([self.api_key, self.secret_key, self.passphrase]):
            raise RuntimeError("OKX API credentials not configured")
        
        self.base_url = "https://www.okx.com"
        self.session = requests.Session()
        logging.info("OKX DEX connector initialized")
    
    def _generate_signature(self, timestamp: str, method: str, request_path: str, body: str = "") -> str:
        message = f"{timestamp}{method}{request_path}{body}"
        signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()
        return signature
    
    def _get_headers(self, method: str, request_path: str, body: str = "") -> Dict[str, str]:
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, request_path, body)
        
        return {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }
    
    async def check_token_tradeable(self, token_address: str) -> bool:
        request_path = f"/api/v5/dex/tokens"
        headers = self._get_headers("GET", request_path)
        
        try:
            response = self.session.get(f"{self.base_url}{request_path}", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "0":
                    tokens = data.get("data", [])
                    for token in tokens:
                        if token.get("tokenAddress", "").lower() == token_address.lower():
                            return True
        except Exception as e:
            logging.error(f"Token tradeable check error: {e}")
        
        return False
    
    async def get_liquidity_depth(self, token_address: str) -> float:
        request_path = f"/api/v5/dex/liquidity"
        params = {"tokenAddress": token_address}
        headers = self._get_headers("GET", request_path)
        
        try:
            response = self.session.get(
                f"{self.base_url}{request_path}", 
                headers=headers, 
                params=params, 
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "0":
                    liquidity_data = data.get("data", [{}])[0]
                    base_liquidity = float(liquidity_data.get("baseLiquidity", 0))
                    quote_liquidity = float(liquidity_data.get("quoteLiquidity", 0))
                    return base_liquidity + quote_liquidity
        except Exception as e:
            logging.error(f"Liquidity depth error: {e}")
        
        return 0.0
    
    async def execute_token_buy(self, token_address: str, eth_amount: float) -> Optional[Dict]:
        request_path = "/api/v5/dex/trade"
        
        trade_data = {
            "chainId": "1",
            "fromTokenAddress": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
            "toTokenAddress": token_address,
            "amount": str(int(eth_amount * 10**18)),
            "slippage": "10",  # 10% max slippage
            "userWalletAddress": os.getenv("ETHEREUM_WALLET_ADDRESS"),
            "referrer": "wallet_mimic_bot"
        }
        
        body = json.dumps(trade_data)
        headers = self._get_headers("POST", request_path, body)
        
        try:
            response = self.session.post(
                f"{self.base_url}{request_path}", 
                headers=headers, 
                data=body, 
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "0":
                    return data.get("data", [{}])[0]
        except Exception as e:
            logging.error(f"Token buy execution error: {e}")
        
        return None

class TokenValidator:
    def __init__(self):
        self.etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
        self.min_liquidity = 50000.0
        self.max_slippage = 0.10
        self.blacklisted_tokens = self._load_blacklist()
        
    def _load_blacklist(self) -> Set[str]:
        try:
            with open("rugdex_blacklist.csv", "r") as f:
                reader = csv.reader(f)
                return set(row[0].lower() for row in reader if row)
        except FileNotFoundError:
            return set()
    
    async def validate_token(self, token_address: str, liquidity: float) -> bool:
        if token_address.lower() in self.blacklisted_tokens:
            logging.warning(f"Token {token_address} is blacklisted")
            return False
        
        if liquidity < self.min_liquidity:
            logging.warning(f"Token {token_address} liquidity too low: ${liquidity}")
            return False
        
        if not await self._verify_contract_source(token_address):
            logging.warning(f"Token {token_address} failed source verification")
            return False
        
        return True
    
    async def _verify_contract_source(self, token_address: str) -> bool:
        if not self.etherscan_api_key:
            return True  # Skip if no API key
        
        url = "https://api.etherscan.io/api"
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": token_address,
            "apikey": self.etherscan_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    result = data.get("result", [{}])[0]
                    source_code = result.get("SourceCode", "")
                    
                    if not source_code:
                        return False
                    
                    # Check for dangerous patterns
                    dangerous_patterns = [
                        "blacklist", "pause", "setFees", "cooldown", 
                        "antiSell", "rebase", "mint(", "burn(",
                        "onlyOwner", "_transfer"
                    ]
                    
                    source_lower = source_code.lower()
                    for pattern in dangerous_patterns:
                        if pattern.lower() in source_lower:
                            logging.warning(f"Token {token_address} contains dangerous pattern: {pattern}")
                            return False
                    
                    return True
        except Exception as e:
            logging.error(f"Source verification error: {e}")
        
        return False

class CapitalManager:
    def __init__(self, initial_capital: float = 1000.0):
        self.total_capital = initial_capital
        self.available_capital = initial_capital
        self.deployed_capital = 0.0
        self.max_position_pct = 0.33
        self.positions = {}
        
    def calculate_position_size(self, wallet_alpha_score: float, confidence: float) -> float:
        base_size = self.available_capital * 0.1  # 10% base
        alpha_multiplier = min(wallet_alpha_score / 10.0, 2.0)
        confidence_multiplier = confidence
        
        position_size = base_size * alpha_multiplier * confidence_multiplier
        max_position = self.total_capital * self.max_position_pct
        
        return min(position_size, max_position, self.available_capital * 0.9)
    
    def allocate_capital(self, amount: float, trade_id: str) -> bool:
        if amount > self.available_capital:
            return False
        
        self.available_capital -= amount
        self.deployed_capital += amount
        self.positions[trade_id] = amount
        return True
    
    def release_capital(self, trade_id: str, pnl: float):
        if trade_id in self.positions:
            original_amount = self.positions.pop(trade_id)
            self.deployed_capital -= original_amount
            self.available_capital += (original_amount + pnl)
            self.total_capital += pnl

class WalletMimicSystem:
    def __init__(self):
        self.alpha_wallets = self._load_alpha_wallets()
        self.eth_monitor = EthereumMonitor()
        self.okx_connector = OKXDEXConnector()
        self.token_validator = TokenValidator()
        self.capital_manager = CapitalManager()
        
        self.trade_log = []
        self.running = False
        
        logging.info(f"Loaded {len(self.alpha_wallets)} alpha wallets")
    
    def _load_alpha_wallets(self) -> Dict[str, AlphaWallet]:
        try:
            with open("alpha_wallets.json", "r") as f:
                data = json.load(f)
                wallets = {}
                
                for wallet_data in data.get("wallets", []):
                    success_rate = wallet_data.get("success_rate", 0)
                    if success_rate > 0.60:  # Only high-success wallets
                        wallet = AlphaWallet(
                            address=wallet_data["address"].lower(),
                            avg_multiplier=wallet_data.get("avg_multiplier", 1.0),
                            avg_hold_time=wallet_data.get("avg_hold_time", 3600),
                            trades_per_day=wallet_data.get("trades_per_day", 0),
                            success_rate=success_rate,
                            last_activity=0.0
                        )
                        wallets[wallet.address] = wallet
                
                return wallets
        except FileNotFoundError:
            logging.error("alpha_wallets.json not found")
            return {}
    
    async def process_wallet_transaction(self, tx_info: Dict):
        try:
            wallet_address = tx_info["wallet_address"]
            token_address = tx_info["token_address"]
            
            wallet = self.alpha_wallets.get(wallet_address)
            if not wallet:
                return
            
            # Update wallet activity
            wallet.last_activity = time.time()
            
            # Check if token is tradeable on OKX
            is_tradeable = await self.okx_connector.check_token_tradeable(token_address)
            if not is_tradeable:
                logging.info(f"Token {token_address} not tradeable on OKX")
                return
            
            # Get liquidity depth
            liquidity = await self.okx_connector.get_liquidity_depth(token_address)
            
            # Validate token
            is_valid = await self.token_validator.validate_token(token_address, liquidity)
            if not is_valid:
                return
            
            # Calculate confidence score
            confidence = self._calculate_confidence(wallet, liquidity)
            if confidence < 0.75:
                logging.info(f"Low confidence ({confidence:.2f}) for {token_address}")
                return
            
            # Calculate position size
            position_size = self.capital_manager.calculate_position_size(
                wallet.avg_multiplier, confidence
            )
            
            if position_size < 0.01:  # Minimum 0.01 ETH
                return
            
            # Execute trade
            await self._execute_mimic_trade(
                wallet_address, token_address, position_size, confidence
            )
            
        except Exception as e:
            logging.error(f"Transaction processing error: {e}")
    
    def _calculate_confidence(self, wallet: AlphaWallet, liquidity: float) -> float:
        base_confidence = wallet.success_rate
        multiplier_bonus = min(wallet.avg_multiplier / 20.0, 0.2)
        liquidity_bonus = min(liquidity / 100000.0, 0.1)
        
        return min(base_confidence + multiplier_bonus + liquidity_bonus, 0.95)
    
    async def _execute_mimic_trade(self, wallet_address: str, token_address: str, 
                                   eth_amount: float, confidence: float):
        try:
            trade_id = f"{token_address}_{int(time.time())}"
            
            # Allocate capital
            if not self.capital_manager.allocate_capital(eth_amount, trade_id):
                logging.warning("Insufficient capital for trade")
                return
            
            # Execute trade via OKX DEX
            result = await self.okx_connector.execute_token_buy(token_address, eth_amount)
            
            if not result:
                # Rollback capital allocation
                self.capital_manager.release_capital(trade_id, 0)
                logging.error("Trade execution failed")
                return
            
            # Log successful trade
            trade = TokenTrade(
                token_address=token_address,
                wallet_address=wallet_address,
                amount_eth=eth_amount,
                token_amount=float(result.get("toTokenAmount", 0)) / 10**18,
                tx_hash=result.get("txHash", ""),
                timestamp=time.time(),
                confidence_score=confidence
            )
            
            self._log_trade(trade)
            
            # Notify exit manager
            try:
                import exit_manager
                await exit_manager.schedule_exit({
                    "token_address": token_address,
                    "entry_price": eth_amount / trade.token_amount if trade.token_amount > 0 else 0,
                    "quantity": trade.token_amount,
                    "timestamp": trade.timestamp,
                    "wallet_followed": wallet_address,
                    "confidence_score": confidence
                })
            except ImportError:
                pass
            
            logging.info(f"✅ MIMIC TRADE EXECUTED: {token_address} | {eth_amount:.4f} ETH | Conf: {confidence:.2f}")
            
        except Exception as e:
            logging.error(f"Trade execution error: {e}")
    
    def _log_trade(self, trade: TokenTrade):
        log_entry = {
            "wallet_followed": trade.wallet_address,
            "token_address": trade.token_address,
            "amount_in_eth": trade.amount_eth,
            "amount_out_tokens": trade.token_amount,
            "tx_hash": trade.tx_hash,
            "timestamp": trade.timestamp,
            "confidence_score": trade.confidence_score
        }
        
        try:
            with open("mimic_log.csv", "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=log_entry.keys())
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow(log_entry)
        except Exception as e:
            logging.error(f"Failed to log trade: {e}")
        
        self.trade_log.append(log_entry)
    
    async def start_monitoring(self):
        self.running = True
        logging.info("🚀 Starting wallet mimic system...")
        logging.info(f"💰 Initial capital: ${self.capital_manager.total_capital}")
        logging.info(f"👁️  Monitoring {len(self.alpha_wallets)} alpha wallets")
        
        alpha_wallet_addresses = set(self.alpha_wallets.keys())
        
        try:
            await self.eth_monitor.monitor_pending_transactions(
                alpha_wallet_addresses, 
                self.process_wallet_transaction
            )
        except KeyboardInterrupt:
            logging.info("Shutting down wallet mimic system...")
            self.running = False
    
    def get_stats(self) -> Dict:
        return {
            "total_capital": self.capital_manager.total_capital,
            "available_capital": self.capital_manager.available_capital,
            "deployed_capital": self.capital_manager.deployed_capital,
            "total_trades": len(self.trade_log),
            "active_positions": len(self.capital_manager.positions),
            "total_return_pct": ((self.capital_manager.total_capital - 1000.0) / 1000.0) * 100
        }

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    required_env_vars = [
        "ETHEREUM_RPC_URL", "ETHEREUM_WS_URL", "ETHERSCAN_API_KEY",
        "OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE",
        "ETHEREUM_WALLET_ADDRESS"
    ]
    
    for var in required_env_vars:
        if not os.getenv(var):
            logging.error(f"Required environment variable {var} not set")
            return
    
    system = WalletMimicSystem()
    await system.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
