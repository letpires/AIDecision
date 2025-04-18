import json
from typing import List, Dict
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI

class RAGStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(temperature=0)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self._initialize_stores()
    
    def _initialize_stores(self):
        """Inicializa as bases de conhecimento vetoriais"""
        try:
            # Carregar dados históricos
            with open('dados/applicants.json', 'r', encoding='utf-8') as f:
                self.applicants_data = json.load(f)
            with open('dados/prospects.json', 'r', encoding='utf-8') as f:
                self.prospects_data = json.load(f)
            with open('dados/vagas.json', 'r', encoding='utf-8') as f:
                self.vagas_data = json.load(f)
            
            # Criar textos para indexação
            applicants_texts = [json.dumps(app, ensure_ascii=False) for app in self.applicants_data]
            prospects_texts = [json.dumps(pros, ensure_ascii=False) for pros in self.prospects_data]
            vagas_texts = [json.dumps(vaga, ensure_ascii=False) for vaga in self.vagas_data]
            
            # Criar bases vetoriais
            self.applicants_store = FAISS.from_texts(
                applicants_texts,
                self.embeddings
            )
            self.prospects_store = FAISS.from_texts(
                prospects_texts,
                self.embeddings
            )
            self.vagas_store = FAISS.from_texts(
                vagas_texts,
                self.embeddings
            )
        except FileNotFoundError:
            print("Arquivos de dados históricos não encontrados. Inicializando stores vazias.")
            self.applicants_data = []
            self.prospects_data = []
            self.vagas_data = []
            self.applicants_store = None
            self.prospects_store = None
            self.vagas_store = None
    
    def find_similar_profiles(self, profile: Dict, k: int = 5) -> List[Dict]:
        """Encontra perfis similares no histórico"""
        if not self.applicants_store:
            return []
        
        query = json.dumps(profile, ensure_ascii=False)
        similar_docs = self.applicants_store.similarity_search(query, k=k)
        
        similar_profiles = []
        for doc in similar_docs:
            try:
                profile_data = json.loads(doc.page_content)
                similar_profiles.append({
                    "profile": profile_data,
                    "similarity_score": doc.metadata.get("score", 0)
                })
            except json.JSONDecodeError:
                continue
        
        return similar_profiles
    
    def get_job_insights(self, job_requirements: List[str]) -> Dict:
        """Obtém insights sobre a vaga baseados em dados históricos"""
        if not self.vagas_store:
            return {}
        
        query = json.dumps({"requirements": job_requirements}, ensure_ascii=False)
        similar_jobs = self.vagas_store.similarity_search(query, k=5)
        
        # Analisar padrões de sucesso
        success_patterns = []
        required_skills = set()
        common_challenges = []
        
        for doc in similar_jobs:
            try:
                job_data = json.loads(doc.page_content)
                if "success_factors" in job_data:
                    success_patterns.extend(job_data["success_factors"])
                if "required_skills" in job_data:
                    required_skills.update(job_data["required_skills"])
                if "common_challenges" in job_data:
                    common_challenges.extend(job_data["common_challenges"])
            except json.JSONDecodeError:
                continue
        
        return {
            "success_patterns": list(set(success_patterns)),
            "critical_skills": list(required_skills),
            "common_challenges": list(set(common_challenges)),
            "similar_jobs_count": len(similar_jobs)
        }
    
    def get_market_trends(self) -> Dict:
        """Analisa tendências do mercado baseadas nos dados históricos"""
        if not self.vagas_store or not self.applicants_store:
            return {}
        
        # Análise de habilidades mais requisitadas
        all_skills = []
        skill_demand = {}
        salary_ranges = []
        
        # Analisar vagas
        for vaga in self.vagas_data:
            if "required_skills" in vaga:
                for skill in vaga["required_skills"]:
                    skill_demand[skill] = skill_demand.get(skill, 0) + 1
            if "salary_range" in vaga:
                salary_ranges.append(vaga["salary_range"])
        
        # Analisar candidatos bem sucedidos
        successful_skills = []
        for app in self.applicants_data:
            if app.get("hired", False):
                successful_skills.extend(app.get("skills", []))
        
        return {
            "top_skills": sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:10],
            "successful_candidate_skills": list(set(successful_skills)),
            "salary_trends": self._analyze_salary_ranges(salary_ranges),
            "market_demand": self._analyze_market_demand()
        }
    
    def _analyze_salary_ranges(self, salary_ranges: List[str]) -> Dict:
        """Analisa tendências salariais"""
        # Implementação simplificada - pode ser expandida conforme necessidade
        return {
            "ranges": salary_ranges,
            "average": len(salary_ranges) // 2 if salary_ranges else None
        }
    
    def _analyze_market_demand(self) -> Dict:
        """Analisa demanda do mercado por área"""
        if not self.vagas_data:
            return {}
        
        area_demand = {}
        for vaga in self.vagas_data:
            area = vaga.get("area", "Outros")
            area_demand[area] = area_demand.get(area, 0) + 1
        
        return {
            "by_area": area_demand,
            "total_positions": len(self.vagas_data)
        }