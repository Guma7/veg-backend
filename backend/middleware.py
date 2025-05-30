from django.http import HttpResponse
from django.core.cache import cache
from datetime import datetime, timedelta

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        key = f'rate_limit_{ip}'
        
        requests = cache.get(key, [])
        now = datetime.now()
        
        # Remove requisições mais antigas que 1 minuto
        requests = [req for req in requests if now - req < timedelta(minutes=1)]
        
        if len(requests) >= 300:  # Limite de 300 requisições por minuto (aumentado de 100)
            return HttpResponse('Too Many Requests', status=429)
        
        requests.append(now)
        cache.set(key, requests, 60)  # Expira em 60 segundos
        
        return self.get_response(request)