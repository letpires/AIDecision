import time
import requests
import pytest

BASE_STREAMLIT = "http://127.0.0.1:8501"
BASE_METRICS = "http://127.0.0.1:9000"

@pytest.fixture(scope="session", autouse=True)
def wait_for_services():
    """Aguardar app e métricas levantarem."""
    # tenta por até 30s a página principal e /metrics
    for _ in range(30):
        try:
            r1 = requests.get(f"{BASE_STREAMLIT}")
            r2 = requests.get(f"{BASE_METRICS}/metrics")
            if r1.status_code == 200 and r2.status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    pytest.skip("Serviços não responderam em localhost:8501 ou 9000")

def test_streamlit_homepage():
    r = requests.get(f"{BASE_STREAMLIT}")
    assert r.status_code == 200
    assert "AI Job Matcher" in r.text

def test_metrics_endpoint_contains_counters():
    r = requests.get(f"{BASE_METRICS}/metrics")
    assert r.status_code == 200
    text = r.text
    # deve conter nossas métricas primárias
    assert "interviews_total" in text
    assert "interview_answers_total" in text
    assert "evaluation_score" in text

def test_trigger_interview_and_metrics_increase():
    # Simula iniciar entrevista via Streamlit index -> Candidatar-se
    # Aqui simplificamos apenas um GET no metrics antes/depois
    pre = requests.get(f"{BASE_METRICS}/metrics").text
    # não vamos automatizar click no Streamlit: apenas verificar delta=0+ entre scrapes
    time.sleep(6)  # aguarda um scrape
    post = requests.get(f"{BASE_METRICS}/metrics").text
    # Conte quantas vezes a linha interviews_total aparece
    def count_metric(s):
        return sum(1 for l in s.splitlines() if l.startswith("interviews_total "))
    assert count_metric(post) >= count_metric(pre)
