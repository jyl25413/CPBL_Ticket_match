import pytest
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

def test_user_registration_and_login(client):
    # Register Seller
    res = client.post('/register', data={
        'username': 'seller1',
        'email': 'seller@example.com',
        'social_link': 'https://facebook.com/seller1',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'seller1' in res.data or b'\xe8\xa8\xbb\xe5\x86\x8a\xe6\x88\x90\xe5\x8a\x9f' in res.data

    # Login Seller
    res_login = client.post('/login', data={
        'username': 'seller1',
        'password': 'password123'
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b'seller1' in res_login.data

def test_anti_scalping_validation(client):
    # Register user
    client.post('/register', data={
        'username': 'seller_scalp',
        'email': 'scalp@example.com',
        'social_link': 'https://instagram.com/scalp',
        'password': 'password123',
        'password_confirm': 'password123'
    })
    client.post('/login', data={'username': 'seller_scalp', 'password': 'password123'})

    # Try listing ticket with price > original_price (Scalping!)
    res = client.post('/listing/create', data={
        'category': 'ticket',
        'team': '中信兄弟',
        'stadium': '台北大巨蛋',
        'zone': '內野熱區 5 排',
        'ticket_type': '全票',
        'delivery_method': '中職官方APP轉贈',
        'original_price': 500,
        'price': 2000,  # > original_price!
        'quantity': 1
    })
    # Should stay on create page with anti-scalping warning error message
    assert b'original_price' in res.data or b'500' in res.data

def test_full_escrow_workflow(client):
    # 1. Register Seller & Buyer
    client.post('/register', data={'username': 'seller_user', 'email': 's@ex.com', 'social_link': 'https://fb.com/s', 'password': 'pass', 'password_confirm': 'pass'})
    client.post('/register', data={'username': 'buyer_user', 'email': 'b@ex.com', 'social_link': 'https://ig.com/b', 'password': 'pass', 'password_confirm': 'pass'})

    # 2. Seller Creates Listing
    client.post('/login', data={'username': 'seller_user', 'password': 'pass'})
    client.post('/listing/create', data={
        'category': 'ticket',
        'team': '味全龍',
        'stadium': '天母棒球場',
        'zone': '特區 A 排 1 號',
        'ticket_type': '全票',
        'delivery_method': '中職官方APP轉贈',
        'original_price': 600,
        'price': 600,
        'quantity': 1
    })

    with app.app_context():
        listing = Listing.query.first()
        assert listing is not None
        assert listing.price == 600
        listing_id = listing.id

    # 3. Buyer Applies for Ticket
    client.get('/logout')
    client.post('/login', data={'username': 'buyer_user', 'password': 'pass'})
    client.post(f'/listing/{listing_id}/apply', follow_redirects=True)

    with app.app_context():
        app_record = Application.query.filter_by(listing_id=listing_id).first()
        assert app_record is not None
        app_id = app_record.id

    # 4. Seller Accepts Application (Creates Order)
    client.get('/logout')
    client.post('/login', data={'username': 'seller_user', 'password': 'pass'})
    client.post(f'/application/{app_id}/accept', follow_redirects=True)

    with app.app_context():
        order = Order.query.first()
        assert order is not None
        assert order.status == 'awaiting_payment'
        order_id = order.id

    # 5. Buyer Simulates Payment
    client.get('/logout')
    client.post('/login', data={'username': 'buyer_user', 'password': 'pass'})
    client.post(f'/order/{order_id}/pay', follow_redirects=True)

    with app.app_context():
        order = db.session.get(Order, order_id)
        assert order.status == 'paid'

    # 6. Seller Ships / Transfers Ticket
    client.get('/logout')
    client.post('/login', data={'username': 'seller_user', 'password': 'pass'})
    client.post(f'/order/{order_id}/ship', follow_redirects=True)

    with app.app_context():
        order = db.session.get(Order, order_id)
        assert order.status == 'shipped'

    # 7. Buyer Confirms Receipt
    client.get('/logout')
    client.post('/login', data={'username': 'buyer_user', 'password': 'pass'})
    client.post(f'/order/{order_id}/complete', follow_redirects=True)

    with app.app_context():
        order = db.session.get(Order, order_id)
        assert order.status == 'completed'

    # 8. Buyer Leaves 5-Star Rating
    client.post(f'/order/{order_id}/rate', data={
        'score': 5,
        'comment': '非常優質好賣家！讚！'
    }, follow_redirects=True)

    with app.app_context():
        seller = User.query.filter_by(username='seller_user').first()
        assert seller.rating_avg == 5.0
