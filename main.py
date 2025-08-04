import os
import logging
from flask import Flask, render_template, request, flash, send_from_directory, session, redirect, url_for

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Language translations
TRANSLATIONS = {
    'en': {
        'title': 'Z-Score Trading Signals',
        'subtitle': '4-Hour Mean Reversion Strategy • Cryptocurrency Analysis',
        'run_analysis': 'Run Analysis',
        'top_signals': 'Top Trading Signals',
        'symbol': 'Symbol',
        'cmc_rank': 'CMC Rank',
        'signal': 'Signal',
        'price': 'Price',
        'strength': 'Strength',
        'precision': 'Precision',
        'status': 'Status',
        'active': 'Active',
        'expired': 'Expired',
        'long': 'LONG',
        'short': 'SHORT',
        'ready_title': 'Ready to Analyze',
        'ready_text': 'Click "Run Analysis" to scan for Z-Score mean reversion signals across all cryptocurrency pairs.',
        'footer_text': 'Signals are valid for 4 hours • Sorted by validity, precision, and strength • Real crypto market data',
        'strategy_params': 'Strategy Parameters',
        'timeframe': 'Timeframe',
        'zscore_period': 'Z-Score Period',
        'threshold': 'Threshold',
        'take_profit': 'Take Profit',
        'risk_warning': 'Risk Warning',
        'risk_text': 'Trading involves substantial risk. Past performance does not guarantee future results. Use proper risk management and never risk more than you can afford to lose.'
    },
    'ru': {
        'title': 'Z-Score Торговые Сигналы',
        'subtitle': '4-часовая стратегия возврата к среднему • Анализ криптовалют',
        'run_analysis': 'Запустить анализ',
        'top_signals': 'Топ торговых сигналов',
        'symbol': 'Символ',
        'cmc_rank': 'Рейтинг CMC',
        'signal': 'Сигнал',
        'price': 'Цена',
        'strength': 'Сила',
        'precision': 'Точность',
        'status': 'Статус',
        'active': 'Активен',
        'expired': 'Истек',
        'long': 'ЛОНГ',
        'short': 'ШОРТ',
        'ready_title': 'Готов к анализу',
        'ready_text': 'Нажмите "Запустить анализ" для поиска сигналов возврата к среднему Z-Score по всем криптовалютным парам.',
        'footer_text': 'Сигналы действительны 4 часа • Отсортированы по валидности, точности и силе • Реальные данные крипторынка',
        'strategy_params': 'Параметры стратегии',
        'timeframe': 'Таймфрейм',
        'zscore_period': 'Период Z-Score',
        'threshold': 'Порог',
        'take_profit': 'Тейк-профит',
        'risk_warning': 'Предупреждение о рисках',
        'risk_text': 'Торговля связана с существенными рисками. Прошлые результаты не гарантируют будущих результатов. Используйте правильное управление рисками и никогда не рискуйте больше, чем можете себе позволить потерять.'
    }
}

def get_current_language():
    return session.get('language', 'ru')

def get_translation(key):
    lang = get_current_language()
    return TRANSLATIONS[lang].get(key, key)

@app.route('/set_language/<language>')
def set_language(language):
    if language in ['en', 'ru']:
        session['language'] = language
    return redirect(url_for('index'))

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error_message = None
    
    if request.method == "POST":
        try:
            import zcore
            results = zcore.run_analysis()
            if not results:
                flash(get_translation('no_signals_found'), "info")
        except Exception as e:
            error_message = f"Analysis failed: {str(e)}"
            logging.error(f"Analysis error: {e}")
            flash(error_message, "error")
    
    # Pass translations to template
    translations = TRANSLATIONS[get_current_language()]
    current_lang = get_current_language()
    
    return render_template("index.html", 
                         results=results, 
                         error_message=error_message,
                         t=translations,
                         current_lang=current_lang)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
