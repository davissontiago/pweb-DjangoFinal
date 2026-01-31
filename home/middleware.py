from django.utils import timezone
from .models import RegistroAcesso

class MonitoramentoAtividadeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Código executado ANTES de carregar a página (Request)
        
        if request.user.is_authenticated:
            # Tenta pegar o último registro de acesso desse usuário que ainda está aberto
            registro = RegistroAcesso.objects.filter(
                usuario=request.user, 
                logout_data__isnull=True
            ).last()

            if registro:
                # Atualiza o horário da última atividade
                registro.ultima_atividade = timezone.now()
                registro.save()

        response = self.get_response(request)
        return response