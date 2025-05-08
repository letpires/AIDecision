import pytest
from interview.interview_agent import InterviewAgent

def test_start_interview_with_minimal_profile():
    agent = InterviewAgent()
    profile = {"nome": "Teste", "email": "teste@example.com"}
    job = {"title": "Desenvolvedor", "requirements": ["Python", "APIs"]}
    question = agent.start_interview(profile, job)
    assert isinstance(question, str)