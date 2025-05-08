import pytest
from streamlit.testing.v1 import AppTest

def test_app_loads():
    at = AppTest.from_file("app/main.py")
    at.run()
    assert "AI Job Matcher" in at.title