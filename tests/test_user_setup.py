import pytest
from src.main import Clingy

def test_user_setup():
    clingy = Clingy('credentials.json')

    try:
        clingy.authenticate()
    except Exception as e:
        pytest.fail(f"User authentication failed with error: {str(e)}")
