from django.http import JsonResponse
import json
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class DetailedErrorMiddleware(MiddlewareMixin):
    """
    Middleware que intercepta respostas de erro e adiciona detalhes adicionais
    para facilitar a depuração no frontend.
    """
    
    def process_response(self, request, response):
        # Verificar se é uma resposta de erro (4xx ou 5xx)
        if 400 <= response.status_code < 600:
            # Verificar se é uma resposta JSON
            if 'application/json' in response.get('Content-Type', ''):
                try:
                    # Tentar obter o conteúdo atual
                    data = json.loads(response.content.decode('utf-8'))
                    
                    # Verificar se data é um dicionário antes de tentar atualizar
                    if isinstance(data, dict):
                        # Adicionar informações extras para depuração
                        data.update({
                            'status_code': response.status_code,
                            'request_path': request.path,
                            'request_method': request.method,
                            'user_authenticated': request.user.is_authenticated,
                            'debug_info': {
                                'headers': dict(request.headers),
                                'cookies': request.COOKIES,
                            }
                        })
                        
                        # Substituir o conteúdo da resposta
                        response.content = json.dumps(data).encode('utf-8')
                    else:
                        # Se for uma lista, criar um novo dicionário com os dados originais e informações extras
                        new_data = {
                            'data': data,
                            'status_code': response.status_code,
                            'request_path': request.path,
                            'request_method': request.method,
                            'user_authenticated': request.user.is_authenticated,
                            'debug_info': {
                                'headers': dict(request.headers),
                                'cookies': request.COOKIES,
                            }
                        }
                        response.content = json.dumps(new_data).encode('utf-8')
                except json.JSONDecodeError:
                    # Se não for um JSON válido, criar uma nova resposta
                    error_data = {
                        'detail': response.reason_phrase,
                        'status_code': response.status_code,
                        'request_path': request.path,
                        'request_method': request.method,
                        'user_authenticated': request.user.is_authenticated
                    }
                    response = JsonResponse(error_data, status=response.status_code)
            
            # Se não for JSON, converter para JSON com informações detalhadas
            elif response.status_code in [403, 401]:
                # Log detalhado para ajudar na depuração
                logger.warning(
                    f"Access denied: {response.status_code} - User: {request.user} - "
                    f"Method: {request.method} - Path: {request.path} - "
                    f"Headers: {dict(request.headers)}"
                )
                
                # Informações mais detalhadas sobre o erro
                error_type = 'forbidden_access' if response.status_code == 403 else 'authentication_required'
                error_message = response.reason_phrase or 'Acesso negado. Verifique suas permissões.' if response.status_code == 403 else 'Autenticação necessária.'
                
                error_data = {
                    'detail': error_message,
                    'status_code': response.status_code,
                    'error_type': error_type,
                    'request_path': request.path,
                    'request_method': request.method,
                    'user_authenticated': request.user.is_authenticated,
                    'debug_info': {
                        'headers': dict(request.headers),
                        'auth_header_present': 'Authorization' in request.headers,
                        'csrf_token_present': 'X-CSRFToken' in request.headers or 'X-Csrftoken' in request.headers,
                        'csrf_token_value': request.headers.get('X-CSRFToken') or request.headers.get('X-Csrftoken', 'Not present'),
                        'csrf_token_length': len(request.headers.get('X-CSRFToken') or request.headers.get('X-Csrftoken', '')),
                        'content_type': request.headers.get('Content-Type', 'Not specified')
                    }
                }
                
                # Configurar cabeçalhos CORS para garantir que o frontend receba a resposta
                response = JsonResponse(error_data, status=response.status_code)
                response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
                response['Access-Control-Allow-Credentials'] = 'true'
                
        return response