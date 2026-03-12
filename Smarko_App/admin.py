from django.contrib import admin
from .models import PerfilUsuario, LogSeguranca

@admin.register(LogSeguranca)
class LogSegurancaAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario', 'evento', 'ip')
    list_filter = ('evento', 'data_hora')
    ordering = ('-data_hora',)
    
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tentativas_falhas', 'bloqueado_ate')