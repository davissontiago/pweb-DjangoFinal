# home/admin.py
from django.contrib import admin
from .models import * # (Se já tiver importando *, ok. Senão importe HackerLog)

# ... outros registros ...

@admin.register(HackerLog)
class HackerLogAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'data_descoberta')
    list_filter = ('data_descoberta',)
    search_fields = ('usuario__username',)
    
@admin.register(RegistroAcesso)
class RegistroAcessoAdmin(admin.ModelAdmin):
    # Adicionamos 'ultima_atividade' na lista
    list_display = ('usuario', 'login_data', 'ultima_atividade', 'logout_data', 'mostrar_tempo')
    
    def mostrar_tempo(self, obj):
        return obj.tempo_permanencia
    mostrar_tempo.short_description = "Tempo Total"
    
