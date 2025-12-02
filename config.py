import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "clave-super-secreta-cambia-esto"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///gis_salud.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
