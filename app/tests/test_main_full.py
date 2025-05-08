import pytest
from app.main import get_example_listings, load_job_listings

def test_get_example_listings_returns_expected_structure():
    listings = get_example_listings()
    assert isinstance(listings, list)
    assert len(listings) >= 1
    assert "title" in listings[0]
    assert "company" in listings[0]
    assert isinstance(listings[0]["requirements"], list)

def test_load_job_listings_fallback(monkeypatch):
    # Força erro simulando ausência de arquivo JSON
    monkeypatch.setattr("app.main.BASE_DIR", "invalid/path")
    listings = load_job_listings()
    assert isinstance(listings, list)
    assert len(listings) >= 1
    assert "title" in listings[0]