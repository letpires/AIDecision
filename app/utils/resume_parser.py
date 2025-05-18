from typing import Dict
import base64
from openai import OpenAI
from config import OPENAI_API_KEY

class ResumeParser:
    def __init__(self):
        self.client = OpenAI()
        
    def encode_pdf_to_base64(self, pdf_path: str) -> str:
        """Convert PDF file to base64 string"""
        with open(pdf_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')

    def analyze_resume(self, pdf_path: str) -> dict:
        """Analyze resume using GPT-4"""
        try:
            # Convert PDF to base64
            base64_pdf = self.encode_pdf_to_base64(pdf_path)
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert resume analyzer. You will receive a PDF document encoded in base64. Extract key information from it."
                },
                {
                    "role": "user",
                    "content": f"""Here is a resume in base64 format. Please analyze it and extract the following information in JSON format:
                    name, email, phone, education, experience (list of jobs with company, title, duration), skills, certifications.
                    Make sure the output is valid JSON.
                    
                    Base64 PDF content:
                    {base64_pdf}"""
                }
            ]

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=4096
            )

            try:
                return eval(response.choices[0].message.content)
            except:
                # Fallback structure if parsing fails
                return {
                    "name": "",
                    "email": "",
                    "phone": "",
                    "education": [],
                    "experience": [],
                    "skills": [],
                    "certifications": []
                }
                
        except Exception as e:
            print(f"Error analyzing resume: {str(e)}")
            return {
                "name": "",
                "email": "",
                "phone": "",
                "education": [],
                "experience": [],
                "skills": [],
                "certifications": []
            }

    def enrich_profile(self, profile: dict, pdf_path: str) -> dict:
        """Enrich candidate profile with resume data"""
        resume_data = self.analyze_resume(pdf_path)
        
        # Update profile with resume data
        profile.update({
            "nome": resume_data.get("name", profile.get("nome", "")),
            "email": resume_data.get("email", profile.get("email", "")),
            "telefone": resume_data.get("phone", profile.get("telefone", "")),
            "educacao": resume_data.get("education", []),
            "experiencia": resume_data.get("experience", []),
            "habilidades": resume_data.get("skills", []),
            "certificacoes": resume_data.get("certifications", [])
        })
        
        return profile 