# Relatório de Inventário de Dados — Smarko Security
 
Este documento detalha o inventário de dados pessoais tratados no sistema **Smarko**, em conformidade com o Artigo 37 da LGPD.
 
## 1. Mapeamento Detalhado (Baseado em Firestore & Django Models)
 
| Dado Pessoal | Categoria | Finalidade | Local de Armazenamento |
| :--- | :--- | :--- | :--- |
| **E-mail / Username** | Identificação | Identificador único para login e comunicação (2FA). | Firestore (`perfis`) e logs |
| **Senha (Hash)** | Segurança | Autenticação via hash criptográfico (bcrypt/sha256). | Firestore (`perfis`) |
| **Endereço IP** | Técnico | Defesa contra ataques e auditoria de acessos. | Firestore (`logs_seguranca`) |
| **Status de Bloqueio** | Segurança | Controle de acesso (`bloqueado_ate`) para proteção de conta. | Firestore (`perfis`) |
| **Tentativas Falhas** | Segurança | Contador de erros de login para ativação de Rate Limit. | Firestore (`perfis`) |
| **Logs de Evento** | Auditoria | Registro de ações (ex: "Reset Solicitado") com timestamp. | Firestore (`logs_seguranca`) |
 
## 2. Fluxo e Infraestrutura
*   **Armazenamento:** Os dados são persistidos no **Google Cloud (Firebase Firestore)**, utilizando criptografia nativa em repouso.
*   **Comunicação:** O tráfego de e-mails para validação de identidade utiliza o gateway **SMTP do Gmail**.
*   **Criptografia:** Senhas são processadas via hash antes do armazenamento, garantindo que o dado original não seja recuperável.
 
## 3. Retenção
*   Os dados de perfil são mantidos enquanto a conta do usuário estiver ativa.
*   Os logs de segurança e auditoria (incluindo IP) são armazenados para cumprimento do **Marco Civil da Internet** (mínimo de 6 meses).
 