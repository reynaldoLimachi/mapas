from models import db
from datetime import datetime
import json

class SearchHistory(db.Model):
    __tablename__ = "search_history"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)   # puede ser null si no logueado
    center_id = db.Column(db.Integer, nullable=True) # id del centro si se seleccionó
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    distancia = db.Column(db.Float, nullable=True)
    duracion = db.Column(db.Float, nullable=True)
    ruta = db.Column(db.Text, nullable=True)         # JSON guardado como texto
    query = db.Column(db.String(300), nullable=True) # texto buscado
    filtros = db.Column(db.Text, nullable=True)      # JSON con filtros aplicados
