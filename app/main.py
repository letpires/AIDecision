import streamlit as st
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from prometheus_client import Counter, start_http_server
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

from prometheus_client import REGISTRY, Counter

def get_or_create_counter(name, documentation):
    try:
        return REGISTRY._names_to_collectors[name]
    except KeyError:
        return Counter(name, documentation)

interview_counter = get_or_create_counter("interviews_total", "Total de entrevistas iniciadas")
answer_counter = get_or_create_counter("interview_answers_total", "Total de respostas dadas")
# Iniciar servidor de métricas (Prometheus)
    
# Iniciar Prometheus com verificação de porta
def start_prometheus_safe():
    import socket
    import errno
    from prometheus_client import start_http_server

    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(("0.0.0.0", 9000))
        test_socket.close()
        start_http_server(9000)
        logging.info("Prometheus iniciado na porta 9000")
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            logging.warning("Porta 9000 já está em uso. Ignorando Prometheus.")
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
    return [
        {
            "id": "dev001",
            "title": "Desenvolvedor Python Sênior",
            "company": "TechCorp Brasil",
            "location": "São Paulo, SP (Híbrido)",
            "salary_range": "R$ 15.000 - R$ 18.000",
            "description": "Procuramos um desenvolvedor Python sênior...",
            "requirements": ["5+ anos de experiência com Python", "Experiência com ML", "APIs", "Docker", "Inglês"]
        }
    ]

def load_job_listings():
    try:
        vagas_path = BASE_DIR / 'dados' / 'vagas.json'
        if not vagas_path.exists():
            st.info("Usando vagas de exemplo para demonstração")
            return get_example_listings()
        with open(vagas_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('vagas', []) if isinstance(data, dict) else data
    except Exception as e:
        logging.error(f"Erro ao carregar vagas: {e}")
        return get_example_listings()

def save_resume(uploaded_file):
    if uploaded_file:
        os.makedirs('uploads', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = uploaded_file.name.split('.')[-1]
        path = f'uploads/resume_{timestamp}.{ext}'
        with open(path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return path
    return None

def display_job_card(job):
    with st.container():
        st.markdown(f"""
        <div style='padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px;'>
            <h3>{job.get('title')}</h3>
            <p><strong>Empresa:</strong> {job.get('company')}</p>
            <p><strong>Local:</strong> {job.get('location')}</p>
            <p><strong>Salário:</strong> {job.get('salary_range')}</p>
            <p>{job.get('description')}</p>
            <details><summary>Requisitos</summary><ul>
            {''.join([f"<li>{r}</li>" for r in job.get('requirements', [])])}
            </ul></details>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Candidatar-se", key=f"apply_{job.get('id')}"):
            st.session_state.selected_job = job
            st.session_state.current_step = 'profile'
            st.rerun()

def profile_section():
    st.header("Perfil do Candidato")
    with st.form("profile_form"):
        nome = st.text_input("Nome completo", value=st.session_state.profile.get('nome', ''))
        email = st.text_input("E-mail", value=st.session_state.profile.get('email', ''))
        telefone = st.text_input("Telefone", value=st.session_state.profile.get('telefone', ''))
        linkedin = st.text_input("LinkedIn", value=st.session_state.profile.get('linkedin', ''))
        github = st.text_input("GitHub", value=st.session_state.profile.get('github', ''))
        uploaded_file = st.file_uploader("Currículo (PDF)", type=['pdf'])

        if st.form_submit_button("Continuar"):
            path = save_resume(uploaded_file) if uploaded_file else None
            st.session_state.profile = {
                'nome': nome, 'email': email, 'telefone': telefone,
                'linkedin': linkedin, 'github': github, 'resume_path': path
            }
            if path:
                try:
                    data = st.session_state.resume_parser.analyze_resume(path)
                    st.session_state.profile.update(data)
                except Exception as e:
                    logging.warning(f"Erro ao analisar currículo: {e}")
            st.session_state.current_step = 'interview'
            st.rerun()

def interview_section():
    st.header("Entrevista Técnica")
    if 'current_question' not in st.session_state:
        question = st.session_state.interview_agent.start_interview(
            st.session_state.profile, st.session_state.selected_job)
        interview_counter.inc()
        st.session_state.current_question = question

    st.write(st.session_state.current_question)
    with st.form("interview_form"):
        answer = st.text_area("Sua resposta:")
        if st.form_submit_button("Enviar"):
            answer_counter.inc()
            result = st.session_state.interview_agent.process_answer(answer)
            if result['status'] == 'completed':
                st.session_state.interview_completed = True
                st.session_state.evaluation = result['evaluation']
                try:
                    TelegramNotifier().notify_new_candidate(
                        st.session_state.profile,
                        st.session_state.selected_job,
                        st.session_state.evaluation
                    )
                except Exception as e:
                    logging.warning(f"Erro ao enviar Telegram: {e}")
                st.session_state.current_step = 'results'
            else:
                st.session_state.current_question = result['next_question']
            st.rerun()

    progress = len(st.session_state.interview_agent.interview_state.get('answers', [])) / 5
    st.progress(progress)

def results_section():
    st.header("Resultados da Avaliação")
    if st.session_state.evaluation:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Geral", f"{st.session_state.evaluation['score']}%")
            st.metric("Técnica", f"{st.session_state.evaluation['technical_score']}%")
            st.metric("Comunicação", f"{st.session_state.evaluation['communication_score']}%")
        with col2:
            st.subheader("Pontos Fortes")
            for s in st.session_state.evaluation['strengths']:
                st.write(f"✓ {s}")
            st.subheader("Áreas de Melhoria")
            for a in st.session_state.evaluation['areas_for_improvement']:
                st.write(f"• {a}")
        st.subheader("Feedback")
        st.write(st.session_state.evaluation['feedback'])
        st.subheader("Recomendação")
        st.write(st.session_state.evaluation['recommendation'])

        if st.button("Voltar para Vagas"):
            st.session_state.current_step = 'jobs'
            st.session_state.selected_job = None
            st.session_state.interview_completed = False
            st.session_state.evaluation = None
            if 'current_question' in st.session_state:
                del st.session_state.current_question
            st.rerun()

def main():
    st.title("🎯 AI Job Matcher")
    if st.session_state.current_step == 'jobs':
        st.header("Vagas Disponíveis")
        for job in load_job_listings():
            display_job_card(job)
    elif st.session_state.current_step == 'profile':
        profile_section()
    elif st.session_state.current_step == 'interview':
        interview_section()
    elif st.session_state.current_step == 'results':
        results_section()

if __name__ == "__main__":
    main()
