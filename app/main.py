# ─── Métricas + ML Antes de tudo ──────────────────────────────────────────────
from prometheus_client import start_http_server, Counter, Gauge, REGISTRY
from utils.ml_matcher import gerar_features_com_llm, montar_features, score_ml

# Inicia o endpoint /metrics em 0.0.0.0:9000
start_http_server(9000, addr="0.0.0.0")

def get_or_create_metric(metric_cls, name, documentation):
    try:
        return REGISTRY._names_to_collectors[name]
    except KeyError:
        return metric_cls(name, documentation)

# Counters
interview_counter        = get_or_create_metric(Counter, "interviews_total",                       "Total de entrevistas iniciadas")
answer_counter           = get_or_create_metric(Counter, "interview_answers_total",                 "Total de respostas dadas")
score_total_counter      = get_or_create_metric(Counter, "interview_score_total",                   "Soma acumulada das pontuações gerais")
tech_score_total_counter = get_or_create_metric(Counter, "interview_technical_score_total",         "Soma acumulada das pontuações técnicas")
comm_score_total_counter = get_or_create_metric(Counter, "interview_communication_score_total",     "Soma acumulada das pontuações de comunicação")

# Gauges
score_gauge              = get_or_create_metric(Gauge,   "evaluation_score",                         "Pontuação geral da avaliação")
technical_gauge          = get_or_create_metric(Gauge,   "evaluation_technical_score",               "Pontuação técnica")
communication_gauge      = get_or_create_metric(Gauge,   "evaluation_communication_score",            "Pontuação de comunicação")
# ───────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd 
import json
import os
import logging
from datetime import datetime
from pathlib import Path

from config import (
    DATA_DIR, RESUMES_DIR, SUPPORTED_FILE_TYPES,
    JOB_CATEGORIES, MINIMUM_SCORE_FOR_NOTIFICATION
)
from interview.interview_agent import InterviewAgent
from utils.telegram_notifier import TelegramNotifier
from utils.resume_parser import ResumeParser

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuração da página
st.set_page_config(
    page_title="AI Job Matcher",
    page_icon="🎯",
    layout="wide"
)

# Logging
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Estado da sessão
if 'interview_agent'     not in st.session_state: st.session_state.interview_agent     = InterviewAgent()
if 'resume_parser'       not in st.session_state: st.session_state.resume_parser       = ResumeParser()
if 'current_step'        not in st.session_state: st.session_state.current_step        = 'jobs'
if 'profile'             not in st.session_state: st.session_state.profile             = {}
if 'selected_job'        not in st.session_state: st.session_state.selected_job        = None
if 'interview_completed' not in st.session_state: st.session_state.interview_completed = False
if 'evaluation'          not in st.session_state: st.session_state.evaluation          = None

