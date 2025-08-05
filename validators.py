import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from config import Config

class ValidationError(Exception):
    """Исключение для ошибок валидации"""
    pass

class DataValidator:
    """Класс для валидации входных данных"""
    
    @staticmethod
    def validate_symbol(symbol: str) -> Tuple[bool, str]:
        """Валидация символа криптовалюты"""
        if not symbol:
            return False, "Symbol cannot be empty"
        
        if not isinstance(symbol, str):
            return False, "Symbol must be a string"
        
        # Проверяем формат символа (только буквы, цифры и дефисы)
        if not re.match(r'^[a-zA-Z0-9-]+$', symbol):
            return False, "Symbol contains invalid characters"
        
        # Проверяем длину
        if len(symbol) < 1 or len(symbol) > 20:
            return False, "Symbol length must be between 1 and 20 characters"
        
        return True, ""
    
    @staticmethod
    def validate_timeframe(timeframe: str) -> Tuple[bool, str]:
        """Валидация таймфрейма"""
        valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
        
        if not timeframe:
            return False, "Timeframe cannot be empty"
        
        if timeframe not in valid_timeframes:
            return False, f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}"
        
        return True, ""
    
    @staticmethod
    def validate_numeric_range(value: Any, min_val: float, max_val: float, field_name: str) -> Tuple[bool, str]:
        """Валидация числового значения в заданном диапазоне"""
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return False, f"{field_name} must be a number"
        
        if num_value < min_val or num_value > max_val:
            return False, f"{field_name} must be between {min_val} and {max_val}"
        
        return True, ""
    
    @staticmethod
    def validate_strategy_params(params: Dict[str, Any]) -> Tuple[bool, str]:
        """Валидация параметров стратегии"""
        required_fields = ['z_len', 'threshold', 'tp_pct', 'sl_pct']
        
        for field in required_fields:
            if field not in params:
                return False, f"Missing required field: {field}"
        
        # Валидация Z-Score периода
        is_valid, error = DataValidator.validate_numeric_range(
            params['z_len'], 5, 100, 'Z-Score period'
        )
        if not is_valid:
            return False, error
        
        # Валидация порога
        is_valid, error = DataValidator.validate_numeric_range(
            params['threshold'], 0.5, 5.0, 'Threshold'
        )
        if not is_valid:
            return False, error
        
        # Валидация take profit
        is_valid, error = DataValidator.validate_numeric_range(
            params['tp_pct'], 0.1, 10.0, 'Take profit percentage'
        )
        if not is_valid:
            return False, error
        
        # Валидация stop loss
        is_valid, error = DataValidator.validate_numeric_range(
            params['sl_pct'], 0.1, 5.0, 'Stop loss percentage'
        )
        if not is_valid:
            return False, error
        
        return True, ""
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, str]:
        """Валидация диапазона дат"""
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            return False, "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        
        if start >= end:
            return False, "Start date must be before end date"
        
        # Проверяем, что диапазон не слишком большой (максимум 1 год)
        if (end - start) > timedelta(days=365):
            return False, "Date range cannot exceed 1 year"
        
        return True, ""
    
    @staticmethod
    def validate_filter_params(filters: Dict[str, Any]) -> Tuple[bool, str]:
        """Валидация параметров фильтрации"""
        valid_filters = ['symbol', 'direction', 'min_precision', 'max_precision', 'valid_only']
        
        for key in filters:
            if key not in valid_filters:
                return False, f"Invalid filter parameter: {key}"
        
        # Валидация направления
        if 'direction' in filters:
            direction = filters['direction']
            if direction not in ['long', 'short', 'all']:
                return False, "Direction must be 'long', 'short', or 'all'"
        
        # Валидация точности
        if 'min_precision' in filters:
            is_valid, error = DataValidator.validate_numeric_range(
                filters['min_precision'], 0.0, 1.0, 'Minimum precision'
            )
            if not is_valid:
                return False, error
        
        if 'max_precision' in filters:
            is_valid, error = DataValidator.validate_numeric_range(
                filters['max_precision'], 0.0, 1.0, 'Maximum precision'
            )
            if not is_valid:
                return False, error
        
        # Проверяем, что min_precision <= max_precision
        if 'min_precision' in filters and 'max_precision' in filters:
            if filters['min_precision'] > filters['max_precision']:
                return False, "Minimum precision cannot be greater than maximum precision"
        
        return True, ""
    
    @staticmethod
    def validate_sort_params(sort_by: str, sort_order: str) -> Tuple[bool, str]:
        """Валидация параметров сортировки"""
        valid_sort_fields = ['symbol', 'direction', 'price', 'strength', 'precision', 'signal_time', 'cmc_rank']
        valid_sort_orders = ['asc', 'desc']
        
        if sort_by not in valid_sort_fields:
            return False, f"Invalid sort field. Must be one of: {', '.join(valid_sort_fields)}"
        
        if sort_order not in valid_sort_orders:
            return False, f"Invalid sort order. Must be 'asc' or 'desc'"
        
        return True, ""
    
    @staticmethod
    def validate_pagination_params(page: int, per_page: int) -> Tuple[bool, str]:
        """Валидация параметров пагинации"""
        if page < 1:
            return False, "Page number must be greater than 0"
        
        if per_page < 1 or per_page > 100:
            return False, "Items per page must be between 1 and 100"
        
        return True, ""
    
    @staticmethod
    def validate_api_request_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Валидация данных API запроса"""
        if not isinstance(data, dict):
            return False, "Request data must be a dictionary"
        
        # Проверяем обязательные поля
        required_fields = ['symbols']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Валидация списка символов
        symbols = data['symbols']
        if not isinstance(symbols, list):
            return False, "Symbols must be a list"
        
        if len(symbols) == 0:
            return False, "Symbols list cannot be empty"
        
        if len(symbols) > 50:
            return False, "Maximum 50 symbols allowed per request"
        
        # Валидация каждого символа
        for symbol in symbols:
            is_valid, error = DataValidator.validate_symbol(symbol)
            if not is_valid:
                return False, f"Invalid symbol '{symbol}': {error}"
        
        # Валидация опциональных параметров
        if 'strategy_params' in data:
            is_valid, error = DataValidator.validate_strategy_params(data['strategy_params'])
            if not is_valid:
                return False, f"Invalid strategy parameters: {error}"
        
        return True, ""

class RequestValidator:
    """Класс для валидации HTTP запросов"""
    
    @staticmethod
    def validate_analysis_request(request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Валидация запроса на анализ"""
        try:
            # Проверяем базовую структуру
            if not isinstance(request_data, dict):
                return False, "Request data must be a dictionary"
            
            # Валидация символов
            symbols = request_data.get('symbols', [])
            if not isinstance(symbols, list):
                return False, "Symbols must be a list"
            
            if len(symbols) == 0:
                return False, "At least one symbol is required"
            
            if len(symbols) > 50:
                return False, "Maximum 50 symbols allowed"
            
            # Валидация каждого символа
            for symbol in symbols:
                is_valid, error = DataValidator.validate_symbol(symbol)
                if not is_valid:
                    return False, f"Invalid symbol '{symbol}': {error}"
            
            # Валидация опциональных параметров
            if 'filters' in request_data:
                is_valid, error = DataValidator.validate_filter_params(request_data['filters'])
                if not is_valid:
                    return False, f"Invalid filters: {error}"
            
            if 'sort_by' in request_data:
                sort_order = request_data.get('sort_order', 'desc')
                is_valid, error = DataValidator.validate_sort_params(
                    request_data['sort_by'], sort_order
                )
                if not is_valid:
                    return False, f"Invalid sort parameters: {error}"
            
            return True, ""
            
        except Exception as e:
            logging.error(f"Validation error: {e}")
            return False, f"Validation failed: {str(e)}"
    
    @staticmethod
    def validate_history_request(request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Валидация запроса на получение истории"""
        try:
            if not isinstance(request_data, dict):
                return False, "Request data must be a dictionary"
            
            # Проверяем обязательные поля
            if 'symbol' not in request_data:
                return False, "Symbol is required"
            
            # Валидация символа
            is_valid, error = DataValidator.validate_symbol(request_data['symbol'])
            if not is_valid:
                return False, f"Invalid symbol: {error}"
            
            # Валидация опциональных параметров
            if 'days' in request_data:
                is_valid, error = DataValidator.validate_numeric_range(
                    request_data['days'], 1, 365, 'Days'
                )
                if not is_valid:
                    return False, error
            
            if 'filters' in request_data:
                is_valid, error = DataValidator.validate_filter_params(request_data['filters'])
                if not is_valid:
                    return False, f"Invalid filters: {error}"
            
            return True, ""
            
        except Exception as e:
            logging.error(f"Validation error: {e}")
            return False, f"Validation failed: {str(e)}" 