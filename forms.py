from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange, URL, Optional
from models import User

TEAMS = [
    ('中信兄弟', '中信兄弟'),
    ('統一7-ELEVEn獅', '統一7-ELEVEn獅'),
    ('樂天桃猿', '樂天桃猿'),
    ('味全龍', '味全龍'),
    ('富邦悍將', '富邦悍將'),
    ('台鋼雄鷹', '台鋼雄鷹')
]

STADIUMS = [
    ('台北大巨蛋', '台北大巨蛋'),
    ('台中洲際棒球場', '台中洲際棒球場'),
    ('新莊棒球場', '新莊棒球場'),
    ('天母棒球場', '天母棒球場'),
    ('樂天桃園棒球場', '樂天桃園棒球場'),
    ('台南市立棒球場', '台南市立棒球場'),
    ('高雄澄清湖棒球場', '高雄澄清湖棒球場')
]

TICKET_TYPES = [
    ('全票', '全票'),
    ('半票', '半票'),
    ('愛心票/身障票', '愛心票/身障票'),
    ('季票/會員票', '季票/會員票')
]

DELIVERY_METHODS = [
    ('中職官方APP轉贈', '中職官方APP轉贈'),
    ('超商取票序號', '超商取票序號'),
    ('現場面交', '現場面交'),
    ('郵寄/宅配', '郵寄/宅配')
]

class RegistrationForm(FlaskForm):
    username = StringField('使用者名稱', validators=[DataRequired()])
    email = StringField('電子信箱', validators=[DataRequired(), Email()])
    social_link = StringField('個人公開 FB 或 IG 網址 (審核用)', validators=[
        DataRequired(message='必須填寫 FB 或 IG 社群網址供賣家審核！'),
        URL(message='請輸入有效的網址 (例如 https://facebook.com/yourid)')
    ])
    password = PasswordField('密碼', validators=[DataRequired()])
    password_confirm = PasswordField('確認密碼', validators=[
        DataRequired(),
        EqualTo('password', message='兩次輸入的密碼必須相同！')
    ])
    submit = SubmitField('註冊帳號')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('此使用者名稱已被使用！')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('此電子信箱已被註冊！')

class LoginForm(FlaskForm):
    username = StringField('使用者名稱', validators=[DataRequired()])
    password = PasswordField('密碼', validators=[DataRequired()])
    remember_me = BooleanField('記住我')
    submit = SubmitField('登入')

class ListingForm(FlaskForm):
    category = SelectField('交易類別', choices=[('ticket', '球票'), ('merch', '週邊商品')], default='ticket')
    team = SelectField('對戰/主場球隊', choices=TEAMS, validators=[DataRequired()])
    stadium = SelectField('比賽球場', choices=STADIUMS, validators=[DataRequired()])
    zone = StringField('座位區域 (例：內野 B 區 12 排 5 號)', validators=[DataRequired()])
    ticket_type = SelectField('票種', choices=TICKET_TYPES, default='全票')
    delivery_method = SelectField('給票方式', choices=DELIVERY_METHODS, default='中職官方APP轉贈')
    original_price = IntegerField('票面原價 (元)', validators=[
        DataRequired(),
        NumberRange(min=1, message='原價必須大於 0')
    ])
    price = IntegerField('擬售價格 (元)', validators=[
        DataRequired(),
        NumberRange(min=0, message='價格不得為負數')
    ])
    quantity = IntegerField('張數/數量', default=1, validators=[
        DataRequired(),
        NumberRange(min=1, max=10, message='數量需在 1 到 10 之間')
    ])
    ticket_image_url = StringField('票券/商品照片連結 (選填)', validators=[Optional(), URL()])
    submit = SubmitField('確認刊登待售票券')

    def validate_price(self, field):
        if self.original_price.data is not None and field.data > self.original_price.data:
            raise ValidationError(f'⚠️【防黃牛限制】轉售價格 (${field.data}) 不得高於票面原價 (${self.original_price.data})！')

class WantToBuyForm(FlaskForm):
    category = SelectField('需求類別', choices=[('ticket', '球票'), ('merch', '週邊商品')], default='ticket')
    team = SelectField('目標球隊', choices=TEAMS, validators=[DataRequired()])
    stadium = SelectField('目標球場', choices=STADIUMS, validators=[DataRequired()])
    zone = StringField('期望區域 (選填)', validators=[Optional()])
    max_price = IntegerField('最高可接受單價 (選填)', validators=[Optional(), NumberRange(min=0)])
    quantity = IntegerField('需求張數/數量', default=1, validators=[DataRequired(), NumberRange(min=1)])
    note = TextAreaField('補充說明 (例：希望能求連號)', validators=[Optional()])
    submit = SubmitField('發布徵票需求')

class OrderNoteForm(FlaskForm):
    note = TextAreaField('取票/面交/配送說明 (例如：APP 轉贈手機號碼、面交時間地點)', validators=[DataRequired()])
    submit = SubmitField('儲存說明')

class RatingForm(FlaskForm):
    score = SelectField('給予評分', choices=[(5, '5星 - 非常滿意'), (4, '4星 - 良好'), (3, '3星 - 普通'), (2, '2星 - 尚可'), (1, '1星 - 差勁')], coerce=int, default=5)
    is_default = BooleanField('對方是否有棄標 / 毀約不履約行為')
    comment = TextAreaField('交易評語', validators=[Optional()])
    submit = SubmitField('送出評價')
