import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from config import (
    DATA_DIR, RESUMES_DIR, SUPPORTED_FILE_TYPES,
    JOB_CATEGORIES, MINIMUM_SCORE_FOR_NOTIFICATION
)
from interview.interview_agent import InterviewAgent
from utils.telegram_notifier import TelegramNotifier
from utils.resume_parser import ResumeParser

# Diretório base do projeto (2 níveis acima do arquivo atual)
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuração da página
st.set_page_config(
    page_title="AI Job Matcher",
    page_icon="🎯",
    layout="wide"
)

# Inicialização do estado da sessão
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
    """Retorna uma lista de vagas de exemplo"""
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
    """Carrega as vagas do arquivo JSON"""
    try:
        vagas_path = BASE_DIR / 'dados' / 'vagas.json'
        if not vagas_path.exists():
            st.info("Usando vagas de exemplo para demonstração")
            return get_example_listings()
            
        with open(vagas_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                vagas = data.get('vagas', [])
            else:
                vagas = data
                
            if not vagas:
                st.info("Nenhuma vaga encontrada no arquivo. Usando vagas de exemplo.")
                return get_example_listings()
                
            return vagas
            
    except Exception as e:
        st.info("Erro ao carregar vagas do arquivo. Usando vagas de exemplo.")
        return get_example_listings()

def save_resume(uploaded_file):
    """Salva o currículo enviado e retorna o caminho"""
    if uploaded_file is not None:
        # Criar diretório se não existir
        os.makedirs('uploads', exist_ok=True)
        
        # Gerar nome único para o arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = uploaded_file.name.split('.')[-1]
        filename = f'resume_{timestamp}.{file_extension}'
        filepath = os.path.join('uploads', filename)
        
        # Salvar arquivo
        with open(filepath, 'wb') as f:
            f.write(uploaded_file.getbuffer())
            
        return filepath
    return None

def display_job_card(job):
    """Exibe o card de uma vaga"""
    with st.container():
        st.markdown(f"""
        <div style='padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px;'>
            <h3>{job.get('title', 'Sem título')}</h3>
            <p><strong>Empresa:</strong> {job.get('company', 'Não informada')}</p>
            <p><strong>Local:</strong> {job.get('location', 'Não informado')}</p>
            <p><strong>Faixa Salarial:</strong> {job.get('salary_range', 'Não informada')}</p>
            <p>{job.get('description', 'Sem descrição')}</p>
            
            <details>
                <summary>Requisitos</summary>
                <ul>
                    {''.join([f"<li>{req}</li>" for req in job.get('requirements', [])])}
                </ul>
            </details>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Candidatar-se", key=f"apply_{job.get('id', '')}"):
            st.session_state.selected_job = job
            st.session_state.current_step = 'profile'
            st.rerun()

def profile_section():
    """Seção de perfil do candidato"""
    st.header("Perfil do Candidato")
    
    with st.form("profile_form"):
        nome = st.text_input("Nome completo", value=st.session_state.profile.get('nome', ''))
        email = st.text_input("E-mail", value=st.session_state.profile.get('email', ''))
        telefone = st.text_input("Telefone", value=st.session_state.profile.get('telefone', ''))
        linkedin = st.text_input("LinkedIn URL", value=st.session_state.profile.get('linkedin', ''))
        github = st.text_input("GitHub URL", value=st.session_state.profile.get('github', ''))
        
        uploaded_file = st.file_uploader("Envie seu currículo (PDF)", type=['pdf'])
        
        if st.form_submit_button("Continuar"):
            # Salvar currículo
            resume_path = save_resume(uploaded_file) if uploaded_file else None
            
            # Atualizar perfil
            st.session_state.profile = {
                'nome': nome,
                'email': email,
                'telefone': telefone,
                'linkedin': linkedin,
                'github': github,
                'resume_path': resume_path
            }
            
            if resume_path:
                # Analisar currículo
                resume_data = st.session_state.resume_parser.analyze_resume(resume_path)
                st.session_state.profile.update(resume_data)
            
            st.session_state.current_step = 'interview'
            st.rerun()

def interview_section():
    """Seção de entrevista"""
    st.header("Entrevista Técnica")
    
    if 'current_question' not in st.session_state:
        # Iniciar entrevista
        question = st.session_state.interview_agent.start_interview(
            st.session_state.profile,
            st.session_state.selected_job
        )
        st.session_state.current_question = question
    
    st.write(st.session_state.current_question)
    
    with st.form("interview_form"):
        answer = st.text_area("Sua resposta:")
        if st.form_submit_button("Enviar"):
            result = st.session_state.interview_agent.process_answer(answer)
            
            if result['status'] == 'completed':
                st.session_state.interview_completed = True
                st.session_state.evaluation = result['evaluation']
                
                # Notificar recrutador
                notifier = TelegramNotifier()
                notifier.notify_new_candidate(
                    st.session_state.profile,
                    st.session_state.selected_job,
                    st.session_state.evaluation
                )
                
                st.session_state.current_step = 'results'
            else:
                st.session_state.current_question = result['next_question']
                
            st.rerun()
    
    # Mostrar progresso
    progress = len(st.session_state.interview_agent.interview_state.get('answers', [])) / 5
    st.progress(progress)

def results_section():
    """Seção de resultados"""
    st.header("Resultados da Avaliação")
    
    if st.session_state.evaluation:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Pontuações")
            st.metric("Pontuação Geral", f"{st.session_state.evaluation['score']}%")
            st.metric("Pontuação Técnica", f"{st.session_state.evaluation['technical_score']}%")
            st.metric("Comunicação", f"{st.session_state.evaluation['communication_score']}%")
        
        with col2:
            st.subheader("Pontos Fortes")
            for strength in st.session_state.evaluation['strengths']:
                st.write(f"✓ {strength}")
            
            st.subheader("Áreas para Desenvolvimento")
            for area in st.session_state.evaluation['areas_for_improvement']:
                st.write(f"• {area}")
        
        st.subheader("Feedback")
        st.write(st.session_state.evaluation['feedback'])
        
        st.subheader("Recomendação")
        st.write(st.session_state.evaluation['recommendation'])
        
        if st.button("Voltar para Vagas"):
            # Resetar estado
            st.session_state.current_step = 'jobs'
            st.session_state.selected_job = None
            st.session_state.interview_completed = False
            st.session_state.evaluation = None
            if 'current_question' in st.session_state:
                del st.session_state.current_question
            st.rerun()

def main():
    st.title("🎯 AI Job Matcher")
    
    # Navegação principal
    if st.session_state.current_step == 'jobs':
        st.header("Vagas Disponíveis")
        jobs = load_job_listings()
        for job in jobs:
            display_job_card(job)
    
    elif st.session_state.current_step == 'profile':
        profile_section()
    
    elif st.session_state.current_step == 'interview':
        interview_section()
    
    elif st.session_state.current_step == 'results':
        results_section()

if __name__ == "__main__":
    main() 