from typing import Dict, List
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
import json
from datetime import datetime
from utils.resume_parser import ResumeParser

class InterviewAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.2)
        self.resume_parser = ResumeParser()
        self.interview_state = {}
        self.current_question_index = 0
        self.max_questions = 5
        
    def start_interview(self, candidate_profile: Dict, job_data: Dict) -> str:
        """Inicia uma nova entrevista"""
        # Enriquecer perfil com dados do currículo se disponível
        if 'resume_path' in candidate_profile:
            candidate_profile = self.resume_parser.enrich_profile(
                candidate_profile,
                candidate_profile['resume_path']
            )
        
        self.interview_state = {
            'candidate': candidate_profile,
            'job': job_data,
            'start_time': datetime.now().isoformat(),
            'questions': [],
            'answers': [],
            'current_question': 0,
            'score': None,
            'feedback': None
        }

        print(self.interview_state)
        
        return self.get_next_question()
    
    def get_next_question(self) -> str:
        """Gera a próxima pergunta com base no contexto atual"""
        if len(self.interview_state['questions']) >= self.max_questions:
            return None
            
        question_prompt = ChatPromptTemplate.from_template("""
        Você é um entrevistador técnico experiente. Com base no perfil do candidato, currículo e requisitos da vaga, 
        gere uma pergunta técnica relevante para avaliar o candidato.
        
        Perfil do Candidato:
        {candidate_profile}
        
        Vaga:
        {job_data}
        
        Perguntas já feitas:
        {previous_questions}
        
        Respostas anteriores:
        {previous_answers}
        
        Gere UMA pergunta técnica específica que:
        1. Não tenha sido feita antes
        2. Seja relevante para os requisitos da vaga
        3. Ajude a avaliar as competências técnicas do candidato
        4. Seja clara e direta
        5. Considere a experiência prévia do candidato mostrada no currículo
        
        A pergunta deve ser em português.
        """)
        
        result = question_prompt.invoke({
            "candidate_profile": json.dumps(self.interview_state['candidate'], ensure_ascii=False),
            "job_data": json.dumps(self.interview_state['job'], ensure_ascii=False),
            "previous_questions": json.dumps(self.interview_state['questions'], ensure_ascii=False),
            "previous_answers": json.dumps(self.interview_state['answers'], ensure_ascii=False)
        })
        
        next_question = self.llm.invoke(result).content
        self.interview_state['questions'].append(next_question)
        return next_question
    
    def process_answer(self, answer: str) -> Dict:
        """Processa a resposta do candidato e retorna o status da entrevista"""
        self.interview_state['answers'].append(answer)
        
        # Se atingiu o número máximo de perguntas, finaliza a entrevista
        if len(self.interview_state['answers']) >= self.max_questions:
            return self.finish_interview()
            
        return {
            'status': 'in_progress',
            'next_question': self.get_next_question(),
            'progress': len(self.interview_state['answers']) / self.max_questions
        }
    
    def finish_interview(self) -> Dict:
        """Finaliza a entrevista e gera o score final"""
        scoring_prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um avaliador técnico experiente. Analise o currículo do candidato, a entrevista técnica e gere uma avaliação detalhada.
            
            Considere:
            1. A experiência prévia do candidato
            2. Formação acadêmica
            3. Certificações relevantes
            4. Habilidades técnicas demonstradas
            5. Qualidade das respostas na entrevista
            6. Adequação ao perfil da vaga
            
            Retorne sua avaliação no seguinte formato JSON (mantenha exatamente as chaves especificadas):
            
            {{
                "score": <número entre 0 e 100>,
                "technical_score": <número entre 0 e 100>,
                "communication_score": <número entre 0 e 100>,
                "strengths": [<lista de pontos fortes>],
                "areas_for_improvement": [<lista de pontos a desenvolver>],
                "recommendation": "<string com recomendação de contratação>",
                "feedback": "<string com feedback construtivo para o candidato>"
            }}
            
            Seja justo e construtivo na avaliação."""),
            ("human", """Perfil do Candidato (incluindo análise do currículo):
            {candidate_profile}
            
            Requisitos da Vaga:
            {job_data}
            
            Entrevista:
            {interview_qa}
            
            Por favor, forneça sua avaliação no formato JSON especificado.""")
        ])
        
        # Preparar o histórico da entrevista
        interview_qa = []
        for q, a in zip(self.interview_state['questions'], self.interview_state['answers']):
            interview_qa.append({"question": q, "answer": a})
        
        result = scoring_prompt.invoke({
            "candidate_profile": json.dumps(self.interview_state['candidate'], ensure_ascii=False),
            "job_data": json.dumps(self.interview_state['job'], ensure_ascii=False),
            "interview_qa": json.dumps(interview_qa, ensure_ascii=False)
        })
        
        response = self.llm.invoke(result)
        # Extrair apenas o JSON da resposta
        json_str = response.content.strip()
        if json_str.startswith('```json'):
            json_str = json_str[7:-3]  # Remove ```json e ```
        elif json_str.startswith('```'):
            json_str = json_str[3:-3]  # Remove ``` e ```
            
        evaluation = json.loads(json_str)
        
        self.interview_state.update({
            'status': 'completed',
            'end_time': datetime.now().isoformat(),
            'evaluation': evaluation
        })
        
        return {
            'status': 'completed',
            'evaluation': evaluation
        } 