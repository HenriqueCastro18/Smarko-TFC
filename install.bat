@echo off
echo ======================================================
echo           Smarko Security - Instalador
echo ======================================================

:: 1. Verifica se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Estou abrindo o site oficial para voce baixar o Python.
    echo Marque a opcao "ADD PYTHON TO PATH" durante a instalacao!
    echo.
    timeout /t 5
    start https://www.python.org/downloads/
    pause
    exit
)

:: 2. Cria o ambiente virtual (venv) se não existir 
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv 
) else (
    echo Ambiente virtual ja existe.
)

:: 3. Ativa o ambiente virtual 
echo Ativando venv...
call venv\Scripts\activate 

:: 4. Atualiza o pip
echo Atualizando o pip...
python -m pip install --upgrade pip 

:: 5. Instala as bibliotecas do requirements.txt 
if exist requirements.txt (
    echo Instalando dependencias...
    pip install -r requirements.txt 
) else (
    echo [ERRO] Arquivo requirements.txt nao encontrado! [cite: 2]
    pause
    exit
)

:: 6. Realiza as migrações do banco de dados (Cria o db.sqlite3)
echo Aplicando migracoes...
python manage.py migrate 

echo ======================================================
echo   Instalacao concluida! Use 'run.bat' para iniciar. [cite: 3]
echo ======================================================
pause
