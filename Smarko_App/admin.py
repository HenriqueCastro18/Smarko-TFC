from django.contrib import admin
from .models import PerfilUsuario, LogSeguranca

@admin.register(LogSeguranca)
class LogSegurancaAdmin(admin.ModelAdmin):
    # Colunas que aparecem na lista de logs
    list_display = ('data_hora', 'usuario', 'evento', 'ip')
    # Filtro lateral para facilitar a correção do professor
    list_filter = ('evento', 'data_hora')
    # Ordem decrescente (mais recentes primeiro)
    ordering = ('-data_hora',)
    
    # Bloqueia edição (auditoria não pode ser alterada manualmente)
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tentativas_falhas', 'bloqueado_ate')