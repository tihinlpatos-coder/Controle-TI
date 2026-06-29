import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "hinl2026")

    DATABASE_URL = os.getenv("DATABASE_URL")

    DEBUG = False
