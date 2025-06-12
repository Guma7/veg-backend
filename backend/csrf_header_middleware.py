import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class CSRFHeaderNormalizationMiddleware(MiddlewareMixin):
    """
    Middleware para normalizar cabeçalhos CSRF que podem chegar em diferentes capitalizações.
    
    Alguns proxies e navegadores podem alterar a capitalização dos cabeçalhos HTTP.
    Este middleware garante que o Django sempre encontre o token CSRF independentemente
    da capitalização do cabeçalho.
    """
    
    def process_request(self, request):
        # Lista de possíveis variações do cabeçalho CSRF
        csrf_header_variations = [
            'HTTP_X_CSRFTOKEN',
            'HTTP_X_CSRF_TOKEN', 
            'HTTP_X_Csrftoken',
            'HTTP_X_Csrf_Token'
        ]
        
        # Procurar por qualquer variação do cabeçalho CSRF
        csrf_token = None
        for header_name in csrf_header_variations:
            if header_name in request.META:
                csrf_token = request.META[header_name]
                break
        
        # Se encontrou um token, garantir que esteja no formato padrão do Django
        if csrf_token:
            # Adicionar logs para depuração
            logger.info(f"Token CSRF recebido: {csrf_token[:5]}...{csrf_token[-5:] if len(csrf_token) > 10 else ''}")
            logger.info(f"Comprimento do token CSRF recebido: {len(csrf_token)}")
            
            # Verificar e corrigir o comprimento do token (64 caracteres)
            if len(csrf_token) != 64:
                logger.warning(f"Token CSRF recebido com comprimento incorreto: {len(csrf_token)}, esperado: 64")
                
                # Ajustar o comprimento do token para 64 caracteres
                if len(csrf_token) < 64:
                    # Se for menor que 64, preencher com caracteres até atingir 64
                    padding = 'X' * (64 - len(csrf_token))
                    csrf_token = csrf_token + padding
                    logger.info(f"Token CSRF ajustado com padding: {len(csrf_token)}")
                elif len(csrf_token) > 64:
                    # Se for maior que 64, truncar para 64 caracteres
                    csrf_token = csrf_token[:64]
                    logger.info(f"Token CSRF truncado: {len(csrf_token)}")
            
            request.META['HTTP_X_CSRFTOKEN'] = csrf_token
        
        return None