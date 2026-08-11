from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User, Listing, WantToBuy, Application, Order, Rating, Notification
from forms import RegistrationForm, LoginForm, ListingForm, WantToBuyForm, OrderNoteForm, RatingForm
from domain import validate_and_build_user

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.before_request
def ensure_tables_exist():
    db.create_all()

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '請先登入系統以存取此功能。'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.context_processor
def inject_unread_notifications():
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    else:
        unread_count = 0
    return dict(unread_notifications_count=unread_count)

def create_notification(user_id, message, link=None):
    notif = Notification(user_id=user_id, message=message, link=link)
    db.session.add(notif)
    db.session.commit()

# --- Auth Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        raw_email = form.email.data or ''
        raw_username = form.username.data or ''
        email_exists = bool(raw_email and User.query.filter_by(email=raw_email.strip().lower()).first())
        username_exists = bool(raw_username and User.query.filter_by(username=raw_username.strip()).first())

        reg_result = validate_and_build_user(
            email=raw_email,
            password=form.password.data,
            password_confirm=form.password_confirm.data,
            username=raw_username,
            social_link=form.social_link.data,
            email_exists=email_exists,
            username_exists=username_exists
        )
        if not reg_result.is_valid:
            for error in reg_result.errors:
                flash(error, 'danger')
            return render_template('auth/register.html', form=form)

        user = User(
            username=reg_result.username,
            email=reg_result.email,
            social_link=reg_result.social_link
        )
        user.set_password(reg_result.password)
        db.session.add(user)
        db.session.commit()
        flash('🎉 註冊成功！請使用新帳號登入。', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/api/register', methods=['POST'])
@csrf.exempt
def api_register():
    data = request.get_json(silent=True) or request.form
    raw_email = data.get('email', '')
    raw_password = data.get('password', '')
    raw_username = data.get('username', '')
    raw_social_link = data.get('social_link', '')

    norm_email = raw_email.strip().lower() if raw_email else ''
    norm_username = raw_username.strip() if raw_username else ''

    email_exists = bool(norm_email and User.query.filter_by(email=norm_email).first())
    username_exists = bool(norm_username and User.query.filter_by(username=norm_username).first())

    reg_result = validate_and_build_user(
        email=raw_email,
        password=raw_password,
        username=raw_username,
        social_link=raw_social_link,
        email_exists=email_exists,
        username_exists=username_exists
    )

    if not reg_result.is_valid:
        return jsonify({'status': 'error', 'message': reg_result.errors[0]}), 400

    final_username = reg_result.username
    if not norm_username:
        base_username = final_username
        counter = 1
        while User.query.filter_by(username=final_username).first():
            final_username = f"{base_username}_{counter}"
            counter += 1

    user = User(
        username=final_username,
        email=reg_result.email,
        social_link=reg_result.social_link
    )
    user.set_password(reg_result.password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': '註冊成功！',
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'social_link': user.social_link,
            'status': reg_result.initial_status,
            'rewards': reg_result.default_rewards
        }
    }), 201

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('❌ 帳號或密碼錯誤，請重新確認！', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash(f'👋 歡迎回來，{user.username}！', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出。', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        social_link = request.form.get('social_link')
        if social_link:
            current_user.social_link = social_link
            db.session.commit()
            flash('個人社群連結已成功更新！', 'success')
            return redirect(url_for('profile'))
    ratings_received = Rating.query.filter_by(ratee_id=current_user.id).order_by(Rating.created_at.desc()).all()
    return render_template('auth/profile.html', user=current_user, ratings=ratings_received)

# --- Dual Board & Listings Routes ---
@app.route('/')
def index():
    team_filter = request.args.get('team', '')
    stadium_filter = request.args.get('stadium', '')
    category_filter = request.args.get('category', '')
    
    # Query Listings (Want to Sell)
    listings_query = Listing.query.filter_by(status='active')
    if team_filter:
        listings_query = listings_query.filter_by(team=team_filter)
    if stadium_filter:
        listings_query = listings_query.filter_by(stadium=stadium_filter)
    if category_filter:
        listings_query = listings_query.filter_by(category=category_filter)
    listings = listings_query.order_by(Listing.created_at.desc()).all()

    # Query Want to Buy
    wtb_query = WantToBuy.query.filter_by(status='active')
    if team_filter:
        wtb_query = wtb_query.filter_by(team=team_filter)
    if stadium_filter:
        wtb_query = wtb_query.filter_by(stadium=stadium_filter)
    if category_filter:
        wtb_query = wtb_query.filter_by(category=category_filter)
    wants_to_buy = wtb_query.order_by(WantToBuy.created_at.desc()).all()

    teams = ['中信兄弟', '統一7-ELEVEn獅', '樂天桃猿', '味全龍', '富邦悍將', '台鋼雄鷹']
    stadiums = ['台北大巨蛋', '台中洲際棒球場', '新莊棒球場', '天母棒球場', '樂天桃園棒球場', '台南市立棒球場', '高雄澄清湖棒球場']

    return render_template('index.html', 
                           listings=listings, 
                           wants_to_buy=wants_to_buy,
                           teams=teams,
                           stadiums=stadiums,
                           selected_team=team_filter,
                           selected_stadium=stadium_filter,
                           selected_category=category_filter)

@app.route('/listing/create', methods=['GET', 'POST'])
@login_required
def create_listing():
    form = ListingForm()
    if form.validate_on_submit():
        listing = Listing(
            seller_id=current_user.id,
            category=form.category.data,
            team=form.team.data,
            stadium=form.stadium.data,
            zone=form.zone.data,
            ticket_type=form.ticket_type.data,
            delivery_method=form.delivery_method.data,
            original_price=form.original_price.data,
            price=form.price.data,
            quantity=form.quantity.data,
            ticket_image_url=form.ticket_image_url.data,
            status='active'
        )
        db.session.add(listing)
        db.session.commit()
        flash('✅ 票券/商品已成功上架待售看板！', 'success')
        return redirect(url_for('index'))
    return render_template('listings/create.html', form=form)

@app.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    listing = db.session.get(Listing, listing_id)
    if not listing:
        flash('找不到該標的物件。', 'danger')
        return redirect(url_for('index'))
    
    existing_application = None
    if current_user.is_authenticated:
        existing_application = Application.query.filter_by(
            listing_id=listing.id, buyer_id=current_user.id
        ).first()

    return render_template('listings/detail.html', listing=listing, existing_application=existing_application)

@app.route('/listing/<int:listing_id>/apply', methods=['POST'])
@login_required
def apply_listing(listing_id):
    listing = db.session.get(Listing, listing_id)
    if not listing or listing.status != 'active':
        flash('該票券目前無法申請購買。', 'warning')
        return redirect(url_for('index'))

    if listing.seller_id == current_user.id:
        flash('您不能申請購買自己刊登的物件！', 'warning')
        return redirect(url_for('listing_detail', listing_id=listing_id))

    existing = Application.query.filter_by(listing_id=listing_id, buyer_id=current_user.id).first()
    if existing:
        flash('您已經提出過購買申請，請靜候賣家審核！', 'info')
        return redirect(url_for('listing_detail', listing_id=listing_id))

    app_record = Application(listing_id=listing_id, buyer_id=current_user.id, status='pending')
    db.session.add(app_record)
    db.session.commit()

    # Notify Seller
    create_notification(
        user_id=listing.seller_id,
        message=f'買家 @{current_user.username} 申請購買您刊登的「{listing.team} @ {listing.stadium}」票券，請至後台審核！',
        link=url_for('seller_dashboard')
    )

    flash('🎉 已成功提交購買申請！賣家審核並選擇您後將會通知您。', 'success')
    return redirect(url_for('listing_detail', listing_id=listing_id))

@app.route('/want_to_buy/create', methods=['GET', 'POST'])
@login_required
def create_want_to_buy():
    form = WantToBuyForm()
    if form.validate_on_submit():
        wtb = WantToBuy(
            buyer_id=current_user.id,
            category=form.category.data,
            team=form.team.data,
            stadium=form.stadium.data,
            zone=form.zone.data,
            max_price=form.max_price.data,
            quantity=form.quantity.data,
            note=form.note.data,
            status='active'
        )
        db.session.add(wtb)
        db.session.commit()
        flash('✅ 已成功發布徵票需求看板！', 'success')
        return redirect(url_for('index'))
    return render_template('listings/create_wtb.html', form=form)

# --- Seller Dashboard & Application Management ---
@app.route('/seller/dashboard')
@login_required
def seller_dashboard():
    my_listings = Listing.query.filter_by(seller_id=current_user.id).order_by(Listing.created_at.desc()).all()
    return render_template('seller/dashboard.html', listings=my_listings)

@app.route('/application/<int:app_id>/accept', methods=['POST'])
@login_required
def accept_application(app_id):
    app_record = db.session.get(Application, app_id)
    if not app_record:
        flash('找不到該申請紀錄。', 'danger')
        return redirect(url_for('seller_dashboard'))

    listing = app_record.listing
    if listing.seller_id != current_user.id:
        flash('無權限進行此操作。', 'danger')
        return redirect(url_for('seller_dashboard'))

    if listing.status != 'active':
        flash('此票券目前狀態不可接受新買家。', 'warning')
        return redirect(url_for('seller_dashboard'))

    # Accept this application
    app_record.status = 'accepted'
    listing.status = 'pending'

    # Auto reject other applications for this listing
    other_apps = Application.query.filter(
        Application.listing_id == listing.id,
        Application.id != app_record.id,
        Application.status == 'pending'
    ).all()
    for other in other_apps:
        other.status = 'rejected'
        create_notification(
            user_id=other.buyer_id,
            message=f'遺憾！賣家已將「{listing.team} @ {listing.stadium}」轉讓給其他買家。',
            link=url_for('index')
        )

    # Create Order
    order = Order(
        listing_id=listing.id,
        buyer_id=app_record.buyer_id,
        seller_id=current_user.id,
        status='awaiting_payment'
    )
    db.session.add(order)
    db.session.commit()

    # Notify winning buyer
    create_notification(
        user_id=app_record.buyer_id,
        message=f'恭喜！賣家已選定您獲選購票「{listing.team} @ {listing.stadium}」，請前往訂單完成【模擬付款】。',
        link=url_for('order_detail', order_id=order.id)
    )

    flash('🎉 已選定買家並建立模擬履約訂單！', 'success')
    return redirect(url_for('order_detail', order_id=order.id))

@app.route('/application/<int:app_id>/reject', methods=['POST'])
@login_required
def reject_application(app_id):
    app_record = db.session.get(Application, app_id)
    if not app_record or app_record.listing.seller_id != current_user.id:
        flash('無操作權限。', 'danger')
        return redirect(url_for('seller_dashboard'))

    app_record.status = 'rejected'
    db.session.commit()

    create_notification(
        user_id=app_record.buyer_id,
        message=f'賣家拒絕了您對「{app_record.listing.team}」票券的申請。',
        link=url_for('index')
    )

    flash('已拒絕該買家申請。', 'info')
    return redirect(url_for('seller_dashboard'))

# --- Order & Mock Escrow State Machine ---
@app.route('/orders')
@login_required
def orders_list():
    buy_orders = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.created_at.desc()).all()
    sell_orders = Order.query.filter_by(seller_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders/list.html', buy_orders=buy_orders, sell_orders=sell_orders)

@app.route('/order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def order_detail(order_id):
    order = db.session.get(Order, order_id)
    if not order or (order.buyer_id != current_user.id and order.seller_id != current_user.id):
        flash('您沒有檢視此訂單的權限。', 'danger')
        return redirect(url_for('index'))

    note_form = OrderNoteForm(note=order.note)
    rating_form = RatingForm()

    if note_form.validate_on_submit() and 'submit_note' in request.form:
        order.note = note_form.note.data
        db.session.commit()
        flash('訂單聯絡資訊已更新。', 'success')
        return redirect(url_for('order_detail', order_id=order.id))

    existing_rating = Rating.query.filter_by(order_id=order.id, rater_id=current_user.id).first()

    return render_template('orders/detail.html', 
                           order=order, 
                           note_form=note_form, 
                           rating_form=rating_form,
                           existing_rating=existing_rating)

@app.route('/order/<int:order_id>/pay', methods=['POST'])
@login_required
def order_pay(order_id):
    order = db.session.get(Order, order_id)
    if not order or order.buyer_id != current_user.id:
        flash('權限不足或訂單不存在。', 'danger')
        return redirect(url_for('index'))

    if order.status != 'awaiting_payment':
        flash('此訂單目前狀態無法執行模擬付款。', 'warning')
        return redirect(url_for('order_detail', order_id=order.id))

    order.status = 'paid'
    db.session.commit()

    create_notification(
        user_id=order.seller_id,
        message=f'買家已完成【模擬付款】，請進行給票/出貨作業！',
        link=url_for('order_detail', order_id=order.id)
    )

    flash('💳 模擬付款成功！已通知賣家發送票券。', 'success')
    return redirect(url_for('order_detail', order_id=order.id))

@app.route('/order/<int:order_id>/ship', methods=['POST'])
@login_required
def order_ship(order_id):
    order = db.session.get(Order, order_id)
    if not order or order.seller_id != current_user.id:
        flash('權限不足或訂單不存在。', 'danger')
        return redirect(url_for('index'))

    if order.status != 'paid':
        flash('買家尚未完成付款，無法出貨。', 'warning')
        return redirect(url_for('order_detail', order_id=order.id))

    order.status = 'shipped'
    db.session.commit()

    create_notification(
        user_id=order.buyer_id,
        message=f'賣家已按「已轉贈/已出貨」，請確認收票！',
        link=url_for('order_detail', order_id=order.id)
    )

    flash('📦 已成功更新狀態為【已出貨/已轉贈】！', 'success')
    return redirect(url_for('order_detail', order_id=order.id))

@app.route('/order/<int:order_id>/complete', methods=['POST'])
@login_required
def order_complete(order_id):
    order = db.session.get(Order, order_id)
    if not order or order.buyer_id != current_user.id:
        flash('權限不足或訂單不存在。', 'danger')
        return redirect(url_for('index'))

    if order.status != 'shipped':
        flash('賣家尚未出貨，無法確認收件。', 'warning')
        return redirect(url_for('order_detail', order_id=order.id))

    order.status = 'completed'
    order.listing.status = 'sold'
    db.session.commit()

    create_notification(
        user_id=order.seller_id,
        message=f'買家已【確認收票】，交易圓滿完成！平台模擬撥款給您，請互相留下評價。',
        link=url_for('order_detail', order_id=order.id)
    )

    flash('🎉 交易完成！感謝您使用 CPBL 球票媒合與履約平台，請為此交易留下評價。', 'success')
    return redirect(url_for('order_detail', order_id=order.id))

@app.route('/order/<int:order_id>/dispute', methods=['POST'])
@login_required
def order_dispute(order_id):
    order = db.session.get(Order, order_id)
    if not order or (order.buyer_id != current_user.id and order.seller_id != current_user.id):
        flash('無操作權限。', 'danger')
        return redirect(url_for('index'))

    order.status = 'disputed'
    db.session.commit()

    other_user_id = order.seller_id if current_user.id == order.buyer_id else order.buyer_id
    create_notification(
        user_id=other_user_id,
        message=f'⚠️ 訂單 #{order.id} 被對方提出了交易爭議申訴，請及時聯繫解決！',
        link=url_for('order_detail', order_id=order.id)
    )

    flash('⚠️ 已提出交易爭議，管理員與雙方將收到申訴通知。', 'warning')
    return redirect(url_for('order_detail', order_id=order.id))

@app.route('/order/<int:order_id>/rate', methods=['POST'])
@login_required
def order_rate(order_id):
    order = db.session.get(Order, order_id)
    if not order or (order.buyer_id != current_user.id and order.seller_id != current_user.id):
        flash('權限不足。', 'danger')
        return redirect(url_for('index'))

    if order.status not in ['completed', 'disputed', 'cancelled', 'buyer_defaulted', 'seller_defaulted']:
        flash('訂單尚未終結，無法提交評價。', 'warning')
        return redirect(url_for('order_detail', order_id=order.id))

    existing = Rating.query.filter_by(order_id=order.id, rater_id=current_user.id).first()
    if existing:
        flash('您已經對此訂單提交過評價囉！', 'info')
        return redirect(url_for('order_detail', order_id=order.id))

    form = RatingForm()
    if form.validate_on_submit():
        ratee_id = order.seller_id if current_user.id == order.buyer_id else order.buyer_id
        is_def = form.is_default.data

        rating = Rating(
            order_id=order.id,
            rater_id=current_user.id,
            ratee_id=ratee_id,
            score=form.score.data,
            is_default=is_def,
            comment=form.comment.data
        )
        db.session.add(rating)
        db.session.commit()

        # Recalculate target user's stats
        ratee_user = db.session.get(User, ratee_id)
        if ratee_user:
            ratee_user.recalculate_stats()
            db.session.commit()

        flash('⭐️ 評價提交成功！感謝您的誠信反饋。', 'success')
        return redirect(url_for('order_detail', order_id=order.id))

    flash('評價資料填寫有誤。', 'danger')
    return redirect(url_for('order_detail', order_id=order.id))

# --- Notifications Route ---
@app.route('/notifications')
@login_required
def notifications():
    user_notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    # Mark all as read
    for n in user_notifs:
        n.is_read = True
    db.session.commit()
    return render_template('notifications.html', notifications=user_notifs)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
