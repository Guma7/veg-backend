from django.utils.deprecation import MiddlewareMixin

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
            request.META['HTTP_X_CSRFTOKEN'] = csrf_token
        
        return None