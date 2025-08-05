#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Barashor Trading System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis import analyzer
from database import db_manager
from api_client import api_client
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_client():
    """Тестирует API клиент"""
    print("🔍 Тестирование API клиента...")
    
    try:
        # Получаем список символов
        symbols = api_client.get_all_futures_symbols()
        print(f"✅ Получено {len(symbols)} символов фьючерсов")
        
        if symbols:
            # Тестируем получение данных для первого символа
            test_symbol = symbols[0]
            print(f"📊 Тестирование данных для {test_symbol}...")
            
            # Получаем исторические данные
            df = api_client.get_klines_data(test_symbol)
            if df is not None and len(df) > 0:
                print(f"✅ Получено {len(df)} записей исторических данных")
                
                # Получаем текущую цену
                price = api_client.get_current_price(test_symbol)
                if price:
                    print(f"✅ Текущая цена {test_symbol}: ${price}")
                else:
                    print("❌ Не удалось получить текущую цену")
            else:
                print("❌ Не удалось получить исторические данные")
        else:
            print("❌ Не удалось получить список символов")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании API клиента: {e}")

def test_database():
    """Тестирует базу данных"""
    print("\n🗄️ Тестирование базы данных...")
    
    try:
        # Инициализируем базу данных
        db_manager.init_db()
        print("✅ База данных инициализирована")
        
        # Тестируем сохранение сигнала
        test_signal = {
            "symbol": "BTCUSDT",
            "current_price": 50000.0,
            "z_score": 2.5,
            "sma_50": 48000.0,
            "rsi": 75.0,
            "macd_line": 0.001,
            "macd_signal": 0.0005,
            "macd_histogram": 0.0005,
            "volume_sma": 1000000.0,
            "volume_ratio": 1.5,
            "signal": "SELL",
            "strength": "STRONG",
            "precision": 85.0,
            "timestamp": "2024-01-01T12:00:00",
            "valid": True
        }
        
        db_manager.save_signal(test_signal)
        print("✅ Тестовый сигнал сохранен")
        
        # Получаем сигналы
        signals = db_manager.get_signals(limit=10)
        print(f"✅ Получено {len(signals)} сигналов из базы данных")
        
        # Получаем статистику
        stats = db_manager.get_statistics()
        print(f"✅ Статистика: {stats}")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании базы данных: {e}")

def test_analyzer():
    """Тестирует анализатор"""
    print("\n📈 Тестирование анализатора...")
    
    try:
        # Создаем тестовые данные
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Генерируем тестовые данные
        dates = pd.date_range(start='2024-01-01', periods=100, freq='4H')
        prices = np.random.normal(50000, 2000, 100).cumsum() + 50000
        volumes = np.random.normal(1000000, 200000, 100)
        
        test_data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': volumes,
            'turnover': prices * volumes
        })
        
        # Тестируем анализ символа
        result = analyzer.analyze_symbol("TESTUSDT", test_data, 50000.0)
        
        if result:
            print(f"✅ Анализ успешен: {result['signal']} сигнал с точностью {result['precision']}%")
            print(f"   Z-Score: {result['z_score']}, RSI: {result['rsi']}")
        else:
            print("❌ Анализ не дал результатов")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании анализатора: {e}")

def test_full_analysis():
    """Тестирует полный анализ"""
    print("\n🚀 Тестирование полного анализа...")
    
    try:
        # Запускаем анализ всех фьючерсов
        signals = analyzer.analyze_all_futures()
        
        if signals:
            print(f"✅ Анализ завершен! Найдено {len(signals)} сигналов")
            
            # Показываем топ-5 сигналов
            print("\n🏆 Топ-5 сигналов:")
            for i, signal in enumerate(signals[:5], 1):
                print(f"{i}. {signal['symbol']} - {signal['signal']} (точность: {signal['precision']}%)")
        else:
            print("❌ Анализ не дал результатов")
            
    except Exception as e:
        print(f"❌ Ошибка при полном анализе: {e}")

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование Barashor Trading System")
    print("=" * 50)
    
    # Тестируем компоненты по очереди
    test_api_client()
    test_database()
    test_analyzer()
    test_full_analysis()
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    main() 