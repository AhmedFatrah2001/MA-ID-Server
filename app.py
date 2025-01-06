from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
from userOperations import create_user, get_user_by_id, get_user_by_credentials
from werkzeug.security import generate_password_hash
import os
import random
import smtplib
from email.mime.text import MIMEText
import numpy as np
import cv2
from zone_detector import ZoneDetector
from text_extractor import OCRProcessor
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "123456789")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

app = Flask(__name__)

# Store OTPs in memory (use a database in production)
user_otps = {}

zone_detector = ZoneDetector()
ocr_processor = OCRProcessor()

# Helper function to send OTP email
def send_otp_email(email, otp):
    try:
        msg = MIMEText(f"Your OTP is: {otp}")
        msg['Subject'] = 'Your OTP Code'
        msg['From'] = EMAIL_USER
        msg['To'] = email

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, email, msg.as_string())
        print("OTP email sent successfully.")
    except Exception as e:
        print(f"Failed to send OTP email: {e}")

# JWT Token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("x-access-token")

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = get_user_by_id(data["user_id"])
            if not current_user:
                raise Exception("User not found")
        except Exception as e:
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "All fields are required!"}), 400

    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    try:
        create_user(username, email, password)
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        return jsonify({"message": "Error registering user", "error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('identifier') or not data.get('password'):
        return jsonify({"message": "Identifier (username or email) and password are required!"}), 400

    identifier = data['identifier']
    password = data['password']

    user = get_user_by_credentials(identifier, password)
    if not user:
        return jsonify({"message": "Invalid username/email or password"}), 401

    otp = random.randint(100000, 999999)
    user_otps[user['id']] = otp
    send_otp_email(user['email'], otp)

    return jsonify({"message": "OTP sent to your email."})

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()

    if not data or not data.get('identifier') or not data.get('otp'):
        return jsonify({"message": "Identifier (username or email) and OTP are required!"}), 400

    identifier = data['identifier']
    otp = int(data['otp'])

    # Find the user using their identifier
    user = None
    for user_id, user_otp in user_otps.items():
        if user_otp == otp:
            user = get_user_by_id(user_id)
            if user and (user['username'] == identifier or user['email'] == identifier):
                break

    if not user:
        return jsonify({"message": "Invalid identifier or OTP!"}), 401

    del user_otps[user['id']]  # Remove OTP after successful verification

    token = jwt.encode({
        "user_id": user['id'],
        "username": user['username'],
        "email": user['email'],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "message": "Login successful!",
        "token": token
    })


@app.route('/scan', methods=['POST'])
@token_required
def scan(current_user):
    # Check if an image file is in the request
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    # Read the image from the request
    file = request.files['image']
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({"error": "Invalid image file"}), 400

    # Detect zones
    detected_zones = zone_detector.detect_zones(image)

    # Perform OCR on detected zones
    ocr_results = ocr_processor.extract_text_from_zones(image, detected_zones)

    # Return the OCR results as JSON
    return jsonify({"ocr_results": ocr_results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
