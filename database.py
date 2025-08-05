from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from config import Config

Base = declarative_base()

class Signal(Base):
    """Модель для хранения торговых сигналов"""
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    current_price = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False)
    sma_50 = Column(Float, nullable=False)
    rsi = Column(Float, nullable=False)
    macd_line = Column(Float, nullable=False)
    macd_signal = Column(Float, nullable=False)
    macd_histogram = Column(Float, nullable=False)
    volume_sma = Column(Float, nullable=False)
    volume_ratio = Column(Float, nullable=False)
    signal = Column(String(10), nullable=False)  # 'BUY' или 'SELL'
    strength = Column(String(20), nullable=False)  # 'STRONG', 'MODERATE', 'WEAK'
    precision = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    valid = Column(Boolean, default=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'current_price': self.current_price,
            'z_score': self.z_score,
            'sma_50': self.sma_50,
            'rsi': self.rsi,
            'macd_line': self.macd_line,
            'macd_signal': self.macd_signal,
            'macd_histogram': self.macd_histogram,
            'volume_sma': self.volume_sma,
            'volume_ratio': self.volume_ratio,
            'signal': self.signal,
            'strength': self.strength,
            'precision': self.precision,
            'timestamp': self.timestamp.isoformat(),
            'valid': self.valid
        }

class DatabaseManager:
    """Менеджер базы данных"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Настройка подключения к базе данных"""
        try:
            self.engine = create_engine(Config.DATABASE_URL)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Создание таблиц
            Base.metadata.create_all(bind=self.engine)
            logging.info("Database setup completed successfully")
            
        except Exception as e:
            logging.error(f"Database setup failed: {e}")
            raise
    
    def init_db(self):
        """Инициализация базы данных"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            raise
    
    def get_session(self):
        """Получение сессии базы данных"""
        return self.SessionLocal()
    
    def save_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Сохранение одного сигнала в базу данных"""
        try:
            session = self.get_session()
            
            # Преобразуем timestamp если это строка
            if isinstance(signal_data['timestamp'], str):
                timestamp = datetime.fromisoformat(signal_data['timestamp'].replace('Z', '+00:00'))
            else:
                timestamp = signal_data['timestamp']
            
            signal = Signal(
                symbol=signal_data['symbol'],
                current_price=signal_data['current_price'],
                z_score=signal_data['z_score'],
                sma_50=signal_data['sma_50'],
                rsi=signal_data['rsi'],
                macd_line=signal_data['macd_line'],
                macd_signal=signal_data['macd_signal'],
                macd_histogram=signal_data['macd_histogram'],
                volume_sma=signal_data['volume_sma'],
                volume_ratio=signal_data['volume_ratio'],
                signal=signal_data['signal'],
                strength=signal_data['strength'],
                precision=signal_data['precision'],
                timestamp=timestamp,
                valid=signal_data['valid']
            )
            
            session.add(signal)
            session.commit()
            session.close()
            
            logging.info(f"Saved signal for {signal_data['symbol']}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving signal: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def save_signals(self, signals: List[Dict[str, Any]]) -> bool:
        """Сохранение списка сигналов в базу данных"""
        try:
            session = self.get_session()
            
            for signal_data in signals:
                # Преобразуем timestamp если это строка
                if isinstance(signal_data['timestamp'], str):
                    timestamp = datetime.fromisoformat(signal_data['timestamp'].replace('Z', '+00:00'))
                else:
                    timestamp = signal_data['timestamp']
                
                signal = Signal(
                    symbol=signal_data['symbol'],
                    current_price=signal_data['current_price'],
                    z_score=signal_data['z_score'],
                    sma_50=signal_data['sma_50'],
                    rsi=signal_data['rsi'],
                    macd_line=signal_data['macd_line'],
                    macd_signal=signal_data['macd_signal'],
                    macd_histogram=signal_data['macd_histogram'],
                    volume_sma=signal_data['volume_sma'],
                    volume_ratio=signal_data['volume_ratio'],
                    signal=signal_data['signal'],
                    strength=signal_data['strength'],
                    precision=signal_data['precision'],
                    timestamp=timestamp,
                    valid=signal_data['valid']
                )
                session.add(signal)
            
            session.commit()
            session.close()
            logging.info(f"Saved {len(signals)} signals to database")
            return True
            
        except Exception as e:
            logging.error(f"Error saving signals: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def get_signals(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение сигналов с фильтрацией"""
        try:
            session = self.get_session()
            
            query = session.query(Signal)
            
            if symbol:
                query = query.filter(Signal.symbol == symbol)
            
            signals = query.order_by(Signal.timestamp.desc()).limit(limit).all()
            
            session.close()
            
            return [signal.to_dict() for signal in signals]
            
        except Exception as e:
            logging.error(f"Error getting signals: {e}")
            return []
    
    def get_recent_signals(self, limit: int = 50, symbol: Optional[str] = None, 
                          direction: Optional[str] = None, valid_only: bool = False) -> List[Dict[str, Any]]:
        """Получение последних сигналов с фильтрацией"""
        try:
            session = self.get_session()
            
            query = session.query(Signal)
            
            if symbol:
                query = query.filter(Signal.symbol == symbol)
            
            if direction:
                query = query.filter(Signal.signal == direction)
            
            if valid_only:
                query = query.filter(Signal.valid == True)
            
            signals = query.order_by(Signal.timestamp.desc()).limit(limit).all()
            
            session.close()
            
            return [signal.to_dict() for signal in signals]
            
        except Exception as e:
            logging.error(f"Error getting signals: {e}")
            return []
    
    def get_signal_history(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Получение истории сигналов для конкретного символа"""
        try:
            session = self.get_session()
            
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            signals = session.query(Signal).filter(
                Signal.symbol == symbol,
                Signal.timestamp >= cutoff_date
            ).order_by(Signal.timestamp.desc()).all()
            
            session.close()
            
            return [signal.to_dict() for signal in signals]
            
        except Exception as e:
            logging.error(f"Error getting signal history: {e}")
            return []
    
    def update_signal_validity(self):
        """Обновление валидности сигналов (помечаем старые как недействительные)"""
        try:
            session = self.get_session()
            
            from datetime import timedelta
            validity_cutoff = datetime.utcnow() - timedelta(hours=4)  # 4 часа
            
            session.query(Signal).filter(
                Signal.timestamp < validity_cutoff,
                Signal.valid == True
            ).update({'valid': False})
            
            session.commit()
            session.close()
            
            logging.info("Updated signal validity")
            
        except Exception as e:
            logging.error(f"Error updating signal validity: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики сигналов"""
        try:
            session = self.get_session()
            
            total_signals = session.query(Signal).count()
            valid_signals = session.query(Signal).filter(Signal.valid == True).count()
            buy_signals = session.query(Signal).filter(Signal.signal == 'BUY').count()
            sell_signals = session.query(Signal).filter(Signal.signal == 'SELL').count()
            
            # Средняя точность
            from sqlalchemy import func
            avg_precision = session.query(func.avg(Signal.precision)).scalar() or 0.0
            
            # Последнее обновление
            last_update = session.query(Signal).order_by(Signal.timestamp.desc()).first()
            last_update_time = last_update.timestamp.strftime('%Y-%m-%d %H:%M') if last_update else 'Нет данных'
            
            session.close()
            
            return {
                'total_signals': total_signals,
                'valid_signals': valid_signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'avg_precision': round(avg_precision, 1),
                'last_update': last_update_time
            }
            
        except Exception as e:
            logging.error(f"Error getting statistics: {e}")
            return {}

# Глобальный экземпляр менеджера базы данных
db_manager = DatabaseManager() 