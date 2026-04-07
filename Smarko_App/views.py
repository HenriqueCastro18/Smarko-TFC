import random
import time
import requests
import urllib.parse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from functools import wraps
from firebase_admin import firestore, auth as firebase_auth
from django.contrib.auth.hashers import make_password

# [Itens 3.4 e 3.5] Conexão Firestore segura para armazenamento de perfis e logs.
db = firestore.client()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def registrar_log_firebase(uid, username, evento, ip):
    try:
        db.collection('logs_seguranca').add({
            'usuario_id': uid,
            'usuario_nome': username,
            'evento': evento,
            'ip': ip,
            'data_hora': firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        print(f"Erro ao salvar log no Firebase: {e}")

def firebase_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('uid'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def register_view(request):
    if request.method == "POST":
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmacao = request.POST.get('confirmacao')

        if not usuario or not senha or not email:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return render(request, 'Smarko_App/register.html')

        if senha != confirmacao:
            messages.error(request, "As senhas não coincidem.")
            return render(request, 'Smarko_App/register.html')

        try:
            user_record = firebase_auth.create_user(email=email, password=senha, display_name=usuario)
            # [Item 1.1] Utilizo make_password para gerar hash seguro.
            senha_hash = make_password(senha)

            db.collection('perfis').document(user_record.uid).set({
                'username': usuario,
                'email': email,
                'senha_hash': senha_hash,
                'tentativas_falhas': 0,
                'bloqueado_ate': None
            })

            registrar_log_firebase(user_record.uid, usuario, "Conta Criada", get_client_ip(request))
            messages.success(request, "Conta criada com sucesso!")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Erro ao registar: {str(e)}")
    
    return render(request, 'Smarko_App/register.html')

def login_view(request):
    if request.method == "POST":
        identificador = request.POST.get('username')
        senha_digitada = request.POST.get('password')
        
        email_login = None
        uid = None
        username_real = identificador

        if '@' in identificador:
            email_login = identificador
            try:
                user_record = firebase_auth.get_user_by_email(email_login)
                uid = user_record.uid
                username_real = user_record.display_name
            except: pass
        else:
            docs = db.collection('perfis').where('username', '==', identificador).limit(1).get()
            if docs:
                email_login = docs[0].to_dict().get('email')
                uid = docs[0].id

        if not email_login or not uid:
            messages.error(request, "Utilizador ou senha incorretos.")
            return render(request, 'Smarko_App/login.html')

        perfil_ref = db.collection('perfis').document(uid)
        p_data = perfil_ref.get().to_dict() or {}
        bloqueio = p_data.get('bloqueado_ate')

        if bloqueio and timezone.now() < bloqueio:
            minutos_restantes = int((bloqueio - timezone.now()).total_seconds() / 60) + 1
            messages.error(request, f"Conta bloqueada por excesso de tentativas. Tente novamente em {minutos_restantes} min.")
            return render(request, 'Smarko_App/login.html')

        api_key = getattr(settings, 'FIREBASE_WEB_API_KEY', '')
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        resp = requests.post(url, json={"email": email_login, "password": senha_digitada, "returnSecureToken": True})
        
        if resp.status_code == 200:
            perfil_ref.update({'tentativas_falhas': 0, 'bloqueado_ate': None})
            
            codigo = str(random.randint(100000, 999999))
            request.session['codigo_2fa'] = codigo
            request.session['user_id_pre_auth'] = uid
            request.session['user_name_pre_auth'] = username_real
            request.session['codigo_2fa_timestamp'] = time.time()

            unique_id = time.time()

            html_msg = f"""
            <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <div style="background: linear-gradient(135deg, #1a182e 0%, #252245 100%); padding: 25px; text-align: center;">
                    <h2 style="color: #ffffff; margin: 0; font-size: 22px; letter-spacing: 1px;">Smarko Security</h2>
                </div>
                <div style="padding: 40px 30px; background-color: #ffffff; text-align: center;">
                    <p style="font-size: 16px; color: #333333; margin-bottom: 10px;">Olá, <strong>{username_real}</strong></p>
                    <p style="font-size: 15px; color: #666666; margin-bottom: 30px;">Utilize o código de autorização abaixo para prosseguir:</p>
                    <div style="background-color: #f8f9fa; padding: 15px 30px; border-radius: 8px; display: inline-block; margin-bottom: 30px; border: 2px dashed #1a182e;">
                        <span style="letter-spacing: 8px; font-size: 34px; font-weight: bold; color: #1a182e;">{codigo}</span>
                    </div>
                    <p style="font-size: 13px; color: #dc3545; font-weight: bold;">⚠️ Este código expira em 2 minutos.</p>
                </div>
                <div style="display: none; visibility: hidden; opacity: 0; font-size: 1px;">{unique_id}</div>
            </div>
            """

            send_mail("Smarko Security - Código de Acesso 🔐", f"Código: {codigo}", settings.DEFAULT_FROM_EMAIL, [email_login], html_message=html_msg)
            return redirect('verificar_2fa')
        else:
            tentativas = p_data.get('tentativas_falhas', 0) + 1
            perfil_ref.update({'tentativas_falhas': tentativas})
            if tentativas >= 3:
                perfil_ref.update({'bloqueado_ate': timezone.now() + timedelta(minutes=5)})
                messages.error(request, "Múltiplas tentativas falhas. Conta bloqueada por 5 minutos.")
            else:
                messages.error(request, f"Senha incorreta. Tentativa {tentativas} de 3.")

    return render(request, 'Smarko_App/login.html')

def verificar_2fa_view(request):
    if request.method == "POST":
        if time.time() - request.session.get('codigo_2fa_timestamp', 0) > 120:
            messages.error(request, "O código expirou. Tente novamente.")
            return redirect('login')

        if request.POST.get('codigo') == request.session.get('codigo_2fa'):
            request.session['uid'] = request.session.get('user_id_pre_auth')
            request.session['username'] = request.session.get('user_name_pre_auth')
            registrar_log_firebase(request.session['uid'], request.session['username'], "Login Sucesso", get_client_ip(request))
            return redirect('home')
        
        messages.error(request, "Código inválido.")
    return render(request, 'Smarko_App/verificar_2fa.html')

def reset_password_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        ip = get_client_ip(request)
        try:
            action_settings = firebase_auth.ActionCodeSettings(
                url='https://smarkoo-copia.vercel.app/reset_confirm/',
                handle_code_in_app=False,
            )
            fb_link = firebase_auth.generate_password_reset_link(email, action_settings)
            
            parsed_url = urllib.parse.urlparse(fb_link)
            oob_code = urllib.parse.parse_qs(parsed_url.query).get('oobCode', [None])[0]

            if oob_code:
                # Agora gravamos apenas o email e o tempo. Não precisamos do 'ja_aberto'
                db.collection('tokens_recuperacao').document(oob_code).set({
                    'email': email, 'criado_em': time.time()
                })

                meu_link = f"https://smarkoo-copia.vercel.app/reset_confirm/?oobCode={oob_code}"
                unique_id = time.time()

                html_msg = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 15px; overflow: hidden;">
                    <div style="background: linear-gradient(135deg, #1a182e 0%, #252245 100%); padding: 30px; text-align: center;">
                        <h2 style="color: #ffffff; margin: 0;">Smarko Security</h2>
                    </div>
                    <div style="padding: 40px; text-align: center; background: #ffffff;">
                        <p style="color: #333; font-size: 16px;">Pedido de redefinição de senha recebido.</p>
                        <p style="color: #dc3545; font-weight: bold; margin-bottom: 30px;">⚠️ Válido por 10 minutos.</p>
                        <a href="{meu_link}" style="background: #1a182e; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Redefinir Senha</a>
                    </div>
                    <div style="display: none; visibility: hidden; opacity: 0; font-size: 1px;">{unique_id}</div>
                </div>
                """
                send_mail("Smarko - Redefinição de Senha", f"Link: {meu_link}", settings.DEFAULT_FROM_EMAIL, [email], html_message=html_msg)
                registrar_log_firebase("SISTEMA", email, "Reset Solicitado", ip)
                return redirect('password_reset_done')
        except Exception as e:
            print(f"Erro no Reset: {e}")
            return redirect('password_reset_done')
    return render(request, 'Smarko_App/password_reset.html')

def password_reset_confirm_view(request):
    oob_code = request.GET.get('oobCode') or request.POST.get('oobCode')
    ip = get_client_ip(request)

    if not oob_code:
        return render(request, 'Smarko_App/password_reset_confirm_fail.html')

    token_ref = db.collection('tokens_recuperacao').document(oob_code)
    token_doc = token_ref.get()

    if not token_doc.exists:
        registrar_log_firebase("SISTEMA", "Desconhecido", "Falha Reset - Token Inexistente", ip)
        return render(request, 'Smarko_App/password_reset_confirm_fail.html')

    token_data = token_doc.to_dict()
    tempo_passado = time.time() - token_data.get('criado_em', 0)

    # [Item 2.3] Verifica expiração (2 minutos)
    if tempo_passado > 180:
        token_ref.delete() # Se expirou, limpamos logo a base de dados
        registrar_log_firebase("SISTEMA", token_data.get('email'), "Falha Reset - Token Expirado", ip)
        return render(request, 'Smarko_App/password_reset_confirm_fail.html')

    api_key = getattr(settings, 'FIREBASE_WEB_API_KEY', '')

    if request.method == "GET":
        return render(request, 'Smarko_App/password_reset_confirm.html', {'oobCode': oob_code})

    if request.method == "POST":
        nova_senha = request.POST.get('nova_senha')
        confirmacao = request.POST.get('confirmacao')

        if nova_senha != confirmacao:
            messages.error(request, "As senhas não coincidem.")
            return render(request, 'Smarko_App/password_reset_confirm.html', {'oobCode': oob_code})

        try:
            reset_url = f"https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key={api_key}"
            resp = requests.post(reset_url, json={"oobCode": oob_code, "newPassword": nova_senha})
            
            if resp.status_code == 200:
                uid = resp.json().get('localId')
                # SINCRONIZAÇÃO: Atualiza hash no Firestore. [Item 1.1]
                if uid:
                    db.collection('perfis').document(uid).update({'senha_hash': make_password(nova_senha)})

                registrar_log_firebase(uid, token_data.get('email'), "Senha Redefinida", ip)
                
                # O TOKEN SÓ É ELIMINADO/QUEIMADO AQUI NO SUCESSO! [Item 2.4]
                token_ref.delete() 
                messages.success(request, "Senha atualizada com sucesso! Faça login.")
                return redirect('login')
            else:
                # Se falhar (ex: chave da Vercel em falta), mostra o erro real em vez de bloquear o token
                error_msg = resp.json().get('error', {}).get('message', 'Erro Desconhecido API')
                registrar_log_firebase("SISTEMA", token_data.get('email'), f"Falha Firebase API: {error_msg}", ip)
                messages.error(request, f"Erro do servidor Firebase: {error_msg}")
                return render(request, 'Smarko_App/password_reset_confirm.html', {'oobCode': oob_code})
        except Exception as e:
            messages.error(request, f"Erro interno do sistema: {str(e)}")
            return render(request, 'Smarko_App/password_reset_confirm.html', {'oobCode': oob_code})

def reset_password_sent_view(request):
    return render(request, 'Smarko_App/password_reset_sent.html')

@firebase_login_required
def home_view(request):
    return render(request, 'Smarko_App/index.html')

def logout_view(request):
    request.session.flush() # [Item 1.10] Invalidação completa
    return redirect('login')

def ping_view(request):
    # [Item 1.9] Esta função atualiza a sessão no Backend para não expirar (AFK timeout).
    if request.session.get('uid'):
        request.session.modified = True
    return JsonResponse({'status': 'vivo'})