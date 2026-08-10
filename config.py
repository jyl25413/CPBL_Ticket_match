import os

basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
os.makedirs(instance_dir, exist_ok=True)

# Ensure forward slashes for SQLite URI across all platforms (especially Windows)
db_path = os.path.join(instance_dir, 'cpbl_tickets.db').replace('\\', '/')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cpbl-ticketing-secret-key-2026-mvp'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
