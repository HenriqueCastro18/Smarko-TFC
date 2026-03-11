@echo off
setlocal
echo ======================================================
echo   SMARKO - Instalador do Sistema de Seguranca
echo ======================================================

:: 1. Verifica se o Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Python nao encontrado no sistema.
    echo Redirecionando para o download da versao 3.12...
    start https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
    echo.
    echo Por favor:
    echo 1. Execute o instalador que foi baixado.
    echo 2. MARQUE A OPCAO "Add Python to PATH".
    echo 3. Apos instalar, feche esta janela e rode o instalar.bat novamente.
    pause
    exit /b
)

:: 2. Verifica se a versao e pelo menos 3.10
for /f "tokens=2 delims= " %%v in ('python --version') do set ver=%%v
for /f "tokens=1,2 delims=." %%a in ("%ver%") do (
    set major=%%a
    set minor=%%b
)

if %minor% LSS 10 (
    if %major% EQU 3 (
        echo [AVISO] Sua versao do Python (%ver%) esta desatualizada.
        echo Recomendamos a versao 3.10 ou superior para o Django 6.0.
        echo Abrindo o site oficial...
        start https://www.python.org/downloads/
        pause
    )
)

echo [OK] Python detectado: %ver%

:: 3. Criando o ambiente e instalando dependencias
echo [1/4] Criando ambiente virtual (venv)...
python -m venv venv

echo [2/4] Instalando dependencias do requirements.txt...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [3/4] Aplicando Migracoes (Banco de Dados e Logs)...
python manage.py makemigrations
python manage.py migrate

echo [4/4] Verificando integridade do sistema...
python -c "import bcrypt; print('Sucesso: Bcrypt e Django estao prontos!')"

echo ======================================================
echo   Instalacao Concluida! 
echo   Para rodar: python manage.py runserver
echo ======================================================
pause