from django.contrib import admin
from django.urls import path
from Smarko_App import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registrar/', views.register_view, name='register'),
    # path('login/', views.login_view, name='login'), <-- Crie esta depois
]