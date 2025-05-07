# 🎯 AI Job Matching Platform

Uma plataforma de matching inteligente que usa IA para avaliar candidatos, conduzir entrevistas automatizadas e notificar recrutadores via Telegram.

## 🚀 Funcionalidades

- 📋 Exibição de vagas
- 🧑 Cadastro de perfil de candidatos
- 📄 Upload e análise de currículos
- 🤖 Entrevista automatizada com IA (OpenAI)
- 📊 Sistema de pontuação e recomendação
- 📲 Notificações via Telegram para recrutadores

---

## 🛠️ Instalação Local

### 1. Clone o repositório

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate         # Linux/macOS
venv\Scripts\activate          # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Crie um arquivo `.env` na raiz do projeto com:

```env
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 5. Crie os diretórios necessários

```bash
mkdir -p uploads dados
```

---

## ▶️ Executando a Aplicação

```bash
streamlit run app/main.py
```

Abra seu navegador e acesse:  
[http://localhost:8501](http://localhost:8501)

---

## 🐳 Executando com Docker

### 1. Crie um arquivo `Dockerfile` com o seguinte conteúdo:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLECORS=false

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]
```

### 2. Crie um arquivo `.env` com as variáveis de ambiente:

```env
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 3. Construa a imagem Docker:

```bash
docker build -t ai-job-matcher .
```

### 4. Rode o container:

```bash
docker run -p 8501:8501 --env-file .env ai-job-matcher
```

Acesse: [http://localhost:8501](http://localhost:8501)

---

## **Deploy na Nuvem**

### **Deploy Usando AWS Elastic Beanstalk**

1. **Pré-requisitos**:
   - Instale a AWS CLI e configure com suas credenciais.
   - Certifique-se de ter um repositório ECR (Elastic Container Registry) configurado.

2. **Push da Imagem para o ECR**:
   ```bash
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account_id>.dkr.ecr.<region>.amazonaws.com
   docker tag minha-api-fastapi:latest <account_id>.dkr.ecr.<region>.amazonaws.com/minha-api-fastapi:latest
   docker push <account_id>.dkr.ecr.<region>.amazonaws.com/minha-api-fastapi:latest
   ```

3. **Criar a Aplicação no Elastic Beanstalk**:
   - Acesse o console da AWS e vá até o Elastic Beanstalk.
   - Crie uma nova aplicação com o nome desejado.
   - Escolha a plataforma Docker e forneça o URI da imagem do ECR.

4. **Configurar o Ambiente**:
   - Configure a porta 8000 no Elastic Beanstalk.
   - Faça o deploy e aguarde a inicialização.

5. **Acessar o Endpoint da Aplicação**:
   O Elastic Beanstalk fornecerá um domínio onde sua aplicação estará acessível.

### **Deploy Usando uma Conta RENDER(Gratuito)**

1. Crie uma conta no Render

2. Crie um novo serviço Web
  
3. Escolha "Docker" como opção de deploy
  
4. Forneça o link do repositório do seu projeto (GitHub/GitLab)

5. Configure variáveis de ambiente e publique!


---

## 📚 Como Usar

1. **Vagas** – Explore vagas disponíveis
2. **Perfil** – Preencha seu perfil e envie seu currículo
3. **Entrevista** – Responda perguntas simuladas com IA
4. **Resultado** – Veja sua pontuação e feedback automático

---

## 🧱 Arquitetura

| Componente     | Tecnologia              |
|----------------|--------------------------|
| Interface      | Streamlit                |
| Entrevista     | OpenAI + lógica local    |
| Análise CV     | Parser de PDF            |
| Notificações   | Telegram Bot             |
| Armazenamento  | Sistema de arquivos local|

---

## 🤝 Contribuindo

1. Fork este repositório
2. Crie um novo branch: `feature/sua-feature`
3. Commit suas alterações: `git commit -m 'feat: adiciona nova funcionalidade'`
4. Push para o branch remoto
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.
