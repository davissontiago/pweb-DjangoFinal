from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.apps import apps 
from django.http import JsonResponse
from .models import *
from .forms import *

@login_required
def index(request):
    # Contagens básicas
    qtd_pedidos = Pedido.objects.count()
    qtd_produtos = Produto.objects.count()
    qtd_clientes = Cliente.objects.count()
    
    # Informação Extra: Soma de todos os pagamentos registrados no sistema
    faturamento = Pagamento.objects.aggregate(Sum('valor'))['valor__sum'] or 0
    
    contexto = {
        'qtd_pedidos': qtd_pedidos,
        'qtd_produtos': qtd_produtos,
        'qtd_clientes': qtd_clientes,
        'faturamento': faturamento, # Passando o extra
    }
    return render(request, 'index.html', contexto)

@login_required
def categoria(request):
    contexto = {
        'lista': Categoria.objects.all().order_by('-id'),
    }
    return render(request, 'categoria/lista.html',contexto)

@login_required
def form_categoria(request):
    if request.method == 'POST':
       form = CategoriaForm(request.POST) # instancia o modelo com os dados do form
       if form.is_valid():# faz a validação do formulário
            form.save() # salva a instancia do modelo no banco de dados
            return redirect('categoria') # redireciona para a listagem
    else:# método é get, novo registro
        form = CategoriaForm() # formulário vazio
    contexto = {
        'form':form,
    }
    return render(request, 'categoria/formulario.html', contexto)

@login_required
def editar_categoria(request, id):
    try:
        categoria = Categoria.objects.get(pk=id)
    except Categoria.DoesNotExist:
        # Caso o registro não seja encontrado, exibe a mensagem de erro
        messages.error(request, 'Registro não encontrado')
        return redirect('categoria')  # Redireciona para a listagem
     
    if request.method == 'POST':
        # combina os dados do formulário submetido com a instância do objeto existente, permitindo editar seus valores.
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save() # save retorna o objeto salvo
            messages.success(request, 'Operação realizada com Sucesso')
            return redirect('categoria') # redireciona para a listagem
    else:
         form = CategoriaForm(instance=categoria)
    return render(request, 'categoria/formulario.html', {'form': form,})

@login_required
def remover_categoria(request, id):
    try:
        categoria = Categoria.objects.get(pk=id)
    except Categoria.DoesNotExist:
        # Caso o registro não seja encontrado, exibe a mensagem de erro
        messages.error(request, 'Registro não encontrado')
        return redirect('categoria')  # Redireciona para a listagem
    
    # Busca a categoria e a exclui do banco
    categoria = Categoria.objects.get(pk=id)
    categoria.delete()
    # Redireciona volta para a listagem
    messages.success(request, 'Operação realizada com Sucesso')
    return redirect('categoria')

@login_required
def detalhes_categoria(request, id):
    # Busca a categoria pelo ID
    categoria = Categoria.objects.get(pk=id)
    contexto = {
        'categoria': categoria,
    }
    # Renderiza o template de detalhes
    return render(request, 'categoria/detalhes.html', contexto)

# ==============================================================================
# CLIENTE (CRUD Completo)
# ==============================================================================

@login_required
def cliente(request):
    contexto = {
        'lista': Cliente.objects.all().order_by('-id'),
    }
    return render(request, 'cliente/lista.html', context=contexto)

@login_required
def form_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente salvo com sucesso!')
            return redirect('cliente')
    else:
        form = ClienteForm()
    
    return render(request, 'cliente/formulario.html', {'form': form})

@login_required
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, pk=id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('cliente')
    else:
        form = ClienteForm(instance=cliente)
        
    return render(request, 'cliente/formulario.html', {'form': form})

@login_required
def remover_cliente(request, id):
    cliente = get_object_or_404(Cliente, pk=id)
    cliente.delete()
    messages.success(request, 'Cliente removido com sucesso!')
    return redirect('cliente')


# ==============================================================================
# PRODUTO (CRUD Completo)
# ==============================================================================

@login_required
def produto(request):
    contexto = {
        'lista': Produto.objects.all().order_by('-id'),
    }
    return render(request, 'produto/lista.html', context=contexto)

@login_required
def form_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto salvo com sucesso!')
            return redirect('produto')
    else:
        form = ProdutoForm()
    
    return render(request, 'produto/formulario.html', {'form': form})

