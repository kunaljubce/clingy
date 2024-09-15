import pytest
import hahahahaah
from src.main import Clingy

def test_authentication():
    clingy = Clingy('credentials.json')

    try:
        clingy.authenticate()
    except Exception as e:
        pytest.fail(f"Authentication failed with error: {str(e)}")
