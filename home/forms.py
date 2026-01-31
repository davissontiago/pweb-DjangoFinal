from django import forms
from datetime import date
from django.contrib import messages
from .models import *


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'ordem']
        widgets = {
            'nome':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
            'ordem':forms.NumberInput(attrs={'class': 'inteiro form-control', 'placeholder': ''}),
        }
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if len(nome) < 3:
            raise forms.ValidationError("O nome deve ter pelo menos 3 caracteres.")
        return nome  
    
    def clean_ordem(self):
        ordem = self.cleaned_data.get('ordem')
        if ordem <= 0:
            raise forms.ValidationError("O campo ordem deve ser maior que zero.")
        return ordem
    
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'cpf', 'datanasc']
        widgets = {
            'nome':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
            'cpf':forms.TextInput(attrs={'class': 'cpf form-control', 'placeholder': 'C.P.F'}),
            'datanasc': forms.DateInput(attrs={'class': 'data form-control', 'placeholder': 'Data de Nascimento'}, format='%d/%m/%Y'),
        }

    def clean_datanasc(self):
        data = self.cleaned_data.get('datanasc')
        if data and data > date.today():
            raise forms.ValidationError("A data de nascimento não pode ser maior que a data atual.")
        return data

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'preco', 'categoria', 'img_base64']
        widgets = {
            'categoria': forms.HiddenInput(),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
            'img_base64': forms.HiddenInput(), 
            'preco': forms.TextInput(attrs={
                'class': 'money form-control', 
                'maxlength': 500,
                'placeholder': '0.000,00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ProdutoForm, self).__init__(*args, **kwargs)
        self.fields['preco'].localize = True
        self.fields['preco'].widget.is_localized = True
        
class EstoqueForm(forms.ModelForm):
    class Meta:
        model = Estoque
        fields = ['produto','qtde']
        
        widgets = {
            'produto': forms.HiddenInput(),  # Campo oculto para armazenar o ID do produto
            'qtde':forms.TextInput(attrs={'class': 'inteiro form-control',}),
    }
        
class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente']
        widgets = {
            'cliente': forms.HiddenInput(),  # Campo oculto para armazenar o ID
        }

class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'qtde']


        widgets = {
            'produto': forms.HiddenInput(),  # Campo oculto para armazenar o ID
            'qtde':forms.TextInput(attrs={'class': 'form-control',}),
        }
        
# home/forms.py

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['pedido', 'forma', 'valor']
        widgets = {
            'pedido': forms.HiddenInput(), # O pedido fica oculto para o usuário não mudar
            'forma': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.TextInput(attrs={
                'class': 'money form-control',
                'maxlength': 500,
                'placeholder': '0.000,00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(PagamentoForm, self).__init__(*args, **kwargs)
        self.fields['valor'].localize = True
        self.fields['valor'].widget.is_localized = True

    def clean(self):
        cleaned_data = super().clean()
        valor = cleaned_data.get('valor')
        pedido = cleaned_data.get('pedido')

        if valor and pedido:
            # Lógica para definir o limite:
            # 1. Pega o débito atual do pedido (Total - Pago)
            limite = pedido.debito
            
            # 2. Se for EDIÇÃO (já tem ID), precisamos "devolver" o valor antigo 
            # para o limite antes de comparar. 
            # Ex: Débito R$ 0. Edito pagamento de R$ 50 para R$ 60. 
            # Limite real é 0 + 50 = 50. Novo valor 60 > 50 -> Erro.
            if self.instance.pk:
                limite += self.instance.valor

            if valor > limite:
                # Formata o número para exibir na mensagem de erro
                from django.utils.numberformat import format
                limite_fmt = format(limite, decimal_sep=',', grouping=3, thousand_sep='.')
                
                self.add_error('valor', f'O valor não pode ser maior que o débito restante (R$ {limite_fmt}).')

        return cleaned_data 
