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

def test_generate_with_auto_rewrite(client, monkeypatch):
    # Mock the rewrite and generate functions to check if rewrite is called
    rewrite_called = False
    original_rewrite_fn = app.generate_rewrite_openai
    
    def mock_rewrite(*args, **kwargs):
        nonlocal rewrite_called
        rewrite_called = True
        return "Rewritten content"
    
    # Mock code generation to avoid actual API calls
    def mock_generate_code(*args, **kwargs):
        return "from diagrams import Diagram\nwith Diagram('Test'):\n    pass"
    
    monkeypatch.setattr(app, 'generate_rewrite_openai', mock_rewrite)
    monkeypatch.setattr(app, 'generate_code_openai', mock_generate_code)
    
    # Mock the subprocess.run to avoid actually running any code
    def mock_subprocess_run(*args, **kwargs):
        class MockResult:
            returncode = 0
            stderr = ""
            stdout = ""
        return MockResult()
    
    monkeypatch.setattr(app.subprocess, 'run', mock_subprocess_run)
    
    # Test that generate endpoint calls rewrite first
    resp = client.post('/generate', json={"description": "test", "provider": "aws"})
    assert rewrite_called, "Rewrite function was not called during generate"

def test_explain_with_provider(client, monkeypatch):
    # Mock the rewrite and explanation functions to check if rewriting is done
    rewrite_called = False
    
    def mock_rewrite(*args, **kwargs):
        nonlocal rewrite_called
        rewrite_called = True
        return "Rewritten prompt with provider-specific terminology"
    
    def mock_explanation(*args, **kwargs):
        return "Provider-specific explanation"
    
    monkeypatch.setattr(app, 'generate_rewrite_openai', mock_rewrite)
    monkeypatch.setattr(app, 'generate_explanation_openai', mock_explanation)
    
    # Test that explain endpoint uses rewrite when provider is specified
    resp = client.post('/explain', json={"code": "test code", "provider": "aws"})
    assert resp.status_code == 200
    assert rewrite_called, "Rewrite function was not called when provider was specified"
    
    # Check response content
    data = resp.get_json()
    assert 'explanation' in data
    assert 'original_prompt' in data
    assert 'rewritten_prompt' in data
    assert 'provider' in data
    assert data['provider'] == 'aws'
