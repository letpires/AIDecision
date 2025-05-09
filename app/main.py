import streamlit as st
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from prometheus_client import Counter, Gauge, start_http_server, REGISTRY
from config import (
    DATA_DIR, RESUMES_DIR, SUPPORTED_FILE_TYPES,
    JOB_CATEGORIES, MINIMUM_SCORE_FOR_NOTIFICATION
)
from interview.interview_agent import InterviewAgent
from utils.telegram_notifier import TelegramNotifier
from utils.resume_parser import ResumeParser

# Configuração de logging
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_or_create_metric(metric_cls, name, documentation):
    try:
        return REGISTRY._names_to_collectors[name]
    except KeyError:
        return metric_cls(name, documentation)

interview_counter = get_or_create_metric(Counter, "interviews_total", "Total de entrevistas iniciadas")
answer_counter = get_or_create_metric(Counter, "interview_answers_total", "Total de respostas dadas")

# **Novos counters para acumular scores**
score_total_counter = get_or_create_metric(Counter, "interview_score_total", "Soma acumulada das pontuações gerais")
tech_score_total_counter = get_or_create_metric(Counter, "interview_technical_score_total", "Soma acumulada das pontuações técnicas")
comm_score_total_counter = get_or_create_metric(Counter, "interview_communication_score_total", "Soma acumulada das pontuações de comunicação")

score_gauge = get_or_create_metric(Gauge, "evaluation_score", "Pontuação geral da avaliação")
technical_gauge = get_or_create_metric(Gauge, "evaluation_technical_score", "Pontuação técnica")
communication_gauge = get_or_create_metric(Gauge, "evaluation_communication_score", "Pontuação de comunicação")

# Iniciar Prometheus com verificação de porta
def start_prometheus_safe():
    import socket
    import errno
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(("0.0.0.0", 9000))
        test_socket.close()
        start_http_server(9000)
        logging.info("Prometheus iniciado na porta 9000")
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            logging.warning("Porta 9000 já está em uso.")
        else:
            logging.error(f"Erro ao iniciar Prometheus: {e}")

start_prometheus_safe()

BASE_DIR = Path(__file__).resolve().parent.parent

st.set_page_config(
    page_title="AI Job Matcher",
    page_icon="🎯",
    layout="wide"
)

if 'interview_agent' not in st.session_state:
    st.session_state.interview_agent = InterviewAgent()
if 'resume_parser' not in st.session_state:
    st.session_state.resume_parser = ResumeParser()
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'jobs'
if 'profile' not in st.session_state:
    st.session_state.profile = {}
if 'selected_job' not in st.session_state:
    st.session_state.selected_job = None
if 'interview_completed' not in st.session_state:
    st.session_state.interview_completed = False
if 'evaluation' not in st.session_state:
    st.session_state.evaluation = None

def get_example_listings():
    return [{
        "id": "dev001",
        "title": "Desenvolvedor Python Sênior",
        "company": "TechCorp Brasil",
        "location": "São Paulo, SP",
        "salary_range": "R$ 15.000 - R$ 18.000",
        "description": "Desenvolvimento de soluções de IA.",
        "requirements": ["Python", "ML", "FastAPI", "Docker", "Inglês"]
    }]

def load_job_listings():
    try:
        path = BASE_DIR / 'dados' / 'vagas.json'
        if not path.exists():
            return get_example_listings()
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('vagas', []) if isinstance(data, dict) else data
    except Exception as e:
        logging.error(f"Erro ao carregar vagas: {e}")
        return get_example_listings()

def save_resume(uploaded_file):
    if uploaded_file:
        os.makedirs('uploads', exist_ok=True)
        filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{uploaded_file.name.split('.')[-1]}"
        path = os.path.join("uploads", filename)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return path
    return None

