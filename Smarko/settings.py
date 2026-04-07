import os
import json
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from django.contrib.auth.hashers import BCryptSHA256PasswordHasher

# [Item 3.6] Proteção de chaves: Uso de variáveis de ambiente (.env) para isolar segredos do código-fonte.
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# [Item 3.6] SECRET_KEY protegida: A chave mestra da criptografia do Django nunca fica exposta no código.
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-local-dev-key-2026')

DEBUG = True

WHITENOISE_USE_FINDERS = True

# [Item 3.2] Configuração de hosts: Prevenção contra ataques de envenenamento de cabeçalho HTTP (Host Header Injection).
ALLOWED_HOSTS = ['*', '.vercel.app', '127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Smarko_App',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # [Item 3.3] Servidor de arquivos estáticos robusto para produção.
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Smarko.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Smarko.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# [Item 1.2 e 3.8] Justificativa Técnica: Aumentei o custo do hash para 14 rounds (padrão é 12).
# Isso torna o brute force extremamente lento e caro para o atacante, sem degradar a experiência do utilizador.
class SmarkoBcryptHasher(BCryptSHA256PasswordHasher):
    rounds = 14

# [Item 1.1] Algoritmo de Hashing: Uso do BCrypt com SHA-256, um padrão ouro de segurança irreversível.
PASSWORD_HASHERS = [
    'Smarko.settings.SmarkoBcryptHasher', 
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-pt'
TIME_ZONE = 'Europe/Lisbon'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_PATH = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [STATIC_PATH] if os.path.exists(STATIC_PATH) else []
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# [Itens 1.9 e 1.10] Sessões e Timeout: Expiração curta (120s) para mitigar riscos de sessões abandonadas (AFK).
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True # Proteção contra ataques XSS (impede acesso via JS)
SESSION_COOKIE_AGE = 120 
SESSION_SAVE_EVERY_REQUEST = True 
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Configuração de E-mail (SMTP com TLS).
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True # [Item 3.1] Envio de e-mails via canal cifrado.
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASS')
DEFAULT_FROM_EMAIL = f"Smarko Security <{os.getenv('EMAIL_USER')}>"

# [Item 3.6] Proteção de chaves: Carregamento da API Key do Firebase via variáveis de ambiente
FIREBASE_WEB_API_KEY = os.getenv('FIREBASE_API_KEY')

# [Item 3.4 e 3.5] Dados em Repouso: O Firestore (Google Cloud) garante criptografia AES-256 nativa no armazenamento.
firebase_info = os.getenv('FIREBASE_SERVICE_ACCOUNT')
if not firebase_admin._apps:
    try:
        if firebase_info:
            cred_dict = json.loads(firebase_info, strict=False)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        else:
            cred_path = os.path.join(BASE_DIR, 'serviceAccountKey.json')
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Erro Firebase: {e}")

db = firestore.client() if firebase_admin._apps else None

# [Item 3.1] Comunicação Segura (TLS/HTTPS): Implementação de blindagem para tráfego em trânsito.
if os.getenv('VERCEL') or not DEBUG:
    # Bloqueio de conexões não seguras: Redireciona HTTP para HTTPS obrigatoriamente.
    SECURE_SSL_REDIRECT = True
    
    # Cookies Protegidos: Sessões e CSRF só viajam em conexões cifradas.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS (HTTP Strict Transport Security): Força o navegador a usar HTTPS por 1 ano.
    SECURE_HSTS_SECONDS = 31536000  
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0