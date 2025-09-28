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
# Kita tambahkan beberapa kolom baru di model User untuk sistem OTP

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
    otp_code = db.Column(db.String(6)) # Kolom baru untuk menyimpan OTP
    otp_expiration = db.Column(db.DateTime) # Kolom baru untuk waktu kedaluwarsa OTP
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    # (Isi model Product tetap sama seperti sebelumnya, tidak perlu diubah)
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    # ... (dan seterusnya)


# --- Fungsi Bantuan ---
def generate_random_code(length):
    """Fungsi untuk membuat kode acak (untuk referral dan OTP)."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# --- API Endpoints ---

@app.route('/')
def index():
    return "<h1>Backend API Indoinvsta Aktif! Modul User Siap.</h1>"

# Endpoint untuk memulai proses registrasi
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    phone = data.get('phone_number')

    if not phone:
        return jsonify({'error': 'Nomor ponsel dibutuhkan'}), 400

    # Cek apakah nomor sudah terdaftar
    if User.query.filter_by(phone_number=phone).first():
        return jsonify({'error': 'Nomor ponsel sudah terdaftar'}), 409

    # Buat OTP dan referral code
    otp = generate_random_code(6)
    ref_code = 'INV' + generate_random_code(7)
    
    new_user = User(
        phone_number=phone,
        referral_code=ref_code,
        otp_code=otp,
        otp_expiration=datetime.datetime.utcnow() + datetime.timedelta(minutes=5) # OTP valid 5 menit
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # PENTING: Di aplikasi nyata, baris berikutnya akan diganti dengan pengiriman SMS.
    # Untuk sekarang, kita tampilkan OTP-nya agar bisa diuji.
    return jsonify({
        'message': 'Registrasi berhasil. Silakan verifikasi OTP.',
        'otp_for_testing': otp 
    }), 201

# Endpoint untuk verifikasi OTP
@app.route('/verify', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone_number')
    otp_submitted = data.get('otp_code')

    if not phone or not otp_submitted:
        return jsonify({'error': 'Nomor ponsel dan OTP dibutuhkan'}), 400

    user = User.query.filter_by(phone_number=phone).first()

    if not user:
        return jsonify({'error': 'Pengguna tidak ditemukan'}), 404
        
    # Cek apakah OTP sudah kedaluwarsa
    if datetime.datetime.utcnow() > user.otp_expiration:
        return jsonify({'error': 'Kode OTP sudah kedaluwarsa'}), 400
        
    # Cek apakah OTP benar
    if user.otp_code != otp_submitted:
        return jsonify({'error': 'Kode OTP salah'}), 400

    # Jika berhasil
    user.otp_code = None # Hapus OTP setelah berhasil digunakan
    db.session.commit()
    
    return jsonify({'message': 'Verifikasi berhasil! Akun Anda sudah aktif.'}), 200
