import random
import time
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail # Import para envio de e-mail
from .models import PerfilUsuario, LogSeguranca

def get_client_ip(request):
    """Captura o IP real do utilizador para auditoria."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def register_view(request):
    """Criação de conta (Requisito 1.1 - Bcrypt)."""
    if request.method == "POST":
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmacao = request.POST.get('confirmacao')

        if senha != confirmacao:
            messages.error(request, "As senhas não coincidem.")
            return render(request, 'Smarko_App/register.html')

        if User.objects.filter(username=usuario).exists():
            messages.error(request, "Utilizador já cadastrado.")
            return render(request, 'Smarko_App/register.html')

        # Criação do usuário com e-mail
        user = User.objects.create_user(username=usuario, email=email, password=senha)
        PerfilUsuario.objects.create(user=user)
        
        LogSeguranca.objects.create(
            usuario=user, 
            evento="Criação de Conta", 
            ip=get_client_ip(request)
        )
        
        messages.success(request, "Conta criada com sucesso!")
        return redirect('login')
    return render(request, 'Smarko_App/register.html')

def login_view(request):
    """Login com Bloqueio (1.11), Auditoria (4.5) e Envio de 2FA por E-mail."""
    if request.method == "POST":
        usuario = request.POST.get('username')
        senha_digitada = request.POST.get('password')
        ip_atual = get_client_ip(request)

        try:
            user = User.objects.get(username=usuario)
            perfil, created = PerfilUsuario.objects.get_or_create(user=user)
        except User.DoesNotExist:
            LogSeguranca.objects.create(usuario=None, evento=f"Tentativa: Usuário Inexistente ({usuario})", ip=ip_atual)
            messages.error(request, "Utilizador ou senha incorretos.")
            return render(request, 'Smarko_App/login.html')

        if perfil.bloqueado_ate and timezone.now() < perfil.bloqueado_ate:
            restante = int((perfil.bloqueado_ate - timezone.now()).total_seconds() // 60) + 1
            messages.error(request, f"Conta bloqueada. Tente em {restante} min.")
            return render(request, 'Smarko_App/login.html')

        user_auth = authenticate(request, username=usuario, password=senha_digitada)

        if user_auth is not None:
            perfil.tentativas_falhas = 0
            perfil.bloqueado_ate = None
            perfil.save()
            
            # Setup 2FA (Requisito 1.5)
            codigo = str(random.randint(100000, 999999))
            request.session['codigo_2fa'] = codigo
            request.session['user_id_pre_auth'] = user_auth.id
            request.session['codigo_2fa_timestamp'] = time.time()
            
            # 1. Mantém o código no console (CMD) para facilitar o teste
            print(f"\n[SISTEMA] CÓDIGO 2FA PARA {usuario}: {codigo}\n")
            
            # 2. Envio de E-mail Real
            if user_auth.email:
                assunto = f"{codigo} é o seu código de acesso Smarko"
                
                # Versão em texto simples (para caso o e-mail do professor não suporte HTML)
                corpo_texto = f"Olá {usuario}, seu código de verificação é: {codigo}"
                
                # Versão em HTML (Layout Bonitão)
                corpo_html = f"""
                <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
                    <div style="background-color: #1a182e; padding: 20px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Smarko Security</h1>
                    </div>
                    <div style="padding: 30px; background-color: #ffffff;">
                        <p style="font-size: 16px; color: #333;">Olá <strong>{usuario}</strong>,</p>
                        <p style="font-size: 16px; color: #333;">Para concluir seu acesso, utilize o código de verificação abaixo:</p>
                        <div style="background-color: #f4f4f9; padding: 20px; text-align: center; border-radius: 6px; margin: 25px 0;">
                            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #1a182e;">{codigo}</span>
                        </div>
                        <p style="font-size: 14px; color: #666; text-align: center;">Este código expira em <strong>2 minutos</strong>.</p>
                        <hr style="border: 0; border-top: 1px solid #eeeeee; margin: 30px 0;">
                        <p style="font-size: 12px; color: #999; text-align: center;">Se você não solicitou este código, por favor ignore este e-mail.</p>
                    </div>
                    <div style="background-color: #f9f9f9; padding: 15px; text-align: center; font-size: 12px; color: #aaa;">
                        &copy; 2026 Smarko Project - Mogi das Cruzes, SP
                    </div>
                </div>
                """
                
                try:
                    send_mail(
                        assunto,
                        corpo_texto,
                        None,
                        [user_auth.email],
                        fail_silently=False,
                        html_message=corpo_html, # Aqui é onde a mágica acontece
                    )
                except Exception as e:
                    LogSeguranca.objects.create(usuario=user_auth, evento=f"Falha SMTP: {str(e)[:100]}", ip=ip_atual)
            
            return redirect('verificar_2fa')
        else:
            perfil.tentativas_falhas += 1
            LogSeguranca.objects.create(usuario=user, evento=f"Falha de Login (Tentativa {perfil.tentativas_falhas})", ip=ip_atual)
            
            if perfil.tentativas_falhas >= 3:
                perfil.bloqueado_ate = timezone.now() + timedelta(minutes=5)
                messages.error(request, "Muitas tentativas. Bloqueado por 5 min.")
            else:
                messages.error(request, f"Senha incorreta! Tentativa {perfil.tentativas_falhas} de 3.")
            perfil.save()

    return render(request, 'Smarko_App/login.html')

def verificar_2fa_view(request):
    """Validação 2FA com Auditoria (Requisito 1.6)."""
    codigo_real = request.session.get('codigo_2fa')
    user_id = request.session.get('user_id_pre_auth')
    timestamp = request.session.get('codigo_2fa_timestamp', 0)

    if not codigo_real or not user_id: return redirect('login')

    if request.method == "POST":
        # Validação de tempo (120 segundos = 2 minutos)
        if time.time() - timestamp > 120:
            messages.error(request, "Código expirado.")
            return redirect('login')

        if request.POST.get('codigo') == codigo_real:
            user = User.objects.get(id=user_id)
            auth_login(request, user)
            LogSeguranca.objects.create(usuario=user, evento="Login Completo (2FA Sucesso)", ip=get_client_ip(request))
            request.session.pop('codigo_2fa', None)
            return redirect('home')
        else:
            LogSeguranca.objects.create(usuario=User.objects.get(id=user_id), evento="Falha no Código 2FA", ip=get_client_ip(request))
            messages.error(request, "Código incorreto.")

    return render(request, 'Smarko_App/verificar_2fa.html')

def home_view(request):
    if not request.user.is_authenticated: return redirect('login')
    return render(request, 'Smarko_App/index.html')

def logout_view(request):
    if request.user.is_authenticated:
        LogSeguranca.objects.create(usuario=request.user, evento="Logout Efetuado", ip=get_client_ip(request))
    logout(request)
    return redirect('login')