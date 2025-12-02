from models import db

class Center(db.Model):
    __tablename__ = "centers"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # hospital / centro / posta
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    direccion = db.Column(db.String(300), nullable=True)
