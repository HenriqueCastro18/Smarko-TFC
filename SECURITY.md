## 3. Estratégia de Criptografia e Comunicação Segura (Smarko Security)

Para garantir a confidencialidade e integridade dos dados transitados e armazenados no sistema Smarko, adotamos os seguintes padrões e algoritmos criptográficos da indústria:

### 3.1. Dados em Trânsito (TLS/HTTPS)
* **Estratégia:** Toda a comunicação entre o cliente e o servidor exige tráfego cifrado.
* **Justificativa Técnica:** O Django foi configurado (`SECURE_SSL_REDIRECT = True`, `SESSION_COOKIE_SECURE = True`) para forçar o redirecionamento HTTP para HTTPS e garantir que cookies de sessão não sejam interceptados em redes abertas. Utilizamos HSTS (`SECURE_HSTS_SECONDS`) para prevenir ataques de *downgrade* de protocolo.

### 3.2. Dados em Repouso (AES-256)
* **Estratégia:** Criptografia transparente de dados armazenados no banco de dados.
* **Justificativa Técnica:** O Smarko utiliza o Google Cloud Firestore como solução de banco de dados (NoSQL). O Firestore criptografa automaticamente todos os dados em repouso antes de serem gravados no disco, utilizando o algoritmo **AES-256** (Advanced Encryption Standard), considerado de nível militar e resistente a ataques de força bruta modernos.

### 3.3. Armazenamento de Senhas (PBKDF2)
* **Estratégia:** Senhas nunca são armazenadas em texto plano, passando por um processo de *hashing* com *salt* dinâmico.
* **Justificativa Técnica:** Utilizamos o algoritmo **PBKDF2** combinado com a função de hash **SHA-256** (`BCryptSHA256PasswordHasher` do Django). Esta escolha adiciona um custo computacional (work factor) que inviabiliza ataques de dicionário e *rainbow tables*, protegendo as credenciais mesmo em caso de vazamento do banco de dados.

### 3.4. Gestão de Chaves Criptográficas e Segredos
* **Estratégia:** Isolamento completo de chaves de API e segredos de aplicação do código-fonte.
* **Justificativa Técnica:** A `SECRET_KEY` do Django e a `FIREBASE_WEB_API_KEY` são injetadas no ambiente de execução via variáveis de ambiente (`.env`). O arquivo `.env` e o certificado `serviceAccountKey.json` são estritamente ignorados pelo controle de versão (Git) para prevenir a exposição acidental de credenciais críticas.