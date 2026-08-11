"""
Characterization tests to lock down current behavior of /register and /api/register routes.
"""
import pytest
from app import app, db
from models import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_characterization_html_register_success(client):
    res = client.post('/register', data={
        'username': 'char_user1',
        'email': 'char1@example.com',
        'social_link': 'https://facebook.com/char1',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)
    
    assert res.status_code == 200
    with app.app_context():
        u = User.query.filter_by(email='char1@example.com').first()
        assert u is not None
        assert u.username == 'char_user1'

def test_characterization_html_register_invalid_email(client):
    res = client.post('/register', data={
        'username': 'char_user2',
        'email': 'invalid-email',
        'social_link': 'https://facebook.com/char2',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)
    
    assert res.status_code == 200
    assert b'Email' in res.data or b'\xe6%a0%bc%e5%bc%8f' in res.data

def test_characterization_api_register_success(client):
    res = client.post('/api/register', json={
        'email': 'char_api@example.com',
        'password': 'password123'
    })
    
    assert res.status_code == 201
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['user']['email'] == 'char_api@example.com'
    assert data['user']['username'] == 'char_api'

def test_characterization_api_register_duplicate_email(client):
    client.post('/api/register', json={
        'email': 'dup@example.com',
        'password': 'password123'
    })
    
    res = client.post('/api/register', json={
        'email': 'dup@example.com',
        'password': 'password123'
    })
    
    assert res.status_code == 400
    data = res.get_json()
    assert data['status'] == 'error'
    assert '已被註冊' in data['message'] or 'Email' in data['message']
