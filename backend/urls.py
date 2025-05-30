from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('recipes.urls')),
    path('api/auth/', include('users.urls_auth')),
    path('api/user/', include('users.urls')),
    
    # Servir arquivos de mídia em produção
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    
    # Servir arquivos estáticos em produção
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

# Em desenvolvimento, usar o método padrão do Django para servir arquivos de mídia
if settings.DEBUG:
    urlpatterns = urlpatterns[:-2] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
