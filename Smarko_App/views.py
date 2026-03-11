from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def register_view(request):
    if request.method == "POST":
        # Capturando os nomes que estão no atributo 'name' do HTML
        usuario = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('password')
        
        # Criando o registro no banco
        novo_usuario = User(username=usuario, email=email)
        novo_usuario.set_password(senha) # AQUI o bcrypt acontece
        novo_usuario.save() # AQUI ele entra no banco
        
        return redirect('login') # Redireciona para onde você quiser
        
    return render(request, 'Smarko_App/register.html')