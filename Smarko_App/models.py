from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, related_name='perfil', on_delete=models.CASCADE)
    tentativas_falhas = models.IntegerField(default=0)
    bloqueado_ate = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Perfil: {self.user.username}"

class LogSeguranca(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    evento = models.CharField(max_length=255)
    ip = models.GenericIPAddressField(null=True, blank=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.data_hora} - {self.evento} ({self.usuario})"