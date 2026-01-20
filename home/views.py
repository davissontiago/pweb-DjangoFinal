from django.shortcuts import render, redirect, get_object_or_404
from django.apps import apps 
from django.http import JsonResponse
from .models import *
from .forms import *

def index(request):
    return render(request,'index.html')

def categoria(request):
    contexto = {
        'lista': Categoria.objects.all().order_by('-id'),
    }
    return render(request, 'categoria/lista.html',contexto)

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

def cliente(request):
    contexto = {
        'lista': Cliente.objects.all().order_by('-id'),
    }
    return render(request, 'cliente/lista.html', context=contexto)

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

def remover_cliente(request, id):
    cliente = get_object_or_404(Cliente, pk=id)
    cliente.delete()
    messages.success(request, 'Cliente removido com sucesso!')
    return redirect('cliente')


# ==============================================================================
# PRODUTO (CRUD Completo)
# ==============================================================================

def produto(request):
    contexto = {
        'lista': Produto.objects.all().order_by('-id'),
    }
    return render(request, 'produto/lista.html', context=contexto)

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

def remover_produto(request, id):
    produto = get_object_or_404(Produto, pk=id)
    produto.delete()
    messages.success(request, 'Produto removido com sucesso!')
    return redirect('produto')
    
def detalhes_produto(request, id):
    produto = get_object_or_404(Produto, pk=id)
    return render(request, 'produto/detalhes.html', {'produto': produto})

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

def teste1(request):
     return render(request, 'testes/teste1.html')

def teste2(request):
     return render(request, 'testes/teste2.html')
 
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

def pedido(request):
    lista = Pedido.objects.all().order_by('-id')  # Obtém todos os registros
    return render(request, 'pedido/lista.html', {'lista': lista})


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

def detalhes_pedido(request, id):
    try:
        pedido = Pedido.objects.get(pk=id)
    except Pedido.DoesNotExist:
        # Caso o registro não seja encontrado, exibe a mensagem de erro
        messages.error(request, 'Registro não encontrado')
        return redirect('pedido')  # Redireciona para a listagem    
    
    if request.method == 'GET':
        itemPedido = ItemPedido(pedido=pedido)
        form = ItemPedidoForm(instance=itemPedido)
    else:
        form = ItemPedidoForm(request.POST)
        # aguardando implementação POST, salvar item
    
    contexto = {
        'pedido': pedido,
        'form': form,
    }
    return render(request, 'pedido/detalhes.html',contexto )

def remover_pedido(request, id):
    pedido = get_object_or_404(Pedido, pk=id)
    pedido.delete()
    messages.success(request, 'pedido removido com sucesso!')
    return redirect('pedido')
    





