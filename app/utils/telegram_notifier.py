from typing import Dict
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramNotifier:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, message: str) -> bool:
        """Envia uma mensagem para o chat do Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Erro ao enviar mensagem para o Telegram: {e}")
            return False

    def notify_new_candidate(self, profile: Dict, job: Dict, evaluation: Dict) -> bool:
        """Notifica sobre um novo candidato"""
        strengths_list = evaluation.get('strengths', ['Não informados'])
        strengths_text = f"{chr(8226)} " + f"\n{chr(8226)} ".join(strengths_list)
        
        message = f"""🎯 <b>Novo Candidato!</b>

👤 <b>Nome:</b> {profile.get('nome', 'Não informado')}
📧 <b>Email:</b> {profile.get('email', 'Não informado')}
📱 <b>Telefone:</b> {profile.get('telefone', 'Não informado')}

💼 <b>Vaga:</b> {job.get('title', 'Não informada')}
🏢 <b>Empresa:</b> {job.get('company', 'Não informada')}

📊 <b>Avaliação:</b>
- Score Geral: {evaluation.get('score', 0)}%
- Score Técnico: {evaluation.get('technical_score', 0)}%
- Score Comunicação: {evaluation.get('communication_score', 0)}%

💪 <b>Pontos Fortes:</b>
{strengths_text}

📈 <b>Recomendação:</b>
{evaluation.get('recommendation', 'Não disponível')}"""
        
        return self.send_message(message)

def send_telegram_notification(candidate_name: str, job_title: str, evaluation: Dict) -> bool:
    """
    Envia notificação via Telegram para o recrutador quando um candidato
    tem um score alto ou se candidata a uma vaga prioritária
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Configurações do Telegram não encontradas")
        return False
        
    score = evaluation.get('score', 0)
    
    # Formatar a mensagem
    message = f"""
🎯 Nova Candidatura Relevante!

👤 Candidato: {candidate_name}
📋 Vaga: {job_title}
⭐ Score: {score:.0f}/100

Avaliação Técnica:
📊 Score Técnico: {evaluation.get('technical_score', 0):.0f}/100
🗣 Score Comunicação: {evaluation.get('communication_score', 0):.0f}/100

💪 Pontos Fortes:
{chr(10).join(['• ' + s for s in evaluation.get('strengths', [])])}

📝 Recomendação:
{evaluation.get('recommendation', 'N/A')}
"""
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar notificação: {str(e)}")
        return False 