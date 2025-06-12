from rest_framework.views import exception_handler
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from django.http import JsonResponse
import logging

logger = logging.getLogger('django')

def custom_exception_handler(exc, context):
    """Custom exception handler that provides more detailed error messages
    for authentication and permission errors.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If it's a permission error, add more details
    if isinstance(exc, PermissionDenied):
        if response is not None:
            # Log the error with more context
            request = context.get('request')
            view = context.get('view')
            logger.error(
                f"Permission denied: {str(exc)} - User: {request.user} - "
                f"View: {view.__class__.__name__} - Method: {request.method} - "
                f"Path: {request.path}"
            )
            
            # Add more details to the response
            response.data = {
                'detail': str(exc),
                'status_code': 403,
                'error_type': 'permission_denied',
                'required_permissions': getattr(view, 'permission_classes', []),
                'user_authenticated': request.user.is_authenticated,
                'request_method': request.method,
                'request_path': request.path,
                'debug_info': {
                    'headers': dict(request.headers),
                    'auth_header_present': 'Authorization' in request.headers,
                     'csrf_token_present': 'X-CSRFToken' in request.headers,  
                    'content_type': request.headers.get('Content-Type', 'Not specified')
                }
            }
            
            # Configurar cabeçalhos CORS para garantir que o frontend receba a resposta
            response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            response['Access-Control-Allow-Credentials'] = 'true'
    
    # If it's an authentication error, add more details
    elif isinstance(exc, AuthenticationFailed):
        if response is not None:
            request = context.get('request')
            logger.warning(
                f"Authentication failed: {str(exc)} - Method: {request.method} - "
                f"Path: {request.path} - Headers: {dict(request.headers)}"
            )
            
            response.data = {
                'detail': str(exc),
                'status_code': 401,
                'error_type': 'authentication_failed',
                'request_method': request.method,
                'request_path': request.path,
                'debug_info': {
                    'headers': dict(request.headers),
                    'auth_header_present': 'Authorization' in request.headers,
                    'csrf_token_present': 'X-CSRFToken' in request.headers,  
                    'content_type': request.headers.get('Content-Type', 'Not specified')
                }
            }
            
            # Configurar cabeçalhos CORS para garantir que o frontend receba a resposta
            response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            response['Access-Control-Allow-Credentials'] = 'true'
    
    return response