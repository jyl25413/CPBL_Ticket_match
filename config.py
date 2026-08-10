import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cpbl-ticketing-secret-key-2026-mvp'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cpbl_tickets.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
