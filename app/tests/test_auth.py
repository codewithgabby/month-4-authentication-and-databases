import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user_success():
    unique_email = f"test_{uuid.uuid4()}@example.com"
    

    """ # debugger
    import pdb; pdb.set_trace() """
    
    payload = {
        "email": unique_email,
        "password": "strongpassword123",
        "full_name": "Test User"
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201