import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from functools import lru_cache
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import Config
from monitoring import monitor_performance, cache_result, health_monitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIClient:
    """Клиент для работы с API Bybit и CoinGecko"""
    
    def __init__(self):
        self.bybit_api_key = Config.BYBIT_API_KEY
        self.bybit_secret_key = Config.BYBIT_SECRET_KEY
        self.coingecko_api_key = Config.COINGECKO_API_KEY
        self.bybit_base_url = Config.BYBIT_API_URL
        self.coingecko_base_url = Config.COINGECKO_API_URL
        
    def _make_request(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
        """Выполняет HTTP запрос с обработкой ошибок"""
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    @cache_result(timeout=600)  # Кэшируем на 10 минут
    @monitor_performance("get_all_futures_symbols")
    def get_all_futures_symbols(self) -> List[str]:
        """Получает список всех доступных фьючерсов на Bybit"""
        try:
            url = f"{self.bybit_base_url}/v5/market/instruments-info"
            params = {
                "category": "linear",
                "status": "Trading"
            }
            
            data = self._make_request(url, params=params)
            if data and data.get("retCode") == 0:
                symbols = []
                for instrument in data.get("result", {}).get("list", []):
                    symbol = instrument.get("symbol")
                    if symbol and symbol.endswith("USDT"):
                        # Исключаем символы, начинающиеся с цифр 1000+ и другие нежелательные символы
                        if not (symbol.startswith(('1000', '10000', '100000', '1000000')) or 
                                symbol.startswith(('TEST', 'DEMO', 'MOCK')) or
                                'TEST' in symbol or 'DEMO' in symbol):
                            symbols.append(symbol)
                return symbols
            else:
                logger.error(f"Failed to get futures symbols: {data}")
                return []
        except Exception as e:
            logger.error(f"Error getting futures symbols: {e}")
            return []
    
    @cache_result(timeout=300)  # Кэшируем на 5 минут
    @monitor_performance("get_klines_data")
    def get_klines_data(self, symbol: str, interval: str = "240", limit: int = 100) -> Optional[pd.DataFrame]:
        """Получает исторические данные свечей для символа"""
        try:
            url = f"{self.bybit_base_url}/v5/market/kline"
            params = {
                "category": "linear",
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            data = self._make_request(url, params=params)
            if data and data.get("retCode") == 0:
                klines = data.get("result", {}).get("list", [])
                if klines:
                    df = pd.DataFrame(klines, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
                    ])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume', 'turnover']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    return df.sort_values('timestamp')
            return None
        except Exception as e:
            logger.error(f"Error getting klines for {symbol}: {e}")
            return None
    
    @cache_result(timeout=60)  # Кэшируем на 1 минуту
    @monitor_performance("get_current_price")
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Получает текущую цену символа"""
        try:
            url = f"{self.bybit_base_url}/v5/market/tickers"
            params = {
                "category": "linear",
                "symbol": symbol
            }
            
            data = self._make_request(url, params=params)
            if data and data.get("retCode") == 0:
                tickers = data.get("result", {}).get("list", [])
                if tickers:
                    return float(tickers[0].get("lastPrice", 0))
            return None
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def get_crypto_rankings(self) -> Dict[str, Dict]:
        """Получает рейтинги криптовалют с CoinGecko"""
        try:
            url = f"{self.coingecko_base_url}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1,
                "sparkline": False
            }
            
            if self.coingecko_api_key:
                headers = {"X-CG-API-Key": self.coingecko_api_key}
            else:
                headers = {}
            
            data = self._make_request(url, params=params, headers=headers)
            if data:
                rankings = {}
                for coin in data:
                    symbol = coin.get("symbol", "").upper() + "USDT"
                    rankings[symbol] = {
                        "rank": coin.get("market_cap_rank", 999),
                        "name": coin.get("name", ""),
                        "market_cap": coin.get("market_cap", 0),
                        "price": coin.get("current_price", 0)
                    }
                return rankings
            return {}
        except Exception as e:
            logger.error(f"Error getting crypto rankings: {e}")
            return {}
    
    def _process_symbol_data(self, symbol: str) -> Optional[Dict]:
        """Обрабатывает данные для одного символа"""
        try:
            # Получаем исторические данные
            df = self.get_klines_data(symbol)
            if df is not None and len(df) > 50:
                current_price = self.get_current_price(symbol)
                if current_price:
                    return {
                        "symbol": symbol,
                        "data": df,
                        "current_price": current_price
                    }
            return None
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            return None
    
    @monitor_performance("get_all_futures_data")
    def get_all_futures_data(self) -> List[Dict]:
        """Получает данные для всех доступных фьючерсов с параллельной обработкой"""
        try:
            symbols = self.get_all_futures_symbols()
            if not symbols:
                logger.warning("No futures symbols found")
                return []
            
            # Анализируем все доступные фьючерсы, кроме тех что с фильтром 1000+
            # Фильтр уже применен в get_all_futures_symbols()
            
            futures_data = []
            
            # Используем ThreadPoolExecutor для параллельной обработки
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Создаем задачи для всех символов
                future_to_symbol = {executor.submit(self._process_symbol_data, symbol): symbol for symbol in symbols}
                
                # Обрабатываем результаты по мере их поступления
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result()
                        if result:
                            futures_data.append(result)
                    except Exception as e:
                        logger.error(f"Error processing {symbol}: {e}")
                        continue
            
            logger.info(f"Successfully processed {len(futures_data)} futures symbols")
            return futures_data
            
        except Exception as e:
            logger.error(f"Error getting all futures data: {e}")
            return []
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Получает информацию о символе"""
        try:
            url = f"{self.bybit_base_url}/v5/market/instruments-info"
            params = {
                "category": "linear",
                "symbol": symbol
            }
            
            data = self._make_request(url, params=params)
            if data and data.get("retCode") == 0:
                instruments = data.get("result", {}).get("list", [])
                if instruments:
                    instrument = instruments[0]
                    return {
                        "symbol": instrument.get("symbol"),
                        "base_coin": instrument.get("baseCoin"),
                        "quote_coin": instrument.get("quoteCoin"),
                        "min_order_qty": instrument.get("minOrderQty"),
                        "max_order_qty": instrument.get("maxOrderQty"),
                        "tick_size": instrument.get("tickSize"),
                        "price_scale": instrument.get("priceScale")
                    }
            return None
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None

# Создаем глобальный экземпляр клиента
api_client = APIClient() 