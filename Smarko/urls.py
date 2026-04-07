from django.contrib import admin
from django.urls import path
from Smarko_App import views

urlpatterns = [
    path('admin/', admin.site.urls), #
    
    # Rotas Principais
    path('', views.home_view, name='home'), #
    path('register/', views.register_view, name='register'), #
    path('login/', views.login_view, name='login'), #
    path('logout/', views.logout_view, name='logout'), #
    path('verificar-2fa/', views.verificar_2fa_view, name='verificar_2fa'), #

    # Rotas de Recuperação de Senha (Fluxo Customizado)
    path('reset_password/', views.reset_password_view, name="reset_password"), #
    path('reset_password_sent/', views.reset_password_sent_view, name="password_reset_done"), #
    
    # Esta é a rota que liga o link do e-mail ao teu novo template personalizado
    path('reset_confirm/', views.password_reset_confirm_view, name='password_reset_confirm'), #

    # Rota do Ping para manter a sessão viva (Heartbeat)
    path('ping/', views.ping_view, name='ping'), #
]