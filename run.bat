@echo off
echo ======================================================
echo           Smarko Security - Iniciando Servidor
echo ======================================================

:: 1. Ativa o ambiente virtual
if exist venv (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate 
) else (
    echo [ERRO] Ambiente virtual nao encontrado! 
    echo Por favor, rode o 'install.bat' primeiro.
    pause
    exit
)

:: 2. Abre o navegador automaticamente
echo Abrindo o navegador em http://127.0.0.1:8000/
start http://127.0.0.1:8000/

:: 3. Inicia o servidor do Django
echo Iniciando o Django...
python manage.py runserver 

pause