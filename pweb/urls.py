from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    
    # Adicione esta linha para incluir as URLs de autenticação padrão (login, logout)
    path('accounts/', include('django.contrib.auth.urls')), 
]