def display_job_card(job):
    with st.container():
        st.markdown(f"""
        <div style='padding: 20px; border: 1px solid #ddd; border-radius: 10px;'>
            <h4>{job['title']}</h4>
            <p><b>Empresa:</b> {job['company']} — {job['location']}</p>
            <p><b>Salário:</b> {job['salary_range']}</p>
            <p>{job['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Candidatar-se", key=job['id']):
            st.session_state.selected_job = job
            st.session_state.current_step = 'profile'
            st.rerun()

def profile_section():
    st.header("Perfil")
    with st.form("profile_form"):
        nome = st.text_input("Nome", value=st.session_state.profile.get("nome", ""))
        email = st.text_input("Email", value=st.session_state.profile.get("email", ""))
        linkedin = st.text_input("LinkedIn", value=st.session_state.profile.get("linkedin", ""))
        github = st.text_input("GitHub", value=st.session_state.profile.get("github", ""))
        file = st.file_uploader("Currículo (PDF)", type=["pdf"])

        if st.form_submit_button("Continuar"):
            path = save_resume(file)
            st.session_state.profile = {
                "nome": nome, "email": email, "linkedin": linkedin,
                "github": github, "resume_path": path
            }
            if path:
                try:
                    data = st.session_state.resume_parser.analyze_resume(path)
                    st.session_state.profile.update(data)
                except Exception as e:
                    logging.warning(f"Erro ao analisar currículo: {e}")
            st.session_state.current_step = "interview"
            st.rerun()

def interview_section():
    st.header("Entrevista Técnica")
    if "current_question" not in st.session_state:
        question = st.session_state.interview_agent.start_interview(
            st.session_state.profile, st.session_state.selected_job)
        st.session_state.current_question = question
        interview_counter.inc()

    st.write(st.session_state.current_question)
    with st.form("interview_form"):
        answer = st.text_area("Sua resposta:")
        if st.form_submit_button("Enviar"):
            answer_counter.inc()
            result = st.session_state.interview_agent.process_answer(answer)
            if result['status'] == 'completed':
                st.session_state.evaluation = result['evaluation']
                st.session_state.interview_completed = True
                evaluation = st.session_state.evaluation
                score_gauge.set(evaluation["score"])
                technical_gauge.set(evaluation["technical_score"])
                communication_gauge.set(evaluation["communication_score"])
                # após processar result['status']=="completed"
                evaluation = result['evaluation']
                score_gauge.set(evaluation["score"])
                technical_gauge.set(evaluation["technical_score"])
                communication_gauge.set(evaluation["communication_score"])

                # **Incrementa os totals** para o Grafana calcular médias
                score_total_counter.inc(evaluation["score"])
                tech_score_total_counter.inc(evaluation["technical_score"])
                comm_score_total_counter.inc(evaluation["communication_score"])

                try:
                    TelegramNotifier().notify_new_candidate(
                        st.session_state.profile,
                        st.session_state.selected_job,
                        st.session_state.evaluation
                    )
                except Exception as e:
                    logging.error(f"Erro Telegram: {e}")
                st.session_state.current_step = "results"
            else:
                st.session_state.current_question = result['next_question']
            st.rerun()

def results_section():
    st.header("Resultados")
    e = st.session_state.evaluation
    if e:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Geral", f"{e['score']}%")
            st.metric("Técnica", f"{e['technical_score']}%")
            st.metric("Comunicação", f"{e['communication_score']}%")
        with col2:
            st.subheader("Pontos Fortes")
            for s in e['strengths']:
                st.write(f"✓ {s}")
            st.subheader("A melhorar")
            for a in e['areas_for_improvement']:
                st.write(f"• {a}")
        st.write("**Feedback**")
        st.write(e["feedback"])
        st.write("**Recomendação**")
        st.write(e["recommendation"])

        if st.button("Voltar"):
            st.session_state.current_step = 'jobs'
            st.session_state.selected_job = None
            st.session_state.interview_completed = False
            st.session_state.evaluation = None
            st.session_state.pop("current_question", None)
            st.rerun()

def main():
    st.title("🎯 AI Job Matcher")
    step = st.session_state.current_step
    if step == "jobs":
        for j in load_job_listings():
            display_job_card(j)
    elif step == "profile":
        profile_section()
    elif step == "interview":
        interview_section()
    elif step == "results":
        results_section()

if __name__ == "__main__":
    main()