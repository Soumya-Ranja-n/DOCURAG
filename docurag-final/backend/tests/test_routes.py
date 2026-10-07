from fastapi.testclient import TestClient
from app.main import app

def test_root():
 with TestClient(app) as c: assert c.get('/').status_code==200
