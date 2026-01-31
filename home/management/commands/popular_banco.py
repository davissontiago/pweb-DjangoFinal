import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from faker import Faker
from home.models import Categoria, Cliente, Produto, Pedido, ItemPedido, Pagamento, Estoque

class Command(BaseCommand):
    help = 'Limpa APENAS os dados deste projeto e popula com dados leves'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando limpeza cirúrgica (apenas tabelas do projeto)...'))
        
        # O SEGREDO: Tudo dentro de uma transação para ser rápido e seguro
        with transaction.atomic():
            
            # --- 1. LIMPEZA SEGURA (Ordem correta para evitar erros de chave estrangeira) ---
            # Apagamos primeiro os "filhos" e depois os "pais"
            Pagamento.objects.all().delete()
            ItemPedido.objects.all().delete()
            Pedido.objects.all().delete()
            Estoque.objects.all().delete()
            Produto.objects.all().delete()
            Cliente.objects.all().delete()
            Categoria.objects.all().delete()
            
            self.stdout.write(self.style.SUCCESS('Dados antigos do projeto removidos com sucesso!'))

            # --- 2. POPULAÇÃO LEVE (Configuração solicitada) ---
            fake = Faker('pt_BR')

            # Criar Categorias
            categorias_nomes = ['Eletrônicos', 'Informática', 'Moda', 'Casa', 'Esportes']
            categorias_objs = []
            for nome in categorias_nomes:
                cat = Categoria.objects.create(nome=nome, ordem=random.randint(1, 100))
                categorias_objs.append(cat)

            # Criar 8 Clientes
            for _ in range(8):
                Cliente.objects.create(
                    nome=fake.name(),
                    cpf=fake.cpf(),
                    datanasc=fake.date_of_birth(minimum_age=18, maximum_age=90)
                )
            self.stdout.write(self.style.SUCCESS('8 Clientes criados.'))

            # Criar 10 Produtos
            adjetivos = ['Pro', 'Max', 'Slim', 'Gamer', '4K', 'Smart']
            substantivos = ['Mouse', 'Teclado', 'Cadeira', 'Mesa', 'Fone', 'Cabo']
            
            produtos_objs = []
            for _ in range(10):
                nome_produto = f"{random.choice(substantivos)} {fake.word().capitalize()} {random.choice(adjetivos)}"
                prod = Produto.objects.create(
                    nome=nome_produto,
                    preco=Decimal(random.uniform(50.0, 1000.0)),
                    categoria=random.choice(categorias_objs),
                    img_base64="" 
                )
                # Ajusta estoque
                estoque = prod.estoque
                estoque.qtde = random.randint(5, 50)
                estoque.save()
                produtos_objs.append(prod)
                
            self.stdout.write(self.style.SUCCESS('10 Produtos criados.'))

            # Criar 12 Pedidos
            clientes_todos = list(Cliente.objects.all())
            
            for _ in range(12):
                cliente = random.choice(clientes_todos)
                
                # Criar pedido
                pedido = Pedido.objects.create(
                    cliente=cliente,
                    status=Pedido.NOVO
                )
                
                # Data aleatória (últimos 6 meses)
                pedido.data_pedido = fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone())
                pedido.save()

                # Adicionar Itens (1 a 3 itens por pedido)
                qtd_itens = random.randint(1, 3)
                produtos_escolhidos = random.sample(produtos_objs, qtd_itens)
                
                for produto in produtos_escolhidos:
                    qtde_compra = random.randint(1, 2)
                    
                    # Verifica estoque fictício
                    if produto.estoque.qtde >= qtde_compra:
                        produto.estoque.qtde -= qtde_compra
                        produto.estoque.save()
                        
                        ItemPedido.objects.create(
                            pedido=pedido,
                            produto=produto,
                            qtde=qtde_compra,
                            preco=produto.preco
                        )

                # Pagamentos e Status Variados
                cenario = random.choice(['novo', 'novo', 'andamento', 'concluido']) # Mais 'novos' para variar
                total_pedido = pedido.total 

                if total_pedido > 0:
                    if cenario == 'andamento':
                        # Paga metade
                        Pagamento.objects.create(pedido=pedido, forma=1, valor=total_pedido / 2)
                    elif cenario == 'concluido':
                        # Paga tudo
                        Pagamento.objects.create(pedido=pedido, forma=2, valor=total_pedido)
                    
                    # Atualiza status (menos se for novo)
                    if cenario != 'novo':
                        pedido.atualizar_status()

        self.stdout.write(self.style.SUCCESS('Banco atualizado com sucesso (Limpeza + Dados Leves)!'))