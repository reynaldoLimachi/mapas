from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import User
from models import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

# Blueprint
auth_bp = Blueprint("auth_bp", __name__, template_folder="../views/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Si ya está logueado, redirige al mapa
    if current_user.is_authenticated:
        return redirect(url_for("map_bp.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)  # Flask-Login
            flash(f"Bienvenido {user.nombre}", "success")
            return redirect(url_for("map_bp.index"))
        else:
            flash("Usuario o contraseña incorrecta", "danger")
            return render_template("login.html")

    # GET → mostrar formulario login
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # Si ya está logueado, redirige al mapa
    if current_user.is_authenticated:
        login_user(user)
        return redirect(url_for("map_bp.index"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        # Validaciones básicas
        if not nombre or not email or not password or not confirm_password:
            flash("Todos los campos son obligatorios", "warning")
            return render_template("register.html")

        if password != confirm_password:
            flash("Las contraseñas no coinciden", "warning")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("El email ya está registrado", "warning")
            return render_template("register.html")

        # Crear usuario
        hashed = generate_password_hash(password)
        nuevo = User(nombre=nombre, email=email, password=hashed)
        db.session.add(nuevo)
        db.session.commit()

        flash("Registro exitoso. Inicia sesión.", "success")
        return redirect(url_for("auth_bp.login"))

    # GET → mostrar formulario registro
    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente", "info")
    return redirect(url_for("auth_bp.login"))
