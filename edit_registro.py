# edit_registro.py
from app import app, db
from models.user import User  # Importa el modelo desde el archivo correcto

usuario_id = 2

with app.app_context():
    usuario = User.query.get(usuario_id)
    
    if usuario:
        usuario.nombre = "Maria Quispe Lopez"
        db.session.commit()
        print(f"Usuario con ID {usuario_id} actualizado correctamente.")
    else:
        print(f"No se encontró ningún usuario con ID {usuario_id}.")
