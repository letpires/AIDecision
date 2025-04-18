from typing import Dict, List, Any
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
import json
from utils.rag_store import RAGStore

class JobMatcherAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.2)
        self.job_listings = self._load_job_listings()
        self.rag_store = RAGStore()
        
    def _load_job_listings(self) -> List[Dict]:
        # TODO: Load job listings from database or file
        return [
            {
                "id": 1,
                "title": "Software Engineer",
                "company": "Tech Corp",
                "description": "Looking for experienced software engineer...",
                "requirements": ["Python", "Django", "AWS"],
                "category": "Technology"
            }
        ]
    
    def _load_historical_data(self) -> Dict:
        """Carrega dados históricos dos arquivos JSON"""
        try:
            with open('dados/applicants.json', 'r', encoding='utf-8') as f:
                applicants = json.load(f)
            with open('dados/prospects.json', 'r', encoding='utf-8') as f:
                prospects = json.load(f)
            with open('dados/vagas.json', 'r', encoding='utf-8') as f:
                vagas = json.load(f)
            return {
                'applicants': applicants,
                'prospects': prospects,
                'vagas': vagas
            }
        except FileNotFoundError:
            return {'applicants': [], 'prospects': [], 'vagas': []}

    def get_next_question(self, profile: Dict, job_requirements: List[str], 
                         previous_questions: List[str], answers: List[str]) -> str:
        """Gera a próxima pergunta da entrevista baseada no contexto completo"""
        
        # Buscar dados históricos relevantes
        historical_data = self._load_historical_data()
        similar_profiles = self.rag_store.find_similar_profiles(profile)
        job_insights = self.rag_store.get_job_insights(job_requirements)
        
        question_prompt = ChatPromptTemplate.from_template("""
        Com base nas informações fornecidas, gere uma pergunta relevante para a entrevista.
        
        PERFIL DO CANDIDATO:
        {profile}
        
        REQUISITOS DA VAGA:
        {requirements}
        
        PERGUNTAS ANTERIORES:
        {previous_questions}
        
        RESPOSTAS ANTERIORES:
        {answers}
        
        DADOS HISTÓRICOS RELEVANTES:
        Perfis similares: {similar_profiles}
        Insights da vaga: {job_insights}
        
        Gere UMA pergunta técnica específica que:
        1. Não tenha sido feita antes
        2. Avalie competências críticas para a vaga
        3. Considere o histórico de respostas
        4. Explore pontos não cobertos nas respostas anteriores
        5. Seja relevante para o nível de experiência do candidato
        
        A pergunta deve ser em português e direta.
        """)
        
        result = question_prompt.invoke({
            "profile": json.dumps(profile, ensure_ascii=False),
            "requirements": json.dumps(job_requirements, ensure_ascii=False),
            "previous_questions": json.dumps(previous_questions, ensure_ascii=False),
            "answers": json.dumps(answers, ensure_ascii=False),
            "similar_profiles": json.dumps(similar_profiles, ensure_ascii=False),
            "job_insights": json.dumps(job_insights, ensure_ascii=False)
        })
        
        return self.llm.invoke(result).content

    def calculate_match_score(self, profile: Dict, job_requirements: List[str], 
                            interview_responses: List[str]) -> Dict:
        """Calcula o score de match considerando todas as fontes de dados"""
        
        # Carregar dados históricos
        historical_data = self._load_historical_data()
        similar_profiles = self.rag_store.find_similar_profiles(profile)
        job_insights = self.rag_store.get_job_insights(job_requirements)
        market_trends = self.rag_store.get_market_trends()
        
        scoring_prompt = ChatPromptTemplate.from_template("""
        Analise todas as informações disponíveis e calcule um score de match detalhado.
        
        PERFIL DO CANDIDATO:
        {profile}
        
        REQUISITOS DA VAGA:
        {requirements}
        
        RESPOSTAS DA ENTREVISTA:
        {responses}
        
        DADOS HISTÓRICOS:
        Perfis similares: {similar_profiles}
        Insights da vaga: {job_insights}
        Tendências do mercado: {market_trends}
        
        Considere:
        1. Alinhamento técnico com os requisitos
        2. Experiência relevante
        3. Qualidade das respostas na entrevista
        4. Histórico de candidatos similares
        5. Tendências do mercado
        6. Certificações e formação
        7. Habilidades complementares
        
        Retorne um JSON com:
        {{
            "score": float entre 0 e 1,
            "strengths": lista de pontos fortes identificados,
            "weaknesses": lista de pontos a desenvolver,
            "historical_insights": lista de insights baseados em dados históricos,
            "recommendation": string com recomendação final,
            "technical_evaluation": {{
                "skills_match": float entre 0 e 1,
                "experience_match": float entre 0 e 1,
                "interview_performance": float entre 0 e 1
            }}
        }}
        """)
        
        result = scoring_prompt.invoke({
            "profile": json.dumps(profile, ensure_ascii=False),
            "requirements": json.dumps(job_requirements, ensure_ascii=False),
            "responses": json.dumps(interview_responses, ensure_ascii=False),
            "similar_profiles": json.dumps(similar_profiles, ensure_ascii=False),
            "job_insights": json.dumps(job_insights, ensure_ascii=False),
            "market_trends": json.dumps(market_trends, ensure_ascii=False)
        })
        
        return eval(self.llm.invoke(result).content) 