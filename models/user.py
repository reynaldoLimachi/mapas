from models import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):  # <- Agrega UserMixin
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)