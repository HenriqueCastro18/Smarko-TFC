from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from Smarko_App import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas Principais
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verificar-2fa/', views.verificar_2fa_view, name='verificar_2fa'),

    # 1. Esqueci a Senha - Formulário para digitar o e-mail
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(
             template_name="Smarko_App/password_reset.html",
             subject_template_name="Smarko_App/password_reset_subject.txt",
             email_template_name="Smarko_App/password_reset_email.html", 
             html_email_template_name="Smarko_App/password_reset_email.html" # HTML para layout com botão
         ), 
         name="reset_password"),

    # 2. E-mail Enviado - Tela de confirmação (Check azul)
    path('reset_password_sent/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name="Smarko_App/password_reset_sent.html"
         ), 
         name="password_reset_done"),
    
    # 3. Link do E-mail - Onde o usuário define a "Nova Senha" ou vê o "Link Expirado"
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name="Smarko_App/password_reset_confirm.html"
         ), 
         name="password_reset_confirm"),
    
    # 4. Senha Alterada - Tela final de sucesso
    path('reset_password_complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name="Smarko_App/password_reset_done.html"
         ), 
         name="password_reset_complete"),
]