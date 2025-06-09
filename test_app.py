import os
import tempfile
import pytest
from app import app, UPLOAD_FOLDER

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_generate_missing_fields(client):
    resp = client.post('/generate', json={})
    assert resp.status_code == 400
    assert b'Description is required' in resp.data

def test_generate_invalid_api_key(client):
    # API key is no longer required in the request body; this test is obsolete
    pass

def test_generate_empty_description(client):
    resp = client.post('/generate', json={"description": ""})
    assert resp.status_code == 400
    assert b'Description must be a non-empty string' in resp.data

def test_diagram_file_serving(client):
    # Create a dummy file
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    test_file = os.path.join(UPLOAD_FOLDER, 'dummy.png')
    with open(test_file, 'wb') as f:
        f.write(b'1234')
    resp = client.get('/diagrams/dummy.png')
    assert resp.status_code == 200
    assert resp.data == b'1234'
    os.remove(test_file)

def test_rewrite_missing_fields(client):
    resp = client.post('/rewrite', json={})
    assert resp.status_code == 400
    assert b'user_input is required' in resp.data

def test_rewrite_invalid_provider(client):
    resp = client.post('/rewrite', json={"user_input": "test", "provider": "invalid"})
    assert resp.status_code == 400
    assert b'Cloud provider is required' in resp.data

def test_rewrite_empty_user_input(client):
    resp = client.post('/rewrite', json={"user_input": "", "provider": "aws"})
    assert resp.status_code == 400
    assert b'user_input is required and must be a non-empty string' in resp.data
