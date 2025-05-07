# 🎯 AI Job Matching Platform

**Plataforma inteligente de recrutamento** que utiliza IA para analisar perfis de candidatos, conduzir entrevistas técnicas simuladas e gerar recomendações automáticas com envio de notificações via Telegram para recrutadores.

---

## 📌 Visão Geral do Projeto

Este projeto tem como objetivo otimizar o processo de recrutamento utilizando Inteligência Artificial para realizar entrevistas simuladas com candidatos. A aplicação analisa o currículo, conduz uma conversa interativa baseada na vaga escolhida e entrega uma avaliação com base em critérios técnicos e comportamentais.

---

## 🚀 Funcionalidades

- 📋 Visualização de vagas cadastradas
- 🧑 Criação de perfil de candidato com LinkedIn e GitHub
- 📄 Upload e parsing automático de currículos (PDF)
- 🤖 Entrevista técnica com agente de IA (OpenAI)
- 📊 Avaliação com pontuação, pontos fortes e sugestões de melhoria
- 📲 Notificação automática ao recrutador via Telegram

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

### 4. Configure variáveis de ambiente em `.env`

```env
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 5. Crie os diretórios esperados

```bash
mkdir -p uploads dados
```

---

## ▶️ Executando a Aplicação

Execute o comando abaixo:

```bash
streamlit run app/main.py
```

Acesse via navegador: [http://localhost:8501](http://localhost:8501)

---

## 🐳 Executando com Docker

### 1. Crie o `Dockerfile`

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

### 2. Crie o arquivo `.env`

```env
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 3. Construa e execute a imagem

```bash
docker build -t ai-job-matcher .
docker run -p 8501:8501 --env-file .env ai-job-matcher
```

---

## ☁️ Deploy em Produção

### Deploy na AWS Elastic Beanstalk (com Docker)

1. Faça push da imagem para o ECR:

```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account_id>.dkr.ecr.<region>.amazonaws.com
docker tag ai-job-matcher:latest <account_id>.dkr.ecr.<region>.amazonaws.com/ai-job-matcher:latest
docker push <account_id>.dkr.ecr.<region>.amazonaws.com/ai-job-matcher:latest
```

2. Crie a aplicação no Elastic Beanstalk com plataforma Docker.
3. Configure as variáveis de ambiente no painel.
4. Faça o deploy usando a imagem do ECR.

### Deploy Gratuito com Render

1. Crie uma conta em [https://render.com](https://render.com)
2. Crie um novo Web Service e selecione Docker
3. Conecte seu repositório GitHub
4. Configure as variáveis de ambiente
5. Clique em “Deploy”

---

## 📚 Como Usar

1. **Escolha uma vaga** – veja as oportunidades disponíveis
2. **Preencha seu perfil** – nome, e-mail, redes, currículo
3. **Participe da entrevista técnica** – perguntas adaptadas à vaga
4. **Receba sua avaliação final** – com pontuação e feedback completo
5. **O recrutador é notificado** via Telegram

---

## 🧱 Arquitetura

| Componente     | Tecnologia              |
|----------------|--------------------------|
| Interface      | Streamlit                |
| IA Entrevista  | OpenAI GPT (via SDK)     |
| Parsing de CV  | PDFMiner, PyMuPDF        |
| Notificação    | Telegram Bot API         |
| Backend        | Lógica integrada no front (sem API separada) |
| Armazenamento  | Sistema de arquivos local|

---

## 🤝 Contribuindo

1. Faça um fork do repositório
2. Crie um branch: `feature/minha-feature`
3. Commit suas alterações
4. Push para seu fork
5. Abra um Pull Request

---

## 📄 Licença

Distribuído sob a Licença MIT.  
Consulte o arquivo `LICENSE` para mais detalhes.
