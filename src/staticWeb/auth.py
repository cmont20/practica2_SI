from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from src.database.database import create_user, authenticate_user

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Clase User para Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    # Almacena id, username en session
    return User(user_id, None)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if create_user(user, pw):
            flash('Usuario creado con éxito. Por favor, inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('El nombre de usuario ya existe.', 'danger')
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        auth = authenticate_user(user, pw)
        if auth:
            user_obj = User(auth['id'], auth['username'])
            login_user(user_obj)
            flash('Sesión iniciada.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))