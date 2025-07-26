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
from eth_account import Account
from typing import Dict, List, Set, Optional, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import csv
import os
from decimal import Decimal
import aiohttp
import discord
from discord import Webhook, RequestsWebhookAdapter

@dataclass
class AlphaWallet:
    address: str
    avg_multiplier: float
    avg_hold_time: int
    first_touch_timestamp: int
    trades_per_day: float
    success_rate: float

@dataclass
class TokenValidation:
    contract_address: str
    is_verified: bool
    has_malicious_functions: bool
    liquidity_usd: float
    is_blacklisted: bool
    slippage_estimate: float

@dataclass
class TradeExecution:
    token_address: str
    amount_in_eth: float
    amount_out_tokens: float
    tx_hash: str
    gas_used: int
    entry_price: float
    timestamp: float

class OKXDEXConnector:
    def __init__(self, api_key: str, secret_key: str, passphrase: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = "https://www.okx.com"
        self.session = requests.Session()
        
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
        timestamp = str(time.time())
        signature = self._generate_signature(timestamp, method, request_path, body)
        
        return {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }
    
    def get_dex_token_info(self, token_address: str) -> Optional[Dict]:
        request_path = f"/api/v5/dex/tokens/{token_address}"
        headers = self._get_headers("GET", request_path)
        
        try:
            response = self.session.get(f"{self.base_url}{request_path}", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "0":
                    return data.get("data", [{}])[0]
        except Exception:
            pass
        return None
    
    def get_liquidity_depth(self, token_address: str) -> float:
        request_path = f"/api/v5/dex/liquidity/{token_address}"
        headers = self._get_headers("GET", request_path)
        
        try:
            response = self.session.get(f"{self.base_url}{request_path}", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "0":
                    liquidity_data = data.get("data", [{}])[0]
                    base_liquidity = float(liquidity_data.get("baseLiquidity", 0))
                    quote_liquidity = float(liquidity_data.get("quoteLiquidity", 0))
                    return base_liquidity + quote_liquidity
        except Exception:
            pass
        return 0.0
    
    def execute_dex_trade(self, token_address: str, amount_eth: float, slippage_tolerance: float = 0.10) -> Optional[Dict]:
        request_path = "/api/v5/dex/trade"
        
        trade_data = {
            "chainId": "1",
            "fromTokenAddress": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "toTokenAddress": token_address,
            "amount": str(int(amount_eth * 10**18)),
            "slippage": str(int(slippage_tolerance * 100)),
            "userWalletAddress": os.getenv("ETHEREUM_WALLET_ADDRESS"),
            "referrer": "hft_mimic_system"
        }
        
        body = json.dumps(trade_data)
        headers = self._get_headers("POST", request_path, body)
        
        try:
            response = self.session.post(f"{self.base_url}{request_path}", headers=headers, data=body, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "0":
                    return data.get("data", [{}])[0]
        except Exception:
            pass
        return None

class EthereumMonitor:
    def __init__(self, provider_url: str):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.is_connected = self.w3.isConnected()
        if not self.is_connected:
            raise RuntimeError("Failed to connect to Ethereum network")
        
        self.contract_cache = {}
        self.deploy_fingerprints = self._load_deploy_fingerprints()
        
    def _load_deploy_fingerprints(self) -> Dict[str, str]:
        try:
            with open("deploy_fingerprints.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_contract_source(self, contract_address: str) -> Optional[str]:
        etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
        if not etherscan_api_key:
            return None
            
        url = f"https://api.etherscan.io/api"
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": contract_address,
            "apikey": etherscan_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    result = data.get("result", [{}])[0]
                    return result.get("SourceCode", "")
        except Exception:
            pass
        return None
    
    def analyze_contract_safety(self, source_code: str) -> bool:
        if not source_code:
            return False
            
        dangerous_patterns = [
            "cooldown", "blacklist", "rebase", "antiSell", "setFees",
            "onlyOwner", "_transfer", "addLiquidity", "removeLiquidity",
            "mint(", "burn(", "pause", "blacklistAddress", "setTaxes"
        ]
        
        source_lower = source_code.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in source_lower:
                return False
        return True
    
    def get_transaction_details(self, tx_hash: str) -> Optional[Dict]:
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                "from": tx["from"],
                "to": tx["to"],
                "value": tx["value"],
                "gas": tx["gas"],
                "gasPrice": tx["gasPrice"],
                "input": tx["input"].hex(),
                "status": receipt["status"],
                "gasUsed": receipt["gasUsed"],
                "logs": [log for log in receipt["logs"]]
            }
        except Exception:
            return None
    
    def decode_transaction_calldata(self, calldata: str) -> Dict[str, any]:
        if len(calldata) < 10:
            return {"type": "unknown", "data": {}}
        
        method_id = calldata[:10]
        
        known_methods = {
            "0xa9059cbb": "transfer",
            "0x23b872dd": "transferFrom",
            "0x095ea7b3": "approve",
            "0x7ff36ab5": "swapExactETHForTokens",
            "0x38ed1739": "swapExactTokensForTokens",
            "0x02751cec": "removeLiquidity",
            "0xe8e33700": "addLiquidity"
        }
        
        method_name = known_methods.get(method_id, "unknown")
        
        return {
            "type": method_name,
            "method_id": method_id,
            "raw_data": calldata[10:] if len(calldata) > 10 else ""
        }
    
    def create_contract_fingerprint(self, bytecode: str) -> str:
        return hashlib.sha256(bytecode.encode()).hexdigest()[:16]

class CapitalManager:
    def __init__(self, initial_capital: float):
        self.total_capital = initial_capital
        self.available_capital = initial_capital
        self.deployed_capital = 0.0
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.max_daily_trades = 50
        self.max_position_size_pct = 0.33
        self.gas_reserve = 0.1
        
    def can_execute_trade(self, required_capital: float, gas_estimate: float) -> bool:
        total_required = required_capital + gas_estimate
        if total_required > self.available_capital:
            return False
        if required_capital > (self.total_capital * self.max_position_size_pct):
            return False
        if self.trades_today >= self.max_daily_trades:
            return False
        return True
    
    def allocate_capital(self, amount: float) -> bool:
        if amount <= self.available_capital:
            self.available_capital -= amount
            self.deployed_capital += amount
            self.trades_today += 1
            return True
        return False
    
    def release_capital(self, amount: float, pnl: float):
        self.available_capital += (amount + pnl)
        self.deployed_capital -= amount
        self.daily_pnl += pnl
        self.total_capital += pnl

class RiskManager:
    def __init__(self):
        self.blacklisted_tokens = self._load_blacklist()
        self.rugdex_blacklist = self._load_rugdex_blacklist()
        self.max_slippage = 0.10
        self.min_liquidity = 50000.0
        
    def _load_blacklist(self) -> Set[str]:
        try:
            with open("wallet_blacklist.json", "r") as f:
                data = json.load(f)
                return set(data.get("blacklisted_addresses", []))
        except FileNotFoundError:
            return set()
    
    def _load_rugdex_blacklist(self) -> Set[str]:
        try:
            with open("rugdex_blacklist.csv", "r") as f:
                reader = csv.reader(f)
                return set(row[0] for row in reader if row)
        except FileNotFoundError:
            return set()
    
    def validate_wallet(self, wallet_address: str) -> bool:
        return wallet_address.lower() not in self.blacklisted_tokens
    
    def validate_token(self, token_address: str, liquidity: float, source_code: str) -> bool:
        if token_address.lower() in self.rugdex_blacklist:
            return False
        if liquidity < self.min_liquidity:
            return False
        if not self._analyze_token_contract(source_code):
            return False
        return True
    
    def _analyze_token_contract(self, source_code: str) -> bool:
        if not source_code:
            return False
            
        suspicious_patterns = [
            "onlyOwner", "blacklist", "pause", "mint", "rebase",
            "setTaxFee", "setLiquidityFee", "antiBot", "cooldown"
        ]
        
        for pattern in suspicious_patterns:
            if pattern in source_code:
                return False
        return True
    
    def estimate_slippage(self, token_address: str, trade_size_eth: float, liquidity: float) -> float:
        if liquidity == 0:
            return 1.0
        
        impact_ratio = trade_size_eth / liquidity
        estimated_slippage = impact_ratio * 2.0
        return min(estimated_slippage, 0.5)

class AlertSystem:
    def __init__(self):
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.discord_user_id = os.getenv("DISCORD_USER_ID")
        
    async def send_trade_alert(self, trade_data: TradeExecution, wallet_followed: str):
        if not self.discord_webhook_url:
            return
            
        embed = {
            "title": "🔥 WALLET MIMIC EXECUTION",
            "color": 0x00ff00,
            "fields": [
                {"name": "Wallet Followed", "value": f"`{wallet_followed[:10]}...`", "inline": True},
                {"name": "Token", "value": f"`{trade_data.token_address[:10]}...`", "inline": True},
                {"name": "Entry Price", "value": f"${trade_data.entry_price:.8f}", "inline": True},
                {"name": "Amount (ETH)", "value": f"{trade_data.amount_in_eth:.4f} ETH", "inline": True},
                {"name": "Tokens Received", "value": f"{trade_data.amount_out_tokens:.2f}", "inline": True},
                {"name": "Gas Used", "value": f"{trade_data.gas_used:,}", "inline": True},
                {"name": "Transaction", "value": f"[View](https://etherscan.io/tx/{trade_data.tx_hash})", "inline": False}
            ],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(trade_data.timestamp))
        }
        
        payload = {
            "embeds": [embed],
            "username": "Wallet Mimic Bot"
        }
        
        if self.discord_user_id:
            payload["content"] = f"<@{self.discord_user_id}> New mimic trade executed!"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.discord_webhook_url, json=payload) as response:
                    if response.status != 204:
                        logging.error(f"Discord webhook failed: {response.status}")
        except Exception as e:
            logging.error(f"Alert system error: {e}")
    
    def send_error_alert(self, error_message: str):
        logging.error(f"SYSTEM ERROR: {error_message}")

class WalletMimicSystem:
    def __init__(self):
        self.alpha_wallets = self._load_alpha_wallets()
        self.okx_connector = OKXDEXConnector(
            os.getenv("OKX_API_KEY"),
            os.getenv("OKX_SECRET_KEY"),
            os.getenv("OKX_PASSPHRASE")
        )
        self.eth_monitor = EthereumMonitor(os.getenv("ETHEREUM_RPC_URL"))
        self.capital_manager = CapitalManager(1000.0)
        self.risk_manager = RiskManager()
        self.alert_system = AlertSystem()
        
        self.ws_url = os.getenv("ETHEREUM_WS_URL")
        self.trade_log = []
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def _load_alpha_wallets(self) -> Dict[str, AlphaWallet]:
        try:
            with open("alpha_wallets.json", "r") as f:
                data = json.load(f)
                wallets = {}
                for wallet_data in data.get("wallets", []):
                    if wallet_data.get("success_rate", 0) > 0.60:
                        wallet = AlphaWallet(
                            address=wallet_data["address"],
                            avg_multiplier=wallet_data.get("avg_multiplier", 1.0),
                            avg_hold_time=wallet_data.get("avg_hold_time", 3600),
                            first_touch_timestamp=wallet_data.get("first_touch_timestamp", 0),
                            trades_per_day=wallet_data.get("trades_per_day", 0),
                            success_rate=wallet_data.get("success_rate", 0)
                        )
                        wallets[wallet_data["address"].lower()] = wallet
                return wallets
        except FileNotFoundError:
            logging.error("alpha_wallets.json not found")
            return {}
    
    def _validate_token_comprehensive(self, token_address: str) -> TokenValidation:
        try:
            source_code = self.eth_monitor.get_contract_source(token_address)
            is_verified = source_code is not None and len(source_code) > 0
            has_malicious = not self.eth_monitor.analyze_contract_safety(source_code)
            
            liquidity = self.okx_connector.get_liquidity_depth(token_address)
            is_blacklisted = not self.risk_manager.validate_token(token_address, liquidity, source_code)
            
            slippage = self.risk_manager.estimate_slippage(token_address, 1.0, liquidity)
            
            return TokenValidation(
                contract_address=token_address,
                is_verified=is_verified,
                has_malicious_functions=has_malicious,
                liquidity_usd=liquidity,
                is_blacklisted=is_blacklisted,
                slippage_estimate=slippage
            )
        except Exception as e:
            logging.error(f"Token validation error: {e}")
            return TokenValidation(token_address, False, True, 0.0, True, 1.0)
    
    def _calculate_position_size(self, wallet_alpha_score: float, current_capital: float, gas_cost: float) -> float:
        base_size_pct = 0.15
        alpha_multiplier = min(wallet_alpha_score / 10.0, 2.0)
        volatility_adjustment = 0.8
        
        position_pct = base_size_pct * alpha_multiplier * volatility_adjustment
        position_value = current_capital * position_pct
        
        max_position = current_capital * self.capital_manager.max_position_size_pct
        position_value = min(position_value, max_position)
        
        return max(position_value - gas_cost, 0.01)
    
    async def _execute_mimic_trade(self, wallet_address: str, token_address: str, detected_tx: Dict) -> Optional[TradeExecution]:
        try:
            token_validation = self._validate_token_comprehensive(token_address)
            
            if not token_validation.is_verified:
                logging.warning(f"Token {token_address} not verified on Etherscan")
                return None
                
            if token_validation.has_malicious_functions:
                logging.warning(f"Token {token_address} has suspicious contract functions")
                return None
                
            if token_validation.liquidity_usd < self.risk_manager.min_liquidity:
                logging.warning(f"Token {token_address} liquidity too low: ${token_validation.liquidity_usd}")
                return None
                
            if token_validation.slippage_estimate > self.risk_manager.max_slippage:
                logging.warning(f"Token {token_address} slippage too high: {token_validation.slippage_estimate:.1%}")
                return None
            
            alpha_wallet = self.alpha_wallets.get(wallet_address.lower())
            if not alpha_wallet:
                return None
                
            alpha_score = alpha_wallet.avg_multiplier * alpha_wallet.success_rate
            gas_estimate = detected_tx.get("gasPrice", 20000000000) * 200000 / 10**18
            
            position_size_eth = self._calculate_position_size(
                alpha_score, 
                self.capital_manager.available_capital, 
                gas_estimate
            )
            
            if not self.capital_manager.can_execute_trade(position_size_eth, gas_estimate):
                logging.warning("Insufficient capital or trade limits reached")
                return None
            
            trade_result = self.okx_connector.execute_dex_trade(
                token_address, 
                position_size_eth, 
                token_validation.slippage_estimate
            )
            
            if not trade_result:
                logging.error("OKX DEX trade execution failed")
                return None
            
            self.capital_manager.allocate_capital(position_size_eth)
            
            execution = TradeExecution(
                token_address=token_address,
                amount_in_eth=position_size_eth,
                amount_out_tokens=float(trade_result.get("toTokenAmount", 0)) / 10**18,
                tx_hash=trade_result.get("txHash", ""),
                gas_used=int(trade_result.get("gasUsed", 0)),
                entry_price=position_size_eth / (float(trade_result.get("toTokenAmount", 1)) / 10**18),
                timestamp=time.time()
            )
            
            self._log_trade(execution, wallet_address)
            await self.alert_system.send_trade_alert(execution, wallet_address)
            
            return execution
            
        except Exception as e:
            self.alert_system.send_error_alert(f"Trade execution failed: {e}")
            return None
    
    def _log_trade(self, execution: TradeExecution, wallet_followed: str):
        log_entry = {
            "wallet_followed": wallet_followed,
            "token_symbol": execution.token_address,
            "okx_token_id": execution.token_address,
            "entry_price": execution.entry_price,
            "amount_in_eth": execution.amount_in_eth,
            "amount_out_tokens": execution.amount_out_tokens,
            "tx_hash": execution.tx_hash,
            "timestamp": execution.timestamp,
            "gas_used": execution.gas_used
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
        
        try:
            import capital_manager
            import exit_manager
            capital_manager.update_position(log_entry)
            exit_manager.schedule_exit(log_entry)
        except ImportError:
            pass
    
    async def _monitor_pending_transactions(self):
        try:
            uri = self.ws_url
            async with websockets.connect(uri) as websocket:
                subscribe_msg = {
                    "id": 1,
                    "method": "eth_subscribe",
                    "params": ["pendingTransactions"]
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if "params" in data and "result" in data["params"]:
                            tx_hash = data["params"]["result"]
                            await self._process_pending_transaction(tx_hash)
                    except Exception as e:
                        logging.error(f"WebSocket message processing error: {e}")
                        
        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            await asyncio.sleep(5)
            if self.running:
                await self._monitor_pending_transactions()
    
    async def _process_pending_transaction(self, tx_hash: str):
        try:
            tx_details = self.eth_monitor.get_transaction_details(tx_hash)
            if not tx_details:
                return
            
            from_address = tx_details["from"].lower()
            if from_address not in self.alpha_wallets:
                return
            
            if not self.risk_manager.validate_wallet(from_address):
                return
            
            calldata_info = self.eth_monitor.decode_transaction_calldata(tx_details["input"])
            
            if calldata_info["type"] in ["swapExactETHForTokens", "swapExactTokensForTokens"]:
                to_address = tx_details.get("to", "").lower()
                
                if "0x" in to_address and len(to_address) == 42:
                    execution = await self._execute_mimic_trade(from_address, to_address, tx_details)
                    if execution:
                        logging.info(f"Successfully mimicked trade from {from_address[:10]}...")
            
            elif calldata_info["type"] == "unknown" and tx_details["to"] is None:
                bytecode = tx_details["input"]
                fingerprint = self.eth_monitor.create_contract_fingerprint(bytecode)
                
                if fingerprint in self.eth_monitor.deploy_fingerprints:
                    logging.info(f"Known deployer pattern detected from {from_address[:10]}...")
                    
        except Exception as e:
            logging.error(f"Transaction processing error: {e}")
    
    async def start_monitoring(self):
        self.running = True
        logging.info("Starting wallet mimic system...")
        logging.info(f"Monitoring {len(self.alpha_wallets)} alpha wallets")
        logging.info(f"Initial capital: ${self.capital_manager.total_capital}")
        
        try:
            while self.running:
                await self._monitor_pending_transactions()
        except KeyboardInterrupt:
            logging.info("Shutting down wallet mimic system...")
            self.running = False
        except Exception as e:
            self.alert_system.send_error_alert(f"System critical error: {e}")
            raise
    
    def stop_monitoring(self):
        self.running = False
        self.executor.shutdown(wait=True)
        
        final_capital = self.capital_manager.total_capital
        total_return = ((final_capital - 1000.0) / 1000.0) * 100
        
        logging.info(f"Final capital: ${final_capital:.2f}")
        logging.info(f"Total return: {total_return:.2f}%")
        logging.info(f"Trades executed: {len(self.trade_log)}")

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    required_env_vars = [
        "OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE",
        "ETHEREUM_RPC_URL", "ETHEREUM_WS_URL", "ETHERSCAN_API_KEY",
        "ETHEREUM_WALLET_ADDRESS"
    ]
    
    for var in required_env_vars:
        if not os.getenv(var):
            raise RuntimeError(f"Required environment variable {var} not set")
    
    system = WalletMimicSystem()
    await system.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
