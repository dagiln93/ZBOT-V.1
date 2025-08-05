import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Основные настройки Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'barashor-trading-secret-key-2024')
    DEBUG = os.getenv('FLASK_ENV') != 'production'
    
    # Настройки базы данных
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///barashor_trading.db')
    
    # API ключи
    BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
    BYBIT_SECRET_KEY = os.getenv('BYBIT_SECRET_KEY', '')
    COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')
    
    # Настройки стратегии Barashor
    STRATEGY_NAME = "Barashor Trading System"
    STRATEGY_DESCRIPTION = "4-часовая стратегия возврата к среднему для криптофьючерсов"
    
    # Параметры анализа
    TIMEFRAME = "4h"  # 4-часовой таймфрейм
    LOOKBACK_PERIOD = 50  # Период для расчета SMA
    Z_SCORE_THRESHOLD = 2.0  # Порог для Z-Score
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    VOLUME_SMA_PERIOD = 20
    
    # API endpoints
    BYBIT_API_URL = "https://api.bybit.com"
    COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
    
    # Настройки кэширования
    CACHE_TIMEOUT = 300  # 5 минут
    
    # Настройки логирования
    LOG_LEVEL = "INFO"
    
    # Поддерживаемые языки
    SUPPORTED_LANGUAGES = ['en', 'ru']
    DEFAULT_LANGUAGE = 'en'
    
    # Популярные криптовалюты для отображения
    POPULAR_SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
        'DOTUSDT', 'LINKUSDT', 'LTCUSDT', 'BCHUSDT', 'XRPUSDT'
    ]
    
    # Ранги криптовалют
    CRYPTO_RANKINGS = {
        'BTCUSDT': {'rank': 1, 'name': 'Bitcoin'},
        'ETHUSDT': {'rank': 2, 'name': 'Ethereum'},
        'BNBUSDT': {'rank': 3, 'name': 'BNB'},
        'ADAUSDT': {'rank': 4, 'name': 'Cardano'},
        'SOLUSDT': {'rank': 5, 'name': 'Solana'},
        'DOTUSDT': {'rank': 6, 'name': 'Polkadot'},
        'LINKUSDT': {'rank': 7, 'name': 'Chainlink'},
        'LTCUSDT': {'rank': 8, 'name': 'Litecoin'},
        'BCHUSDT': {'rank': 9, 'name': 'Bitcoin Cash'},
        'XRPUSDT': {'rank': 10, 'name': 'XRP'}
    }
    
    # Переводы
    TRANSLATIONS = {
        'en': {
            'title': 'Barashor Trading System',
            'subtitle': '4-Hour Mean Reversion Strategy for Crypto Futures',
            'analyze': 'Analyze All Futures',
            'history': 'Signal History',
            'settings': 'Settings',
            'symbol': 'Symbol',
            'direction': 'Direction',
            'precision': 'Precision',
            'z_score': 'Z-Score',
            'sma_50': 'SMA 50',
            'volume_sma': 'Volume SMA',
            'rsi': 'RSI',
            'macd': 'MACD',
            'signal': 'Signal',
            'strength': 'Strength',
            'timestamp': 'Timestamp',
            'valid': 'Valid',
            'buy': 'BUY',
            'sell': 'SELL',
            'neutral': 'NEUTRAL',
            'strong': 'Strong',
            'moderate': 'Moderate',
            'weak': 'Weak',
            'loading': 'Analyzing all futures...',
            'no_signals': 'No signals found',
            'error': 'Error occurred',
            'language': 'Language',
            'theme': 'Theme',
            'dark': 'Dark',
            'light': 'Light',
            'auto': 'Auto',
            'monitoring': 'Monitoring',
            'system_monitoring': 'System Monitoring',
            'system_health': 'System Health',
            'performance_metrics': 'Performance Metrics',
            'cache_statistics': 'Cache Statistics',
            'recent_alerts': 'Recent Alerts',
            'api_connectivity': 'API Connectivity',
            'database_connectivity': 'Database Connectivity',
            'analysis_performance': 'Analysis Performance',
            'refresh': 'Refresh',
            'total_entries': 'Total Entries',
            'expired_entries': 'Expired Entries',
            'memory_usage': 'Memory Usage',
            'no_alerts': 'No alerts at this time',
            'home': 'Home'
        },
        'ru': {
            'title': 'Barashor Trading System',
            'subtitle': '4-часовая стратегия возврата к среднему для криптофьючерсов',
            'analyze': 'Анализировать все фьючерсы',
            'history': 'История сигналов',
            'settings': 'Настройки',
            'symbol': 'Символ',
            'direction': 'Направление',
            'precision': 'Точность',
            'z_score': 'Z-Score',
            'sma_50': 'SMA 50',
            'volume_sma': 'Объем SMA',
            'rsi': 'RSI',
            'macd': 'MACD',
            'signal': 'Сигнал',
            'strength': 'Сила',
            'timestamp': 'Время',
            'valid': 'Действителен',
            'buy': 'ПОКУПКА',
            'sell': 'ПРОДАЖА',
            'neutral': 'НЕЙТРАЛЬНО',
            'strong': 'Сильный',
            'moderate': 'Умеренный',
            'weak': 'Слабый',
            'loading': 'Анализируем все фьючерсы...',
            'no_signals': 'Сигналы не найдены',
            'error': 'Произошла ошибка',
            'language': 'Язык',
            'theme': 'Тема',
            'dark': 'Темная',
            'light': 'Светлая',
            'auto': 'Авто',
            'monitoring': 'Мониторинг',
            'system_monitoring': 'Мониторинг системы',
            'system_health': 'Здоровье системы',
            'performance_metrics': 'Метрики производительности',
            'cache_statistics': 'Статистика кэша',
            'recent_alerts': 'Последние алерты',
            'api_connectivity': 'Подключение к API',
            'database_connectivity': 'Подключение к базе данных',
            'analysis_performance': 'Производительность анализа',
            'refresh': 'Обновить',
            'total_entries': 'Всего записей',
            'expired_entries': 'Истекших записей',
            'memory_usage': 'Использование памяти',
            'no_alerts': 'Алертов нет',
            'home': 'Главная'
        }
    } 