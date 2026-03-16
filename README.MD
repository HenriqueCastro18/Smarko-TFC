# 🛡️ Smarko - Autenticação Defensiva

#📌 Sobre o Projeto
****O Smarko é um sistema de automação comercial focado no gerenciamento de mercados. O grande diferencial desta aplicação é a sua arquitetura robusta de segurança e autenticação, garantindo a integridade dos dados e o controle rigoroso de acesso dos usuários.**

> **Status do Projeto:** 🛠️ Em Desenvolvimento / TFC (Trabalho de Final de Curso)

---

## 🚀 Tech Stack

O projeto utiliza tecnologias de ponta para garantir performance e integridade dos dados:

* **Linguagem:** Python 3.14
* **Framework:** Django 6.0.3
* **Banco de Dados:** SQLite (Desenvolvimento)
* **Bibliotecas de Segurança:**
    * `bcrypt`: Hashing de alta resistência.
    * `python-dotenv`: Gestão de variáveis de ambiente.
    * `django-csp`: Content Security Policy contra XSS.

---

## 🔒 Camadas de Segurança Implementadas

### 1. Proteção de Credenciais
Utilizamos o algoritmo **BCrypt** com **12 rounds** de custo. Essa abordagem torna o processo de hashing computacionalmente caro, protegendo as senhas contra ataques de dicionário e *rainbow tables*.

### 2. Autenticação Multifator (MFA)
Implementação de **2FA (Two-Factor Authentication)** via código de verificação enviado por **E-mail**, garantindo uma camada extra de validação no login.

### 3. Gestão de Sessão e Mitigação de Ataques
* **Cookies de Segurança:** Implementação de `HttpOnly Cookies` e `Secure Flags` para evitar o sequestro de sessões via scripts maliciosos.
* **Proteção CSRF:** Uso de tokens para validar a integridade das requisições.
* **Rate Limiting:** Controle de fluxo implementado especificamente para mitigação de ataques de força bruta nos endpoints de autenticação.

---

## ⚙️ Configuração do Ambiente

O projeto exige um arquivo `.env` na raiz do diretório para funcionar corretamente.

**Variáveis obrigatórias:**
* `SECRET_KEY` = sua_chave_secreta_aqui
* `EMAIL_USER` = exemplo@gmail.com
* `EMAIL_PASS` = Pass do email.

---

## 🛠️ Automação (Setup Local)

Para facilitar o desenvolvimento e a instalação, utilize os scripts `.bat` inclusos (ambiente Windows):

1.  **Instalação:** Execute `install.bat` para criar o ambiente virtual (`venv`), instalar dependências e rodar as migrações do banco de dados.
2.  **Execução:** Execute `run.bat` para ativar o ambiente e inicializar o servidor de desenvolvimento.

---

## 📍 Endpoints Principais

| Endpoint | Função | Segurança |
| :--- | :--- | :--- |
| `/login/` | Autenticação primária | Rate Limit & CSRF |
| `/verify-2fa/` | Verificação do MFA | Expiração de Token |
| `/admin/` | Painel Administrativo | Acesso Restrito |
| `/static/` | Ativos Estáticos | CSP Policy |

---

## 👤 Autor

* **Henrique Castro** **Victor Fozato** **Rafael Barbosa** 