def get_example_listings():
    return [
        {
            "id": "dev001",
            "title": "Desenvolvedor Python Sênior",
            "company": "TechCorp Brasil",
            "location": "São Paulo, SP (Híbrido)",
            "salary_range": "R$ 15.000 - R$ 18.000",
            "description": "Procuramos um desenvolvedor Python sênior para atuar no desenvolvimento de soluções de IA e machine learning. O profissional irá trabalhar com tecnologias modernas como FastAPI, PyTorch e Docker.",
            "requirements": [
                "5+ anos de experiência com Python",
                "Experiência com frameworks de ML (PyTorch, TensorFlow)",
                "Conhecimento em APIs REST e FastAPI",
                "Experiência com Docker e containers",
                "Inglês avançado"
            ]
        },
        {
            "id": "data001",
            "title": "Cientista de Dados",
            "company": "DataInsights",
            "location": "Remoto",
            "salary_range": "R$ 12.000 - R$ 15.000",
            "description": "Buscamos cientista de dados para desenvolver modelos preditivos e soluções de análise avançada. Você irá trabalhar com grandes volumes de dados e implementar soluções de machine learning.",
            "requirements": [
                "Mestrado ou Doutorado em área relacionada",
                "Experiência com Python e R",
                "Conhecimento em SQL e bancos de dados",
                "Experiência com bibliotecas de ML",
                "Boa comunicação"
            ]
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
            vagas = data.get('vagas', []) if isinstance(data, dict) else data
            if not vagas:
                st.info("Nenhuma vaga encontrada no arquivo. Usando vagas de exemplo.")
                return get_example_listings()
            return vagas
    except Exception as e:
        st.info("Erro ao carregar vagas do arquivo. Usando vagas de exemplo.")
        logging.error(f"Erro load_job_listings: {e}")
        return get_example_listings()

def save_resume(uploaded_file):
    if uploaded_file is not None:
        os.makedirs('uploads', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = uploaded_file.name.split('.')[-1]
        filename = f'resume_{timestamp}.{ext}'
        filepath = os.path.join('uploads', filename)
        with open(filepath, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return filepath
    return None

def display_job_card(job):
    with st.container():
        st.markdown(f"""
        <div style='padding:20px; border:1px solid #ddd; border-radius:10px; margin-bottom:20px;'>
          <h3>{job.get('title')}</h3>
          <p><strong>Empresa:</strong> {job.get('company')}</p>
          <p><strong>Local:</strong> {job.get('location')}</p>
          <p><strong>Salário:</strong> {job.get('salary_range')}</p>
          <p>{job.get('description')}</p>
        </div>
        """, unsafe_allow_html=True)
    if st.button("Candidatar-se", key=f"apply_{job.get('id')}"):
        st.session_state.selected_job = job
        st.session_state.current_step = 'profile'
        st.rerun()

def profile_section():
    st.header("Perfil do Candidato")
    with st.form("profile_form"):
        nome  = st.text_input("Nome completo", value=st.session_state.profile.get('nome',''))
        email = st.text_input("E-mail", value=st.session_state.profile.get('email',''))
        tel   = st.text_input("Telefone", value=st.session_state.profile.get('telefone',''))
        linkedin = st.text_input("LinkedIn URL", value=st.session_state.profile.get('linkedin',''))
        github   = st.text_input("GitHub URL", value=st.session_state.profile.get('github',''))
        up = st.file_uploader("Envie seu currículo (PDF)", type=['pdf'])
        if st.form_submit_button("Continuar"):
            path = save_resume(up)
            st.session_state.profile = {
                'nome':nome, 'email':email, 'telefone':tel,
                'linkedin':linkedin, 'github':github, 'resume_path':path
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
        q = st.session_state.interview_agent.start_interview(
            st.session_state.profile, st.session_state.selected_job
        )
        st.session_state.current_question = q
        interview_counter.inc()

    st.write(st.session_state.current_question)
    with st.form("interview_form"):
        ans = st.text_area("Sua resposta:")
        if st.form_submit_button("Enviar"):
            answer_counter.inc()
            res = st.session_state.interview_agent.process_answer(ans)
            if res['status'] == 'completed':
                ev = res['evaluation']
                st.session_state.evaluation = ev
                st.session_state.interview_completed = True

                # Set gauges
                score_gauge.set(ev["score"])
                technical_gauge.set(ev["technical_score"])
                communication_gauge.set(ev["communication_score"])
                # Inc totals
                score_total_counter.inc(ev["score"])
                tech_score_total_counter.inc(ev["technical_score"])
                comm_score_total_counter.inc(ev["communication_score"])

                # LLM + ML scoring
                txt_cv  = st.session_state.profile.get("content","")
                txt_vaga = (st.session_state.selected_job.get("description","")
                            + "\n".join(st.session_state.selected_job.get("requirements",[])))
                feats = gerar_features_com_llm(txt_cv, txt_vaga)
                vec   = montar_features(profile=feats, job={}, extra_data={})
                ml_sc = score_ml(vec)
                # final blend
                final = round(0.6*ml_sc + 0.4*(ev["score"]/100), 3)
                st.session_state.evaluation.update({
                    'score_final': final,
                    'score_ml': round(ml_sc*100,2),
                    'score_agent': ev["score"]
                })

                if final > 0.7:
                    try:
                        TelegramNotifier().notify_new_candidate(
                            st.session_state.profile,
                            st.session_state.selected_job,
                            st.session_state.evaluation
                        )
                    except Exception:
                        pass

                st.session_state.current_step = 'results'
            else:
                st.session_state.current_question = res['next_question']
            st.rerun()

    prog = len(st.session_state.interview_agent.interview_state.get('answers',[])) / 5
    st.progress(prog)

def results_section():
    st.header("Resultados da Avaliação")
    ev = st.session_state.evaluation or {}
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Score Final",      f"{ev.get('score_final',0)*100:.2f}%")
        st.metric("Score Agente",     f"{ev.get('score_agent',0)}%")
        st.metric("Score ML",         f"{ev.get('score_ml',0)}%")
    with col2:
        st.metric("Técnica",          f"{ev.get('technical_score',0)}%")
        st.metric("Comunicação",      f"{ev.get('communication_score',0)}%")
    st.subheader("Pontos Fortes")
    for s in ev.get('strengths',[]): st.write(f"✓ {s}")
    st.subheader("Áreas para Desenvolvimento")
    for a in ev.get('areas_for_improvement',[]): st.write(f"• {a}")
    st.write("**Feedback**");     st.write(ev.get('feedback',''))
    st.write("**Recomendação**");  st.write(ev.get('recommendation',''))

    if st.button("Voltar para Vagas"):
        for k in ['current_step','selected_job','interview_completed','evaluation','current_question']:
            st.session_state.pop(k,None)
        st.session_state.current_step = 'jobs'
        st.rerun()

def main():
    st.title("🎯 AI Job Matcher")
    step = st.session_state.current_step

    if step == 'jobs':
        for j in load_job_listings():
            display_job_card(j)

    elif step == 'profile':
        profile_section()

    elif step == 'interview':
        interview_section()

    elif step == 'results':
        results_section()


if __name__ == "__main__":
    main()
