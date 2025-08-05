import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
import threading
from collections import defaultdict, deque
import json
import os

logger = logging.getLogger(__name__)

class CacheManager:
    """Менеджер кэширования для оптимизации производительности"""
    
    def __init__(self, default_timeout: int = 300):
        self.cache = {}
        self.timeouts = {}
        self.default_timeout = default_timeout
        self.lock = threading.Lock()
        
    def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша"""
        with self.lock:
            if key in self.cache:
                if key in self.timeouts:
                    if datetime.now() < self.timeouts[key]:
                        return self.cache[key]
                    else:
                        # Удаляем истекший кэш
                        del self.cache[key]
                        del self.timeouts[key]
        return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Устанавливает значение в кэш"""
        with self.lock:
            self.cache[key] = value
            self.timeouts[key] = datetime.now() + timedelta(seconds=timeout or self.default_timeout)
    
    def clear(self) -> None:
        """Очищает весь кэш"""
        with self.lock:
            self.cache.clear()
            self.timeouts.clear()
    
    def clear_expired(self) -> None:
        """Очищает истекшие записи кэша"""
        with self.lock:
            current_time = datetime.now()
            expired_keys = [
                key for key, expiry in self.timeouts.items()
                if current_time >= expiry
            ]
            for key in expired_keys:
                if key in self.cache:
                    del self.cache[key]
                if key in self.timeouts:
                    del self.timeouts[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Получает статистику кэша"""
        with self.lock:
            return {
                "total_entries": len(self.cache),
                "expired_entries": len([k for k, v in self.timeouts.items() 
                                      if datetime.now() >= v]),
                "memory_usage": sum(len(str(v)) for v in self.cache.values())
            }

class PerformanceMonitor:
    """Монитор производительности системы"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "min_time": float('inf'),
            "max_time": 0.0,
            "errors": 0,
            "last_execution": None
        })
        self.lock = threading.Lock()
        
    def record_metric(self, operation: str, execution_time: float, 
                     success: bool = True, error: Optional[str] = None) -> None:
        """Записывает метрику выполнения операции"""
        with self.lock:
            metric = self.metrics[operation]
            metric["count"] += 1
            metric["total_time"] += execution_time
            metric["min_time"] = min(metric["min_time"], execution_time)
            metric["max_time"] = max(metric["max_time"], execution_time)
            metric["last_execution"] = datetime.now()
            
            if not success:
                metric["errors"] += 1
                if error:
                    logger.error(f"Operation {operation} failed: {error}")
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Получает все метрики"""
        with self.lock:
            result = {}
            for operation, metric in self.metrics.items():
                avg_time = (metric["total_time"] / metric["count"] 
                           if metric["count"] > 0 else 0)
                success_rate = ((metric["count"] - metric["errors"]) / metric["count"] * 100
                              if metric["count"] > 0 else 0)
                
                result[operation] = {
                    "count": metric["count"],
                    "avg_time": round(avg_time, 3),
                    "min_time": metric["min_time"] if metric["min_time"] != float('inf') else 0,
                    "max_time": metric["max_time"],
                    "success_rate": round(success_rate, 2),
                    "errors": metric["errors"],
                    "last_execution": metric["last_execution"].isoformat() 
                    if metric["last_execution"] else None
                }
            return result
    
    def reset_metrics(self) -> None:
        """Сбрасывает все метрики"""
        with self.lock:
            self.metrics.clear()

class SystemHealthMonitor:
    """Монитор здоровья системы"""
    
    def __init__(self):
        self.health_status = {
            "api_connectivity": True,
            "database_connectivity": True,
            "analysis_performance": True,
            "last_check": datetime.now()
        }
        self.alerts = deque(maxlen=100)
        self.lock = threading.Lock()
    
    def check_api_health(self, api_client) -> bool:
        """Проверяет здоровье API соединения"""
        try:
            start_time = time.time()
            symbols = api_client.get_all_futures_symbols()
            execution_time = time.time() - start_time
            
            is_healthy = len(symbols) > 0 and execution_time < 10.0
            
            with self.lock:
                self.health_status["api_connectivity"] = is_healthy
                self.health_status["last_check"] = datetime.now()
                
                if not is_healthy:
                    self.alerts.append({
                        "timestamp": datetime.now(),
                        "type": "API_HEALTH",
                        "message": f"API connectivity issues. Response time: {execution_time:.2f}s, Symbols: {len(symbols)}"
                    })
            
            return is_healthy
            
        except Exception as e:
            with self.lock:
                self.health_status["api_connectivity"] = False
                self.alerts.append({
                    "timestamp": datetime.now(),
                    "type": "API_ERROR",
                    "message": f"API connection failed: {str(e)}"
                })
            return False
    
    def check_database_health(self, db_manager) -> bool:
        """Проверяет здоровье базы данных"""
        try:
            start_time = time.time()
            # Простая проверка - попытка получить статистику
            stats = db_manager.get_statistics()
            execution_time = time.time() - start_time
            
            is_healthy = execution_time < 5.0
            
            with self.lock:
                self.health_status["database_connectivity"] = is_healthy
                
                if not is_healthy:
                    self.alerts.append({
                        "timestamp": datetime.now(),
                        "type": "DB_HEALTH",
                        "message": f"Database performance issues. Response time: {execution_time:.2f}s"
                    })
            
            return is_healthy
            
        except Exception as e:
            with self.lock:
                self.health_status["database_connectivity"] = False
                self.alerts.append({
                    "timestamp": datetime.now(),
                    "type": "DB_ERROR",
                    "message": f"Database connection failed: {str(e)}"
                })
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Получает текущий статус здоровья системы"""
        with self.lock:
            return {
                "status": self.health_status,
                "alerts": list(self.alerts),
                "overall_health": all(self.health_status.values())
            }

def monitor_performance(operation_name: str):
    """Декоратор для мониторинга производительности функций"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                execution_time = time.time() - start_time
                performance_monitor.record_metric(operation_name, execution_time, success, error)
        
        return wrapper
    return decorator

def cache_result(timeout: int = 300):
    """Декоратор для кэширования результатов функций"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Создаем ключ кэша на основе имени функции и аргументов
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Проверяем кэш
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Выполняем функцию и кэшируем результат
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator

# Глобальные экземпляры
cache_manager = CacheManager()
performance_monitor = PerformanceMonitor()
health_monitor = SystemHealthMonitor()

def get_system_status() -> Dict[str, Any]:
    """Получает полный статус системы"""
    return {
        "cache_stats": cache_manager.get_stats(),
        "performance_metrics": performance_monitor.get_metrics(),
        "health_status": health_monitor.get_health_status(),
        "timestamp": datetime.now().isoformat()
    }

def cleanup_expired_cache():
    """Очищает истекшие записи кэша"""
    cache_manager.clear_expired()
    logger.info("Expired cache entries cleaned up")

def log_system_status():
    """Логирует текущий статус системы"""
    status = get_system_status()
    logger.info(f"System Status: {json.dumps(status, indent=2, default=str)}") 