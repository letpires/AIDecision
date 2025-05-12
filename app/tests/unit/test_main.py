import os
import json
import tempfile
import pytest
from pathlib import Path
from prometheus_client import Counter, Gauge, CollectorRegistry

# vamos importar diretamente as funções
from app.main import (
    get_example_listings,
    load_job_listings,
    save_resume,
    get_or_create_metric
)

class DummyFile:
    """Simula o UploadedFile do Streamlit."""
    def __init__(self, name, content: bytes):
        self.name = name
        self._content = content
    def getbuffer(self):
        return self._content

def test_get_example_listings_structure():
    listings = get_example_listings()
    assert isinstance(listings, list)
    assert "id" in listings[0]
    assert "title" in listings[0]

def test_load_job_listings_fallback(tmp_path, monkeypatch):
    # forçar ausência de dados/vagas.json
    fake_base = tmp_path / "no_data_dir"
    monkeypatch.setenv("BASE_DIR", str(fake_base))
    # monkeypatch o BASE_DIR usado por load_job_listings
    import app.main as m
    m.BASE_DIR = fake_base
    listings = load_job_listings()
    assert listings == get_example_listings()

def test_load_job_listings_from_file(tmp_path, monkeypatch):
    # criar arquivo vagas.json válido
    data = {"vagas": [{"id":"x1","title":"T","company":"C"}]}
    d = tmp_path / "dados"
    d.mkdir()
    f = d / "vagas.json"
    f.write_text(json.dumps(data), encoding="utf-8")
    # monkeypatch PATH
    import app.main as m
    m.BASE_DIR = tmp_path
    listings = load_job_listings()
    assert listings == data["vagas"]

def test_save_resume_creates_file(tmp_path, monkeypatch):
    # monkeypatch o CWD para tmp_path
    monkeypatch.chdir(tmp_path)
    content = b"PDF-DATA"
    dummy = DummyFile("meu.pdf", content)
    path = save_resume(dummy)
    assert path is not None
    assert os.path.exists(path)
    assert Path(path).read_bytes() == content

def test_get_or_create_metric_new():
    registry = CollectorRegistry()
    # inspeciona um registry vazio
    counter = get_or_create_metric(Counter, "u_test", "doc")
    assert isinstance(counter, Counter)
    # deve existir no default REGISTRY
    same = get_or_create_metric(Counter, "u_test", "doc")
    assert same is counter
