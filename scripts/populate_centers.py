from app import app
from models import db
from models.centers import Center

with app.app_context():
    db.drop_all()
    db.create_all()

    centers = [
        {"nombre":"Hospital Municipal La Paz", "tipo":"hospital", "lat":-16.5000, "lon":-68.1500, "direccion":"Av. Principal 1"},
        {"nombre":"Centro de Salud Cotahuma", "tipo":"centro", "lat":-16.5120, "lon":-68.1560, "direccion":"Calle 5"},
        {"nombre":"Posta San Miguel", "tipo":"posta", "lat":-16.5200, "lon":-68.1450, "direccion":"Calle 10"},
    ]
    for c in centers:
        center = Center(nombre=c["nombre"], tipo=c["tipo"], lat=c["lat"], lon=c["lon"], direccion=c["direccion"])
        db.session.add(center)
    db.session.commit()
    print("Centros poblados.")
