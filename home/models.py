import locale
import random
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    ordem = models.IntegerField()
    
    def __str__(self):
        return self.nome
    
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=15,verbose_name="C.P.F")
    datanasc = models.DateField(verbose_name="Data de Nascimento")


    def __str__(self):
        return self.nome
    
    @property
    def datanascimento(self):
        """Retorna a data de nascimento no formato DD/MM/AAAA"""
        if self.datanasc:
            return self.datanasc.strftime('%d/%m/%Y')
        return None

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    img_base64 = models.TextField(blank=True)

    def __str__(self):
        return self.nome
    
    @property
    def estoque(self):
        # Tenta buscar o estoque, se não existir, cria um novo com qtde 0
        estoque_item, flag_created = Estoque.objects.get_or_create(produto=self, defaults={'qtde': 0})
        print(flag_created)
        return estoque_item
    
class Estoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    qtde = models.IntegerField()


    def __str__(self):
        return f'{self.produto.nome} - Quantidade: {self.qtde}'


class Pedido(models.Model):
    NOVO = 1
    EM_ANDAMENTO = 2
    CONCLUIDO = 3
    CANCELADO = 4


    STATUS_CHOICES = [
        (NOVO, 'Novo'),
        (EM_ANDAMENTO, 'Em Andamento'),
        (CONCLUIDO, 'Concluído'),
        (CANCELADO, 'Cancelado'),
    ]


    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    produtos = models.ManyToManyField(Produto, through='ItemPedido')
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=NOVO)
    
    def atualizar_status(self):
        """Atualiza o status automaticamente baseado nos pagamentos"""
        
        # Se o pedido já estiver cancelado, não mexemos
        if self.status == self.CANCELADO:
            return

        # Lógica de atualização
        if self.qtde_itens > 0 and self.debito <= 0:
            # Se tem itens e não deve nada -> Concluído
            self.status = self.CONCLUIDO
        elif self.total_pago > 0:
            # Se pagou alguma coisa mas ainda deve -> Em Andamento
            self.status = self.EM_ANDAMENTO
        else:
            # Se não pagou nada -> Novo
            self.status = self.NOVO
            
        self.save()
        
    @property
    def data_pedidof(self):
        if self.data_pedido:
            return self.data_pedido.strftime('%d/%m/%Y %H:%M')
        return None
    
    @property
    def total(self):
        lista = self.itempedido_set.all()
        total_pedido = sum([item.subtotal for item in lista]) 
        return total_pedido

    @property
    def qtde_itens(self):
        return self.itempedido_set.count() 

    # lista de todos os pagamentos realiados
    @property
    def pagamentos(self):
        return Pagamento.objects.filter(pedido=self)    
    
    #Calcula o total de todos os pagamentos do pedido
    @property
    def total_pago(self):
        total = sum(pagamento.valor for pagamento in self.pagamentos.all())
        return total    
    
    @property
    def debito(self):
        return self.total - self.total_pago

    @property
    def icms(self):
        # Converte 0.18 para Decimal antes de multiplicar
        return self.total * Decimal('0.18')

    @property
    def ipi(self):
        return self.total * Decimal('0.04')

    @property
    def pis(self):
        return self.total * Decimal('0.0165')

    @property
    def cofins(self):
        return self.total * Decimal('0.076')

    @property
    def total_impostos(self):
        return self.icms + self.ipi + self.pis + self.cofins

    @property
    def total_com_impostos(self):
        return self.total + self.total_impostos

    # --- Propriedade Chave de Acesso ---
    @property
    def chave_acesso(self):
        # Formato de chave fake: UF + AA + MM + CNPJ + MOD + SER + NUM + ALEATORIO
        # Ex: 35 24 01 12345678000199 55 001 000000001 12345678
        uf = "21" # Maranhão (exemplo)
        data = self.data_pedido.strftime('%y%m') if self.data_pedido else "0000"
        cnpj = "12345678000195" # CNPJ da sua empresa fictícia
        modelo = "55"
        serie = "001"
        numero_nota = f"{self.id:09}" # ID do pedido com 9 dígitos
        codigo_aleatorio = f"{random.randint(10000000, 99999999)}"
        
        chave = f"{uf}{data}{cnpj}{modelo}{serie}{numero_nota}1{codigo_aleatorio}"
        
        # Formatação visual (opcional, separa a cada 4 dígitos)
        return " ".join([chave[i:i+4] for i in range(0, len(chave), 4)])

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    qtde = models.PositiveIntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self):
        return self.qtde * self.preco

    def __str__(self):
        return f"{self.produto.nome} (Qtd: {self.qtde}) - Preço Unitário: {self.preco}"      
    
class Pagamento(models.Model):
    DINHEIRO = 1
    CARTAO = 2
    PIX = 3
    OUTRA = 4


    FORMA_CHOICES = [
        (DINHEIRO, 'Dinheiro'),
        (CARTAO, 'Cartão'),
        (PIX, 'Pix'),
        (OUTRA, 'Outra'),
    ]


    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    forma = models.IntegerField(choices=FORMA_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2,blank=False)
    data_pgto = models.DateTimeField(auto_now_add=True)
    
    @property
    def data_pgtof(self):
        """Retorna a data no formato DD/MM/AAAA HH:MM"""
        if self.data_pgto:
            return self.data_pgto.strftime('%d/%m/%Y %H:%M')
        return None
    
class HackerLog(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_descoberta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"HACKER DETECTADO: {self.usuario.username} em {self.data_descoberta}"
    
class RegistroAcesso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    login_data = models.DateTimeField(auto_now_add=True)
    logout_data = models.DateTimeField(null=True, blank=True)
    # NOVO CAMPO:
    ultima_atividade = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Acesso de {self.usuario.username}"

    @property
    def tempo_permanencia(self):
        """Calcula o tempo baseado na última vez que o usuário mexeu no sistema"""
        fim = self.logout_data if self.logout_data else self.ultima_atividade
        
        if fim:
            diferenca = fim - self.login_data
            # Remove os milisegundos para ficar limpo
            return str(diferenca).split('.')[0]
        
        return "Logado agora..."

# --- SINAIS (A MÁGICA ACONTECE AQUI) ---

# 1. Dispara quando o usuário faz LOGIN
@receiver(user_logged_in)
def registrar_login(sender, request, user, **kwargs):
    RegistroAcesso.objects.create(usuario=user)

# 2. Dispara quando o usuário faz LOGOUT (Clica em Sair)
@receiver(user_logged_out)
def registrar_logout(sender, request, user, **kwargs):
    # Pega o último registro desse usuário que ainda não tem data de saída
    registro = RegistroAcesso.objects.filter(usuario=user, logout_data__isnull=True).last()
    
    if registro:
        registro.logout_data = timezone.now()
        registro.save()


