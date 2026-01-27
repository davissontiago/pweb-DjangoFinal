from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    
    # Categoria
    path('categoria', views.categoria, name="categoria"),
    path('form_categoria', views.form_categoria, name="form_categoria"),
    path('categoria/editar/<int:id>', views.editar_categoria, name="editar_categoria"),
    path('categoria/detalhes/<int:id>', views.detalhes_categoria, name="detalhes_categoria"),
    path('categoria/remover/<int:id>', views.remover_categoria, name="remover_categoria"),

    # Cliente   
    path('cliente/', views.cliente, name='cliente'),
    path('cliente/form_cliente/', views.form_cliente, name='form_cliente'),
    path('cliente/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('cliente/remover/<int:id>/', views.remover_cliente, name='remover_cliente'),

    # Produto 
    path('produto/', views.produto, name='produto'),
    path('produto/form_produto/', views.form_produto, name='form_produto'),
    path('produto/editar/<int:id>/', views.editar_produto, name='editar_produto'),
    path('produto/remover/<int:id>/', views.remover_produto, name='remover_produto'),
    path('produto/detalhes/<int:id>/', views.detalhes_produto, name='detalhes_produto'),
    path('produto/ajustar_estoque/<int:id>/',  views.ajustar_estoque, name='ajustar_estoque'),
    
    path('teste1/', views.teste1, name='teste1'),
    path('teste2/', views.teste2, name='teste2'),
    
    path('buscar_dados/<str:app_modelo>/',views.buscar_dados, name='buscar_dados'),
    
    path('pedido/', views.pedido, name='pedido'),
    path('pedido/form/<int:id>', views.novo_pedido, name='novo_pedido'),
    path('pedido/detalhes/<int:id>/', views.detalhes_pedido, name='detalhes_pedido'),
    path('pedido/remover/<int:id>/', views.remover_pedido, name='remover_pedido'),
    path('pedido/remover_item/<int:id>', views.remover_item_pedido, name='remover_item_pedido'),

]