@login_required
def editar_produto(request, id):
    produto = get_object_or_404(Produto, pk=id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('produto')
    else:
        form = ProdutoForm(instance=produto)
        
    return render(request, 'produto/formulario.html', {'form': form})

@login_required
def remover_produto(request, id):
    produto = get_object_or_404(Produto, pk=id)
    produto.delete()
    messages.success(request, 'Produto removido com sucesso!')
    return redirect('produto')

@login_required    
def detalhes_produto(request, id):
    produto = get_object_or_404(Produto, pk=id)
    return render(request, 'produto/detalhes.html', {'produto': produto})

@login_required
def ajustar_estoque(request, id):
    produto = produto = Produto.objects.get(pk=id)
    estoque = produto.estoque # pega o objeto estoque relacionado ao produto
    if request.method == 'POST':
        form = EstoqueForm(request.POST, instance=estoque)
        if form.is_valid():
            estoque = form.save()
            lista = []
            lista.append(estoque.produto) 
            return render(request, 'produto/lista.html', {'lista': lista})
    else:
         form = EstoqueForm(instance=estoque)
    return render(request, 'produto/estoque.html', {'form': form,})

@login_required
def teste1(request):
     return render(request, 'testes/teste1.html')

@login_required
def teste2(request):
     return render(request, 'testes/teste2.html')

@login_required 
def buscar_dados(request, app_modelo):
    termo = request.GET.get('q', '') 
    
    try:
        app, modelo = app_modelo.split('.')
        modelo = apps.get_model(app, modelo)
    except (LookupError, ValueError):
        return JsonResponse({'error': 'Modelo não encontrado'}, status=404)
    
    if not hasattr(modelo, 'nome'):
        return JsonResponse({'error': 'Modelo deve ter o campo "nome"'}, status=400)
    
    resultados = modelo.objects.filter(nome__icontains=termo)
    
    # CORREÇÃO AQUI:
    # 1. Usamos 'label' e 'value' (padrão jQuery UI)
    # 2. Retornamos a lista direta 'dados', sem envolver em {'results': ...}
    dados = [
        {'id': obj.id, 'label': obj.nome, 'value': obj.nome} 
        for obj in resultados
    ]
    
    return JsonResponse(dados, safe=False)

@login_required
def pedido(request):
    lista = Pedido.objects.all().order_by('-id')  # Obtém todos os registros
    return render(request, 'pedido/lista.html', {'lista': lista})


@login_required
def novo_pedido(request,id):
    if request.method == 'GET':
        try:
            cliente = Cliente.objects.get(pk=id)
        except Cliente.DoesNotExist:
            # Caso o registro não seja encontrado, exibe a mensagem de erro
            messages.error(request, 'Registro não encontrado')
            return redirect('cliente')  # Redireciona para a listagem
        # cria um novo pedido com o cliente selecionado
        pedido = Pedido(cliente=cliente)
        form = PedidoForm(instance=pedido)# cria um formulario com o novo pedido
        return render(request, 'pedido/form.html',{'form': form,})
    else: # se for metodo post, salva o pedido.
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save()
            return redirect('pedido')

# home/views.py

@login_required
def detalhes_pedido(request, id):
    try:
        pedido = Pedido.objects.get(pk=id)
    except Pedido.DoesNotExist:
        messages.error(request, 'Registro não encontrado')
        return redirect('pedido')
    
    if request.method == 'POST':
        form = ItemPedidoForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.pedido = pedido
            item.preco = item.produto.preco
            
            # --- LÓGICA DE ESTOQUE (NOVO) ---
            # Acessa o estoque do produto selecionado
            estoque_atual = item.produto.estoque 
            
            # 1. Verifica se tem saldo suficiente
            if estoque_atual.qtde < item.qtde:
                messages.error(request, f'Estoque insuficiente! Apenas {estoque_atual.qtde} unidades disponíveis.')
                # Retorna para a mesma tela sem salvar nada
                return redirect('detalhes_pedido', id=id)
            
            # 2. Se passou, desconta do estoque
            estoque_atual.qtde -= item.qtde
            estoque_atual.save() # Salva a nova quantidade no estoque
            
            # 3. Salva o item no pedido
            item.save()
            
            pedido.atualizar_status()
            messages.success(request, 'Produto adicionado com sucesso!')
            return redirect('detalhes_pedido', id=id)
            # --------------------------------
            
    else:
        form = ItemPedidoForm()
    
    contexto = {
        'pedido': pedido,
        'form': form,
    }
    return render(request, 'pedido/detalhes.html', contexto)

@login_required
def remover_pedido(request, id):
    pedido = get_object_or_404(Pedido, pk=id)
    pedido.delete()
    messages.success(request, 'pedido removido com sucesso!')
    return redirect('pedido')

@login_required
def remover_item_pedido(request, id):
    try:
        item = ItemPedido.objects.get(pk=id)
        pedido_id = item.pedido.id
        
        # --- LÓGICA DE DEVOLUÇÃO AO ESTOQUE (NOVO) ---
        estoque_atual = item.produto.estoque
        estoque_atual.qtde += item.qtde # Devolve a quantidade
        estoque_atual.save()
        # ---------------------------------------------
        
        item.delete()
        item.pedido.atualizar_status()
        messages.success(request, 'Item removido e estoque atualizado!')
        return redirect('detalhes_pedido', id=pedido_id)
        
    except ItemPedido.DoesNotExist:
        messages.error(request, 'Item não encontrado')
        return redirect('pedido')

@login_required
def form_pagamento(request, id):
    pedido = get_object_or_404(Pedido, pk=id)
    
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            form.save()
            pedido.atualizar_status()
            messages.success(request, 'Pagamento registrado com sucesso')
            return redirect('form_pagamento', id=pedido.id)
    else:
        # Inicializa o formulário JÁ com o pedido vinculado
        form = PagamentoForm(initial={'pedido': pedido})
        
    contexto = { 'pedido': pedido, 'form': form }
    return render(request, 'pedido/pagamento.html', contexto)

@login_required
def editar_pagamento(request, id):
    # Busca o pagamento ou retorna erro 404
    pagamento = get_object_or_404(Pagamento, pk=id)
    pedido = pagamento.pedido # Guarda o pedido para poder voltar pra ele depois

    if request.method == 'POST':
        form = PagamentoForm(request.POST, instance=pagamento)
        if form.is_valid():
            form.save()
            pedido.atualizar_status()
            messages.success(request, 'Pagamento atualizado com sucesso!')
            # Redireciona para a tela de pagamentos do PEDIDO (usando o ID do pedido)
            return redirect('form_pagamento', id=pedido.id) 
    else:
        form = PagamentoForm(instance=pagamento)
    
    contexto = {
        'pedido': pedido,
        'form': form,
    }
    # Reutilizamos o mesmo template de pagamento
    return render(request, 'pedido/pagamento.html', contexto)

@login_required
def remover_pagamento(request, id):
    # Busca o pagamento
    pagamento = get_object_or_404(Pagamento, pk=id)
    pedido_id = pagamento.pedido.id # Guarda o ID do pedido antes de apagar
    
    # Apaga
    pagamento.delete()
    pedido.atualizar_status()
    messages.success(request, 'Pagamento removido com sucesso!')
    
    # Volta para a lista de pagamentos deste pedido
    return redirect('form_pagamento', id=pedido_id)

@login_required
def nota_fiscal(request, id):
    try:
        pedido = Pedido.objects.get(pk=id)
    except Pedido.DoesNotExist:
        # Caso o registro não seja encontrado, exibe a mensagem de erro
        messages.error(request, 'Registro não encontrado')
        return redirect('pedido')  # Redireciona para a listagem    
    return render(request, 'pedido/nota_fiscal.html', {'pedido': pedido})

@login_required
def cancelar_pedido(request, id):
    pedido = get_object_or_404(Pedido, pk=id)
    
    # --- RESTRIÇÃO 1: Evitar cancelamento repetido ---
    if pedido.status == Pedido.CANCELADO:
        messages.warning(request, 'Este pedido já está cancelado.')
        return redirect('detalhes_pedido', id=id)

    # --- RESTRIÇÃO 2: Não cancelar pedidos já concluídos ---
    if pedido.status == Pedido.CONCLUIDO:
        messages.error(request, 'Não é possível cancelar um pedido que já foi Concluído.')
        return redirect('detalhes_pedido', id=id)

    # --- RESTRIÇÃO 3: Bloquear se houver pagamento (Segurança Financeira) ---
    if pedido.total_pago > 0:
        messages.error(request, f'O pedido tem pagamentos registrados (R$ {pedido.total_pago}). Remova os pagamentos antes de cancelar.')
        return redirect('detalhes_pedido', id=id)

    # Se passou por todas as regras, executa o cancelamento:
    
    # 1. Devolve o estoque
    for item in pedido.itempedido_set.all():
        estoque = item.produto.estoque
        estoque.qtde += item.qtde
        estoque.save()
    
    # 2. Atualiza o status
    pedido.status = Pedido.CANCELADO
    pedido.save()
    
    messages.success(request, 'Pedido cancelado com sucesso e produtos devolvidos ao estoque!')
    return redirect('detalhes_pedido', id=id)







