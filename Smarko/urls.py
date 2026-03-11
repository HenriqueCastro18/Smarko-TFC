from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from Smarko_App import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Rotas de Autenticação Principal ---
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verificar-2fa/', views.verificar_2fa_view, name='verificar_2fa'),

    # --- Fluxo de Recuperação de Senha (Requisito 2 do TFC) ---
    
    # 1. Formulário para inserir o e-mail
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(template_name="Smarko_App/password_reset.html"), 
         name="reset_password"),
    
    # 2. Confirmação de envio do link (Mensagem de sucesso no envio)
    path('reset_password_sent/', 
         auth_views.PasswordResetDoneView.as_view(template_name="Smarko_App/password_reset_sent.html"), 
         name="password_reset_done"),
    
    # 3. O Link Mágico com Token (uidb64 = ID do usuário, token = chave temporária)
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="Smarko_App/password_reset_confirm.html"), 
         name="password_reset_confirm"),
    
    # 4. Tela de finalização (Senha alterada com sucesso)
    path('reset_password_complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="Smarko_App/password_reset_done.html"), 
         name="password_reset_complete"),
]