from flask import Blueprint, render_template, jsonify, request
from flask_login import current_user
from models.centers import Center
from models.search_history import SearchHistory
from models import db
import json
import requests
from datetime import datetime

# Blueprint
#map_bp = Blueprint("map", __name__)
map_bp = Blueprint("map_bp", __name__, template_folder="../views/map")

# Página principal del mapa
@map_bp.route("/")
def index():
    return render_template("index.html")


# API: obtener todos los centros
@map_bp.route("/api/centers")
def api_centers():
    centers = Center.query.all()
    data = [
        {
            "id": c.id,
            "nombre": c.nombre,
            "tipo": c.tipo,
            "lat": c.lat,
            "lon": c.lon,
            "direccion": c.direccion
        }
        for c in centers
    ]
    return jsonify(data)


# API: búsqueda filtrada
@map_bp.route("/api/search")
def api_search():
    name = request.args.get("name", "").strip()
    tipos = request.args.get("tipos", "").strip()  # "hospital,centro"
    query = Center.query

    if name:
        like = f"%{name}%"
        query = query.filter(Center.nombre.ilike(like))

    if tipos:
        tipos_list = [t.strip() for t in tipos.split(",") if t.strip()]
        if tipos_list:
            query = query.filter(Center.tipo.in_(tipos_list))

    results = query.all()
    data = [
        {
            "id": c.id,
            "nombre": c.nombre,
            "tipo": c.tipo,
            "lat": c.lat,
            "lon": c.lon,
            "direccion": c.direccion
        } for c in results
    ]
    return jsonify(data)


# API: registrar búsqueda en historial
@map_bp.route("/api/record_search", methods=["POST"])
def api_record_search():
    data = request.get_json() or {}
    user_id = current_user.id if current_user.is_authenticated else None

    sh = SearchHistory(
        user_id=user_id,
        center_id=data.get("center_id"),
        query=data.get("query"),
        filtros=json.dumps(data.get("filtros")) if data.get("filtros") else None,
        distancia=data.get("distancia"),
        duracion=data.get("duracion"),
        ruta=json.dumps(data.get("ruta")) if data.get("ruta") else None,
        fecha=datetime.utcnow()
    )
    db.session.add(sh)
    db.session.commit()
    return jsonify({"ok": True, "id": sh.id})


# API: calcular ruta con OSRM
@map_bp.route("/api/ruta", methods=["POST"])
def api_ruta():
    """
    Recibe JSON:
      {
        "start": [lat, lon],
        "end": [lat, lon],
        "hospital": "Nombre Hospital",
        "center_id": 12
      }
    Devuelve la ruta más corta usando OSRM y registra historial.
    """
    data = request.get_json() or {}
    start = data.get("start")   # [lat, lon]
    end = data.get("end")       # [lat, lon]
    center_id = data.get("center_id")

    if not start or not end:
        return jsonify({"error": "start y end requeridos"}), 400

    # Construir URL OSRM: lon,lat;lon,lat
    osrm_url = f"https://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson&alternatives=false&steps=false"

    try:
        resp = requests.get(osrm_url, timeout=10)
        osrm = resp.json()
    except Exception as e:
        return jsonify({"error": "Error llamando a OSRM", "detail": str(e)}), 500

    # Extraer distancia y duración
    distancia = None
    duracion = None
    if "routes" in osrm and len(osrm["routes"]) > 0:
        r = osrm["routes"][0]
        distancia = r.get("distance")  # metros
        duracion = r.get("duration")   # segundos

    # Guardar historial
    user_id = current_user.id if current_user.is_authenticated else None
    sh = SearchHistory(
        user_id=user_id,
        center_id=center_id,
        fecha=datetime.utcnow(),
        distancia=(distancia/1000.0) if distancia else None,  # km
        duracion=(duracion/60.0) if duracion else None,       # minutos
        ruta=json.dumps(osrm),
        query=None,
        filtros=None
    )
    db.session.add(sh)
    db.session.commit()

    return jsonify(osrm)
