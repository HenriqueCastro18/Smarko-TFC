from django.db import models
from django.contrib.auth.models import User

# [Item 1.1] Modelo para estender o perfil do utilizador, se necessário localmente.
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Adicione campos locais se não quiser usar apenas o Firebase
    
    def __str__(self):
        return self.user.username

# [Item 2.6 e 2.7] Modelo para registo de logs de auditoria local (espelhamento do Firebase).
class LogSeguranca(models.Model):
    usuario_nome = models.CharField(max_length=255)
    evento = models.CharField(max_length=255)
    ip = models.GenericIPAddressField()
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario_nome} - {self.evento}"