
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load .env if present (for SECRET_KEY and DATABASE_URL)
load_dotenv()

app = Flask(__name__)

# Sensitive config via environment variables (never hardcode!)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-do-not-use-in-prod")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")  # "user" or "admin"

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)  # pbkdf2:sha256

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Inicia sesión para continuar.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_role" not in session:
                flash("No autorizado. Inicia sesión.", "danger")
                return redirect(url_for("login"))
            if session.get("user_role") not in roles:
                flash("No tienes permisos para acceder a esta página.", "danger")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/")
def home():
    return render_template("home.html", user_role=session.get("user_role"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "user")
        if not username or not password:
            flash("Usuario y contraseña son obligatorios.", "warning")
            return redirect(url_for("register"))
        if User.query.filter_by(username=username).first():
            flash("El usuario ya existe.", "danger")
            return redirect(url_for("register"))
        u = User(username=username, role=role if role in ("user","admin") else "user")
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash("Registro exitoso. Ahora inicia sesión.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Credenciales inválidas.", "danger")
            return redirect(url_for("login"))
        # Authentication success -> create session
        session["user_id"] = user.id
        session["user_role"] = user.role
        flash(f"Bienvenido, {user.username}. Autenticación OK.", "success")
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    # Example protected page: authentication required
    return render_template("dashboard.html", user_role=session.get("user_role"))

@app.route("/admin")
@login_required
@role_required("admin")
def admin():
    # Example of authorization by role
    users = User.query.order_by(User.username).all()
    return render_template("admin.html", users=users)

@app.cli.command("init-db")
def init_db():
    """Flask CLI: flask init-db -> creates tables and a default admin"""
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin creado: usuario=admin, contraseña=admin123")
    print("Base lista.")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
