from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

# --- Inisialisasi Aplikasi dan Database ---
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


# --- Model Database (Struktur Tabel dalam bentuk Kode Python) ---
class Level(db.Model):
    __tablename__ = 'levels'
    id = db.Column(db.Integer, primary_key=True)
    level_name = db.Column(db.String(50), nullable=False, unique=True)
    profit_bonus_percentage = db.Column(db.Numeric(5, 2), default=0.00)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    price = db.Column(db.Numeric(15, 2), nullable=False)
    profit_percentage = db.Column(db.Integer, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    logo_url = db.Column(db.String(255))
    promotes_to_level_id = db.Column(db.Integer, db.ForeignKey('levels.id'))
    is_active = db.Column(db.Boolean, default=True)


# --- API Endpoint (URL yang bisa diakses) ---
@app.route('/')
def index():
    return "<h1>Backend API Indoinvsta Aktif!</h1>"

# (Endpoint untuk fitur-fitur lain akan kita tambahkan di sini nanti)
