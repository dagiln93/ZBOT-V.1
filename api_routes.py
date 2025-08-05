from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from config import Config
from analysis import analyzer
from database import db_manager
from validators import RequestValidator
from monitoring import get_system_status, cleanup_expired_cache, health_monitor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание Blueprint для API
api_bp = Blueprint('api', __name__)

def get_translation(key: str, language: str = 'en') -> str:
    """Получает перевод для ключа на указанном языке"""
    translations = Config.TRANSLATIONS.get(language, Config.TRANSLATIONS['en'])
    return translations.get(key, key)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Проверка состояния API"""
    try:
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'service': 'Barashor Trading System API'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Service unavailable',
            'timestamp': datetime.now().isoformat()
        }), 503

@api_bp.route('/analysis', methods=['POST'])
def run_analysis():
    """Запуск анализа всех фьючерсов"""
    try:
        logger.info("Starting analysis of all futures...")
        
        # Запускаем анализ всех фьючерсов
        signals = analyzer.analyze_all_futures()
        
        if signals:
            logger.info(f"Analysis completed successfully. Found {len(signals)} signals")
            return jsonify({
                'success': True,
                'signals': signals,
                'total_signals': len(signals),
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.warning("No signals found during analysis")
            return jsonify({
                'success': True,
                'signals': [],
                'total_signals': 0,
                'message': 'No trading signals found',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/signals', methods=['GET'])
def get_signals():
    """Получение истории сигналов"""
    try:
        # Получаем параметры запроса
        symbol = request.args.get('symbol')
        limit = int(request.args.get('limit', 100))
        
        # Валидация параметров
        if limit > 1000:
            limit = 1000
        
        # Получаем сигналы
        signals = analyzer.get_signal_history(symbol=symbol, limit=limit)
        
        return jsonify({
            'success': True,
            'signals': signals,
            'total_count': len(signals),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get signals: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/signals/<symbol>/history', methods=['GET'])
def get_symbol_history(symbol):
    """Получение истории сигналов для конкретного символа"""
    try:
        # Валидация символа
        if not symbol or len(symbol) > 20:
            return jsonify({
                'success': False,
                'error': 'Invalid symbol'
            }), 400
        
        # Получаем историю сигналов
        signals = analyzer.get_signal_history(symbol=symbol, limit=100)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'signals': signals,
            'total_count': len(signals),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting symbol history for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get symbol history: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Получение статистики сигналов"""
    try:
        stats = analyzer.get_statistics()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get statistics: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/symbols', methods=['GET'])
def get_symbols():
    """Получение списка доступных символов"""
    try:
        from api_client import api_client
        
        # Получаем все доступные фьючерсы
        symbols = api_client.get_all_futures_symbols()
        
        return jsonify({
            'success': True,
            'symbols': symbols,
            'total_count': len(symbols),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get symbols: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/prices', methods=['GET'])
def get_prices():
    """Получение текущих цен"""
    try:
        from api_client import api_client
        
        # Получаем популярные символы
        symbols = Config.POPULAR_SYMBOLS[:10]  # Ограничиваем 10 символами
        
        prices = {}
        for symbol in symbols:
            price = api_client.get_current_price(symbol)
            if price:
                prices[symbol] = price
        
        return jsonify({
            'success': True,
            'prices': prices,
            'total_count': len(prices),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting prices: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get prices: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/validate', methods=['POST'])
def validate_data():
    """Валидация входных данных"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Валидация данных
        validator = RequestValidator()
        is_valid, errors = validator.validate_analysis_request(data)
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'errors': errors if not is_valid else [],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error validating data: {e}")
        return jsonify({
            'success': False,
            'error': f'Validation failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/monitoring/status', methods=['GET'])
def get_monitoring_status():
    """Получение статуса мониторинга системы"""
    try:
        status = get_system_status()
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get monitoring status: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/monitoring/health', methods=['GET'])
def check_system_health():
    """Проверка здоровья системы"""
    try:
        from api_client import api_client
        
        # Проверяем здоровье API
        api_health = health_monitor.check_api_health(api_client)
        
        # Проверяем здоровье базы данных
        db_health = health_monitor.check_database_health(db_manager)
        
        health_status = health_monitor.get_health_status()
        
        return jsonify({
            'success': True,
            'health': health_status,
            'api_healthy': api_health,
            'database_healthy': db_health,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return jsonify({
            'success': False,
            'error': f'Health check failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/monitoring/cache/clear', methods=['POST'])
def clear_cache():
    """Очистка кэша"""
    try:
        cleanup_expired_cache()
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to clear cache: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500 