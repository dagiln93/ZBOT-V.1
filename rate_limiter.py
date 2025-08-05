from flask import request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, ip):
        now = time.time()
        # Очищаем старые запросы
        self.requests[ip] = [req_time for req_time in self.requests[ip] 
                            if now - req_time < self.window_seconds]
        
        # Проверяем лимит
        if len(self.requests[ip]) >= self.max_requests:
            return False
        
        # Добавляем новый запрос
        self.requests[ip].append(now)
        return True

rate_limiter = RateLimiter()

def rate_limit(f):
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        if not rate_limiter.is_allowed(ip):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.'
            }), 429
        return f(*args, **kwargs)
    return decorated_function 