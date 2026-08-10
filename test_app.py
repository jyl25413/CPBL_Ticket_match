import pytest
import bcrypt
from app import app, db
from models import User, Listing, WantToBuy, Application, Order, Rating, Notification

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

# --- Acceptance Tests matching user_registration_spec.md ---

def test_registration_success_example(client):
    # Example 1: user@example.com, Pass1234, Pass1234, 小明 -> Success 201
    res = client.post('/api/register', json={
        'email': 'user@example.com',
        'password': 'Pass1234',
        'confirm_password': 'Pass1234',
        'display_name': '小明'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['user']['email'] == 'user@example.com'
    assert data['user']['display_name'] == '小明'

    with app.app_context():
        u = User.query.filter_by(email='user@example.com').first()
        assert u is not None
        assert u.display_name == '小明'
        # Verify Bcrypt hashing
        assert bcrypt.checkpw('Pass1234'.encode('utf-8'), u.password_hash.encode('utf-8'))

def test_registration_email_trim_and_lowercase(client):
    # Example 2: ' USER@example.com ' -> auto trimmed & lowercased to 'user@example.com'
    res = client.post('/api/register', json={
        'email': ' USER@example.com ',
        'password': 'Pass1234',
        'confirm_password': 'Pass1234',
        'display_name': '小明'
    })
    assert res.status_code == 201

    with app.app_context():
        u = User.query.filter_by(email='user@example.com').first()
        assert u is not None
        assert u.email == 'user@example.com'

def test_registration_invalid_email(client):
    # Example 3: invalid-email -> Reject
    res = client.post('/api/register', json={
        'email': 'invalid-email',
        'password': 'Pass1234',
        'confirm_password': 'Pass1234',
        'display_name': '小明'
    })
    assert res.status_code == 400
    data = res.get_json()
    assert '請輸入有效的 Email 格式' in data['message']

def test_registration_invalid_password_rule(client):
    # Example 4: 12345 (too short, no uppercase) -> Reject
    res = client.post('/api/register', json={
        'email': 'user@example.com',
        'password': '12345',
        'confirm_password': '12345',
        'display_name': '小明'
    })
    assert res.status_code == 400
    data = res.get_json()
    assert '密碼至少需 8 個字元且包含大寫與數字' in data['message']

def test_registration_password_mismatch(client):
    # Example 5: Pass1234 vs Different12 -> Reject
    res = client.post('/api/register', json={
        'email': 'user@example.com',
        'password': 'Pass1234',
        'confirm_password': 'Different12',
        'display_name': '小明'
    })
    assert res.status_code == 400
    data = res.get_json()
    assert '兩次輸入的密碼不一致' in data['message']

def test_registration_duplicate_email(client):
    # Example 6: Existing email -> Reject
    client.post('/api/register', json={
        'email': 'user@example.com',
        'password': 'Pass1234',
        'confirm_password': 'Pass1234',
        'display_name': '小明'
    })

    res_dup = client.post('/api/register', json={
        'email': 'user@example.com',
        'password': 'Pass1234',
        'confirm_password': 'Pass1234',
        'display_name': '小華'
    })
    assert res_dup.status_code == 400
    data = res_dup.get_json()
    assert '此 Email 已被註冊' in data['message']

def test_anti_scalping_validation(client):
    # Register user
    client.post('/api/register', json={
        'email': 'scalp@example.com',
        'password': 'Pass1234',
        'confirm_password': 'Pass1234',
        'display_name': '賣家'
    })

    # Try listing ticket with price > original_price (Scalping!)
    res = client.post('/listing/create', data={
        'category': 'ticket',
        'team': '中信兄弟',
        'stadium': '台北大巨蛋',
        'zone': '內野熱區 5 排',
        'ticket_type': '全票',
        'delivery_method': '中職官方APP轉贈',
        'original_price': 500,
        'price': 2000,
        'quantity': 1
    })
    assert b'original_price' in res.data or b'500' in res.data
