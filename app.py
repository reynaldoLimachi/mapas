from flask import Flask, redirect, url_for
from config import Config
from models import db
from flask_login import LoginManager
from controllers.auth_controller import auth_bp
from controllers.map_controller import map_bp
from controllers.dashboard_controller import dashboard_bp

def create_app():
    # Crear la app con templates en /views y static en /static
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.config.from_object(Config)

    # Inicializar la base de datos
    db.init_app(app)

    # Inicializar Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "auth_bp.login"
    login_manager.init_app(app)

    # User loader para Flask-Login
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    # Registrar Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(map_bp, url_prefix="/map")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    # Ruta principal → redirige al mapa
    @app.route("/")
    def home():
        # Simplemente redirige a la ruta del blueprint map
        return redirect("/map/")

    return app

# Crear instancia de la app
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
