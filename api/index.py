# Nama File: api/index.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os
import random
import string
import datetime

# --- Inisialisasi Aplikasi dan Database ---
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


# --- Model Database (Struktur Tabel dalam bentuk Kode Python) ---
# Tidak ada perubahan di bagian Model, isinya tetap sama.

class Level(db.Model):
    __tablename__ = 'levels'
    id = db.Column(db.Integer, primary_key=True)
    level_name = db.Column(db.String(50), nullable=False, unique=True)
    profit_bonus_percentage = db.Column(db.Numeric(5, 2), default=0.00)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False, default=1)
    withdrawable_balance = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    active_investment_balance = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    referral_code = db.Column(db.String(15), nullable=False, unique=True)
    referred_by_code = db.Column(db.String(15), nullable=True)
    ip_address = db.Column(db.String(45))
    otp_code = db.Column(db.String(6))
    otp_expiration = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

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


# --- Fungsi Bantuan ---
def generate_random_code(length):
    """Fungsi untuk membuat kode acak (untuk referral dan OTP)."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# --- API Endpoints ---

@app.route('/')
def index():
    return "<h1>Backend API Indoinvsta Aktif! Modul User & Produk Siap.</h1>"

# === MODUL USER (dari langkah sebelumnya) ===

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    phone = data.get('phone_number')
    if not phone: return jsonify({'error': 'Nomor ponsel dibutuhkan'}), 400
    if User.query.filter_by(phone_number=phone).first(): return jsonify({'error': 'Nomor ponsel sudah terdaftar'}), 409
    otp = generate_random_code(6)
    ref_code = 'INV' + generate_random_code(7)
    new_user = User(
        phone_number=phone,
        referral_code=ref_code,
        otp_code=otp,
        otp_expiration=datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registrasi berhasil. Silakan verifikasi OTP.', 'otp_for_testing': otp }), 201

@app.route('/verify', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone_number')
    otp_submitted = data.get('otp_code')
    if not phone or not otp_submitted: return jsonify({'error': 'Nomor ponsel dan OTP dibutuhkan'}), 400
    user = User.query.filter_by(phone_number=phone).first()
    if not user: return jsonify({'error': 'Pengguna tidak ditemukan'}), 404
    if datetime.datetime.utcnow() > user.otp_expiration: return jsonify({'error': 'Kode OTP sudah kedaluwarsa'}), 400
    if user.otp_code != otp_submitted: return jsonify({'error': 'Kode OTP salah'}), 400
    user.otp_code = None
    db.session.commit()
    return jsonify({'message': 'Verifikasi berhasil! Akun Anda sudah aktif.'}), 200

# === MODUL PRODUK (KODE BARU) ===

@app.route('/products', methods=['POST', 'GET'])
def handle_products():
    # --- Pintu untuk ADMIN (Menambahkan produk baru) ---
    if request.method == 'POST':
        data = request.get_json()
        
        # Validasi sederhana untuk memastikan data yang dikirim lengkap
        required_fields = ['product_name', 'level_id', 'price', 'profit_percentage', 'duration_days']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Data yang dikirim tidak lengkap'}), 400

        new_product = Product(
            product_name=data['product_name'],
            level_id=data['level_id'],
            price=data['price'],
            profit_percentage=data['profit_percentage'],
            duration_days=data['duration_days'],
            logo_url=data.get('logo_url'), # Menggunakan .get() untuk data opsional
            promotes_to_level_id=data.get('promotes_to_level_id')
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({'message': f"Produk '{data['product_name']}' berhasil ditambahkan."}), 201

    # --- Pintu untuk PENGGUNA (Melihat semua produk) ---
    if request.method == 'GET':
        products = Product.query.filter_by(is_active=True).all()
        
        # Mengubah data produk dari objek menjadi format JSON yang mudah dibaca
        output = []
        for product in products:
            product_data = {
                'id': product.id,
                'product_name': product.product_name,
                'level_id': product.level_id,
                'price': str(product.price), # diubah ke string agar tidak ada masalah format
                'profit_percentage': product.profit_percentage,
                'duration_days': product.duration_days,
                'logo_url': product.logo_url
            }
            output.append(product_data)
            
        return jsonify({'products': output}), 200
