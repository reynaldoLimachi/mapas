from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.centers import Center
from models.user import User
from models import db

dashboard_bp = Blueprint("dashboard_bp", __name__, template_folder="../views/dashboard")

# Página principal del dashboard
@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    # Obtener datos de centros y usuarios
    centros = Center.query.order_by(Center.id.asc()).all()  # orden ascendente
    usuarios = User.query.all()

    # Calcular estadísticas
    estadisticas = {
        "hospitales": Center.query.filter_by(tipo="hospital").count(),
        "centros": Center.query.filter_by(tipo="centro").count(),
        "postas": Center.query.filter_by(tipo="posta").count(),
        "usuarios": len(usuarios)
    }

    # Pasar todo al template
    return render_template(
        "dashboard/index.html",
        centros=centros,
        usuarios=usuarios,
        estadisticas=estadisticas
    )


# Registrar nuevo centro
@dashboard_bp.route("/registrar_centro", methods=["POST"])
@login_required
def registrar_centro():
    nombre = request.form.get("nombre", "").strip()
    tipo = request.form.get("tipo", "").strip()
    direccion = request.form.get("direccion", "").strip()
    lat = request.form.get("lat", "").strip()
    lon = request.form.get("lon", "").strip()

    # Validaciones básicas
    if not nombre or not tipo or not lat or not lon:
        flash("Todos los campos son obligatorios.", "warning")
        return redirect(url_for("dashboard_bp.index"))

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        flash("Latitud y longitud deben ser números válidos.", "warning")
        return redirect(url_for("dashboard_bp.index"))

    # Crear y guardar el nuevo centro
    nuevo_centro = Center(nombre=nombre, tipo=tipo, direccion=direccion, lat=lat, lon=lon)
    db.session.add(nuevo_centro)
    db.session.commit()
    flash(f"Centro '{nombre}' registrado correctamente.", "success")
    return redirect(url_for("dashboard_bp.index"))

# =====================================================================
# Mostrar formulario de edición de un centro
@dashboard_bp.route("/editar_centro/<int:id>", methods=["GET", "POST"])
@login_required
def editar_centro(id):
    centro = Center.query.get_or_404(id)

    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.form.get("nombre", "").strip()
        tipo = request.form.get("tipo", "").strip()
        direccion = request.form.get("direccion", "").strip()
        lat = request.form.get("lat", "").strip()
        lon = request.form.get("lon", "").strip()

        # Validaciones básicas
        if not nombre or not tipo or not lat or not lon:
            flash("Todos los campos son obligatorios.", "warning")
            return redirect(url_for("dashboard_bp.editar_centro", id=id))

        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            flash("Latitud y longitud deben ser números válidos.", "warning")
            return redirect(url_for("dashboard_bp.editar_centro", id=id))

        # Actualizar datos del centro
        centro.nombre = nombre
        centro.tipo = tipo
        centro.direccion = direccion
        centro.lat = lat
        centro.lon = lon

        db.session.commit()
        flash(f"Centro '{nombre}' actualizado correctamente.", "success")
        return redirect(url_for("dashboard_bp.index"))        

    # GET → mostrar formulario de edición con datos actuales
    return render_template("dashboard/editar_centro.html", centro=centro)

# =====================================================================
# Eliminar un centro de salud
@dashboard_bp.route("/eliminar_centro/<int:id>", methods=["POST"])
@login_required
def eliminar_centro(id):
    centro = Center.query.get_or_404(id)

    try:
        db.session.delete(centro)
        db.session.commit()
        flash(f"Centro '{centro.nombre}' eliminado correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar el centro.", "danger")

    return redirect(url_for("dashboard_bp.index"))


