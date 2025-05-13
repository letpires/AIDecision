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
- 📈 Monitoramento de métricas com Prometheus e Grafana
- 🧪 Testes unitários e funcionais para garantir qualidade

---

## 🛠️ Instalação Local

```bash
git clone <repository-url>
cd <repository-name>

python -m venv venv
source venv/bin/activate         # ou venv\Scripts\activate no Windows

pip install -r requirements.txt
```

Crie um arquivo `.env` com:

```env
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Crie os diretórios necessários:

```bash
mkdir -p uploads dados logs
```

---

## ▶️ Executando a Aplicação Localmente

```bash
streamlit run app/main.py
```

Abra [http://localhost:8501](http://localhost:8501) no navegador.

---

## 🧪 Executando Testes Unitários e Funcionais

### Testes Unitários

Executam validações de funções isoladas, como:
- Análise de currículo (ResumeParser)
- Avaliação de resposta (InterviewAgent)

```bash
pytest tests/unit/
```

### Testes Funcionais

Simulam o fluxo completo da aplicação, incluindo:
- Escolha de vaga
- Preenchimento do perfil
- Entrevista e resultado final

```bash
pytest tests/functional/
```

---

## 📊 Monitoramento com Prometheus + Grafana

1. A aplicação expõe métricas em http://localhost:9000/metrics
2. Use docker-compose up -d para subir Prometheus e Grafana

Acesse:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

Importe o dashboard JSON:
- `monitoring/ai_job_matcher_grafana_dashboard.json`

---

## 🐳 Dockerfile (localizado em app/Dockerfile)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y build-essential && \
    pip install --no-cache-dir -r requirements.txt

ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501

EXPOSE 8501
CMD ["streamlit", "run", "main.py"]
```

---

## 🐳 Docker Compose (na raiz)

```yaml
version: '3.7'

services:
  app:
    build:
      context: ./app
      dockerfile: Dockerfile
    container_name: ai-job-matcher-app
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./uploads:/app/uploads
      - ./dados:/app/dados
      - ./logs:/app/logs
    restart: always

  prometheus:
    image: prom/prometheus
    container_name: prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    restart: always

  grafana:
    image: grafana/grafana
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-storage:/var/lib/grafana
    depends_on:
      - prometheus
    restart: always

volumes:
  grafana-storage:
```

---

## ▶️ Executando com Docker Compose

```bash
docker compose up --build -d         # Subir os serviços
docker compose logs -f               # Acompanhar logs
docker compose down                  # Encerrar tudo
```

---
## ☁️ Acessar os Serviços

| Serviço    | URL                                            | Usuário | Senha          |
| ---------- | ---------------------------------------------- | ------- | -------------- |
| Streamlit  | [http://localhost:8501](http://localhost:8501) | —       | —              |
| Prometheus | [http://localhost:9090](http://localhost:9090) | —       | —              |
| Grafana    | [http://localhost:3000](http://localhost:3000) | admin   | admin (padrão) |


---
## 🚀 Importando o Dashboard no Grafana

1. Baixe o arquivo JSON do dashboard:

```bash
wget -O monitoring/ai_job_matcher_dashboard.json \
  https://<seu-repo>/monitoring/monitoring_dashboard.json
```

2. Acesse o Grafana em http://localhost:3000

3. No menu lateral, clique em “+” → Import

4. No campo “Upload JSON file or Grafana.com Dashboard”, selecione monitoring/monitoring_dashboard.json

5. Garanta que o campo Name seja preenchido automaticamente como “Monitoramento - AI Job Matcher”

6. elecione a Data source chamada Prometheus

7. Clique em Import

Você verá agora:

Total de Entrevistas (stat panel)
Acurácia (gauge panel)
Média da Pontuação Geral (time series)
Média da Pontuação Técnica (time series)
Média da Pontuação de Comunicação (time series)


---
## ☁️ Deploy com Render

1. Crie conta em https://render.com
2. Conecte com GitHub
3. Configure como serviço Web (Docker)
4. Adicione variáveis de ambiente e publique

---

## 📚 Como Usar

1. Escolha uma vaga
2. Preencha seu perfil
3. Participe da entrevista com IA
4. Receba a avaliação
5. Recrutador é notificado

---

## 🧱 Arquitetura

| Componente     | Tecnologia              |
|----------------|--------------------------|
| Interface      | Streamlit                |
| IA Entrevista  | OpenAI GPT (via SDK)     |
| Parsing de CV  | PyMuPDF / PDFMiner       |
| Notificação    | Telegram Bot API         |
| Métricas       | Prometheus + Grafana     |
| Armazenamento  | Sistema de arquivos local|

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie um branch `feature/nome-da-feature`
3. Faça commits claros
4. Abra um Pull Request

---

## 📄 Licença

MIT License
