import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from config import Config
from api_client import api_client
from database import db_manager
from validators import DataValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingAnalyzer:
    """Анализатор торговых сигналов для Barashor Trading System"""
    
    def __init__(self):
        self.config = Config()
        self.validator = DataValidator()
        
    def calculate_z_score(self, prices: pd.Series, period: int = 20) -> float:
        """Вычисляет Z-Score для цен"""
        if len(prices) < period:
            return 0.0
        
        rolling_mean = prices.rolling(window=period).mean()
        rolling_std = prices.rolling(window=period).std()
        
        if rolling_std.iloc[-1] == 0:
            return 0.0
        
        z_score = (prices.iloc[-1] - rolling_mean.iloc[-1]) / rolling_std.iloc[-1]
        return z_score
    
    def calculate_sma(self, prices: pd.Series, period: int) -> float:
        """Вычисляет Simple Moving Average"""
        if len(prices) < period:
            return prices.mean() if len(prices) > 0 else 0.0
        return prices.rolling(window=period).mean().iloc[-1]
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Вычисляет Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        if loss.iloc[-1] == 0:
            return 100.0
        
        rs = gain.iloc[-1] / loss.iloc[-1]
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """Вычисляет MACD"""
        if len(prices) < slow:
            return 0.0, 0.0, 0.0
        
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return macd_line.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]
    
    def calculate_volume_sma(self, volumes: pd.Series, period: int = 20) -> float:
        """Вычисляет SMA для объема"""
        if len(volumes) < period:
            return volumes.mean() if len(volumes) > 0 else 0.0
        return volumes.rolling(window=period).mean().iloc[-1]
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
        """Вычисляет Bollinger Bands"""
        if len(prices) < period:
            return 0.0, 0.0, 0.0
        
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band.iloc[-1], sma.iloc[-1], lower_band.iloc[-1]
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Tuple[float, float]:
        """Вычисляет Stochastic Oscillator"""
        if len(close) < period:
            return 50.0, 50.0
        
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=3).mean()
        
        return k_percent.iloc[-1], d_percent.iloc[-1]
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        """Вычисляет Average True Range"""
        if len(close) < period:
            return 0.0
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr.iloc[-1]
    
    def generate_signal(self, z_score: float, rsi: float, macd_histogram: float, 
                       volume_ratio: float) -> Optional[Dict]:
        """Генерирует торговый сигнал на основе технических индикаторов"""
        
        # Определяем направление сигнала (только BUY или SELL)
        signal_direction = None
        signal_strength = "WEAK"
        
        # Анализ Z-Score - основной индикатор
        if z_score > self.config.Z_SCORE_THRESHOLD:
            signal_direction = "SELL"
        elif z_score < -self.config.Z_SCORE_THRESHOLD:
            signal_direction = "BUY"
        
        # Если Z-Score не дает сигнала, проверяем RSI
        if signal_direction is None:
            if rsi > self.config.RSI_OVERBOUGHT:
                signal_direction = "SELL"
            elif rsi < self.config.RSI_OVERSOLD:
                signal_direction = "BUY"
        
        # Если все еще нет сигнала, проверяем MACD
        if signal_direction is None:
            if macd_histogram < -0.001:  # Отрицательный MACD
                signal_direction = "SELL"
            elif macd_histogram > 0.001:  # Положительный MACD
                signal_direction = "BUY"
        
        # Если нет четкого сигнала, пропускаем
        if signal_direction is None:
            return None
        
        # Определяем силу сигнала
        # Анализ RSI для подтверждения
        if rsi > self.config.RSI_OVERBOUGHT and signal_direction == "SELL":
            signal_strength = "STRONG"
        elif rsi < self.config.RSI_OVERSOLD and signal_direction == "BUY":
            signal_strength = "STRONG"
        
        # Анализ MACD для подтверждения
        if macd_histogram > 0 and signal_direction == "BUY":
            signal_strength = "STRONG"
        elif macd_histogram < 0 and signal_direction == "SELL":
            signal_strength = "STRONG"
        
        # Анализ объема
        if volume_ratio > 1.5:  # Объем выше среднего
            if signal_strength == "WEAK":
                signal_strength = "MODERATE"
            elif signal_strength == "MODERATE":
                signal_strength = "STRONG"
        
        # Вычисляем точность сигнала
        precision = self._calculate_signal_precision(z_score, rsi, macd_histogram, volume_ratio)
        
        # Проверяем минимальную точность (отсекаем слабые сигналы)
        if precision < 60.0:
            return None
        
        return {
            "direction": signal_direction,
            "strength": signal_strength,
            "precision": precision
        }
    
    def _calculate_signal_precision(self, z_score: float, rsi: float, 
                                   macd_histogram: float, volume_ratio: float) -> float:
        """Вычисляет точность сигнала (0-100%)"""
        precision = 50.0  # Базовая точность
        
        # Z-Score вклад (основной фактор)
        z_score_contribution = min(abs(z_score) / 3.0, 1.0) * 30
        precision += z_score_contribution
        
        # RSI вклад
        if rsi < 25 or rsi > 75:
            precision += 20
        elif rsi < 30 or rsi > 70:
            precision += 15
        elif rsi < 40 or rsi > 60:
            precision += 10
        
        # MACD вклад
        if abs(macd_histogram) > 0.002:
            precision += 15
        elif abs(macd_histogram) > 0.001:
            precision += 10
        
        # Объем вклад
        if volume_ratio > 1.5:
            precision += 15
        elif volume_ratio > 1.2:
            precision += 10
        
        return min(precision, 100.0)
    
    def analyze_symbol(self, symbol: str, data: pd.DataFrame, current_price: float) -> Optional[Dict]:
        """Анализирует один символ и генерирует сигнал"""
        try:
            if len(data) < 50:
                return None
            
            # Получаем цены и объемы
            prices = data['close']
            volumes = data['volume']
            
            # Вычисляем технические индикаторы
            z_score = self.calculate_z_score(prices, period=20)
            sma_50 = self.calculate_sma(prices, period=50)
            rsi = self.calculate_rsi(prices, period=14)
            macd_line, macd_signal, macd_histogram = self.calculate_macd(prices)
            volume_sma = self.calculate_volume_sma(volumes, period=20)
            
            # Вычисляем отношение текущего объема к среднему
            current_volume = volumes.iloc[-1] if len(volumes) > 0 else 0
            volume_ratio = current_volume / volume_sma if volume_sma > 0 else 1.0
            
            # Генерируем сигнал
            signal_info = self.generate_signal(z_score, rsi, macd_histogram, volume_ratio)
            
            # Если нет сигнала, возвращаем None
            if signal_info is None:
                return None
            
            # Создаем результат анализа
            analysis_result = {
                "symbol": symbol,
                "current_price": current_price,
                "z_score": round(z_score, 4),
                "sma_50": round(sma_50, 4),
                "rsi": round(rsi, 2),
                "macd_line": round(macd_line, 6),
                "macd_signal": round(macd_signal, 6),
                "macd_histogram": round(macd_histogram, 6),
                "volume_sma": round(volume_sma, 2),
                "volume_ratio": round(volume_ratio, 2),
                "signal": signal_info["direction"],
                "strength": signal_info["strength"],
                "precision": round(signal_info["precision"], 2),
                "timestamp": datetime.now(),
                "valid": True
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def analyze_all_futures(self) -> List[Dict]:
        """Анализирует все доступные фьючерсы на Bybit"""
        try:
            logger.info("Starting analysis of all Bybit futures...")
            
            # Получаем данные всех фьючерсов
            futures_data = api_client.get_all_futures_data()
            
            if not futures_data:
                logger.warning("No futures data available")
                return []
            
            analysis_results = []
            
            for future_data in futures_data:
                symbol = future_data["symbol"]
                data = future_data["data"]
                current_price = future_data["current_price"]
                
                # Анализируем символ
                result = self.analyze_symbol(symbol, data, current_price)
                if result:
                    analysis_results.append(result)
                    
                    # Сохраняем сигнал в базу данных
                    try:
                        db_manager.save_signal(result)
                    except Exception as e:
                        logger.error(f"Error saving signal for {symbol}: {e}")
            
            # Сортируем результаты по точности и силе сигнала
            # Сначала по точности (убывание), затем по силе сигнала
            analysis_results.sort(key=lambda x: (x['precision'], x['strength']), reverse=True)
            
            logger.info(f"Analysis completed. Found {len(analysis_results)} signals")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in analyze_all_futures: {e}")
            return []
    
    def get_signal_history(self, symbol: Optional[str] = None, 
                          limit: int = 100) -> List[Dict]:
        """Получает историю сигналов"""
        try:
            return db_manager.get_signals(symbol=symbol, limit=limit)
        except Exception as e:
            logger.error(f"Error getting signal history: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Получает статистику сигналов"""
        try:
            return db_manager.get_statistics()
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

# Создаем глобальный экземпляр анализатора
analyzer = TradingAnalyzer() 