import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime

from config import Config
from analysis import analyzer
from database import db_manager
from api_routes import api_bp

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание Flask приложения
app = Flask(__name__)
app.config.from_object(Config)

# Настройка CORS
CORS(app, origins=['*'])

# Регистрация API blueprint
app.register_blueprint(api_bp, url_prefix='/api/v1')

def get_translation(key: str, language: str = 'en') -> str:
    """Получает перевод для ключа на указанном языке"""
    translations = Config.TRANSLATIONS.get(language, Config.TRANSLATIONS['en'])
    return translations.get(key, key)

@app.route('/')
def index():
    """Главная страница"""
    language = session.get('language', Config.DEFAULT_LANGUAGE)
    
    def t(key):
        return get_translation(key, language)
    
    return render_template('index.html', language=language, t=t)

@app.route('/set_language/<language>')
def set_language(language):
    """Установка языка"""
    if language in Config.SUPPORTED_LANGUAGES:
        session['language'] = language
    return redirect(url_for('index'))

@app.route('/history')
def history():
    """Страница истории сигналов"""
    language = session.get('language', Config.DEFAULT_LANGUAGE)
    
    def t(key):
        return get_translation(key, language)
    
    try:
        signals = analyzer.get_signal_history(limit=100)
        return render_template('history.html', signals=signals, language=language, t=t)
    except Exception as e:
        logger.error(f"Error loading history: {e}")
        return render_template('history.html', signals=[], language=language, t=t)

@app.route('/statistics')
def statistics():
    """Страница статистики"""
    language = session.get('language', Config.DEFAULT_LANGUAGE)
    
    def t(key):
        return get_translation(key, language)
    
    try:
        stats = analyzer.get_statistics()
        return render_template('statistics.html', stats=stats, language=language, t=t)
    except Exception as e:
        logger.error(f"Error loading statistics: {e}")
        return render_template('statistics.html', stats={}, language=language, t=t)

@app.route('/monitoring')
def monitoring():
    """Страница мониторинга системы"""
    language = session.get('language', Config.DEFAULT_LANGUAGE)
    
    def t(key):
        return get_translation(key, language)
    
    return render_template('monitoring.html', language=language, t=t)

@app.route('/api')
def api_docs():
    """Документация API"""
    language = session.get('language', Config.DEFAULT_LANGUAGE)
    
    def t(key):
        return get_translation(key, language)
    
    return render_template('api_docs.html', language=language, t=t)

@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибки"""
    language = session.get('language', Config.DEFAULT_LANGUAGE)
    
    def t(key):
        return get_translation(key, language)
    
    return render_template('404.html', language=language, t=t), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработка 500 ошибки"""
    language = session.get('language', Config.DEFAULT_LANGUAGE)
    
    def t(key):
        return get_translation(key, language)
    
    logger.error(f"Internal server error: {error}")
    return render_template('500.html', language=language, t=t), 500

if __name__ == '__main__':
    try:
        # Инициализация базы данных
        db_manager.init_db()
        logger.info("Database initialized successfully")
        
        # Запуск приложения
        app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise 