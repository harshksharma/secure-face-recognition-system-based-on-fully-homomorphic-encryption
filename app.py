from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import base64
import numpy as np
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
import cv2

# For images
from flask import Flask, send_from_directory

# Import our custom encryption/decryption modules
import encryption_method
import decryption_method

# Import face_recognition for faster face embedding
import face_recognition

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Consider using environment variables in production

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    enc_face = db.Column(db.LargeBinary, nullable=False)
    secret_key = db.Column(db.LargeBinary, nullable=False)
    public_key = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/image/<filename>')
def get_image(filename):
    return send_from_directory('static/images', filename)

def decode_image(base64_data):
    """Decodes a base64-encoded image string into a numpy array."""
    try:
        # base64_data is expected in the format "data:image/png;base64,AAA..."
        header, data = base64_data.split(',', 1)
        return np.frombuffer(base64.b64decode(data), np.uint8)
    except Exception as e:
        logging.error(f"Error decoding image: {e}")
        return None

def preprocess_and_save_image(image_array, username):
    """
    Preprocesses the image and saves it to a secure user folder.
    Returns the path to the saved image or None on error.
    """
    try:
        safe_username = secure_filename(username)
        user_folder = os.path.join('user_images', safe_username)
        os.makedirs(user_folder, exist_ok=True)
        img_path = os.path.join(user_folder, f"{safe_username}.png")

        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if img is None:
            logging.error("Failed to decode image array into an image.")
            return None
        # Resize to something smaller (e.g., 160x160) for speed
        resized_img = cv2.resize(img, (160, 160))
        cv2.imwrite(img_path, resized_img)

        return img_path
    except Exception as e:
        logging.error(f"Error processing and saving image: {e}")
        return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        image_data = request.form.get('image_data')

        if not username or not email or not image_data:
            flash("All fields are required!", "error")
            return redirect(url_for('signup'))

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash("User already exists. Try a different username.", "warning")
            return redirect(url_for('signup'))

        # Decode and preprocess the image
        img_array = decode_image(image_data)
        if img_array is None:
            flash("Invalid image data. Please try again.", "error")
            return redirect(url_for('signup'))

        img_path = preprocess_and_save_image(img_array, username)
        if not img_path:
            flash("Error saving the image. Please try again.", "error")
            return redirect(url_for('signup'))

        # ---- FACE RECOGNITION USING face_recognition ----
        try:
            # Load the image and extract face encodings
            loaded_image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(loaded_image)
            if len(encodings) == 0:
                flash("No face detected in the photo. Please try again.", "error")
                return redirect(url_for('signup'))

            face_vector = encodings[0]  # Use the first face found
        except Exception as e:
            logging.error(f"Error extracting face encoding: {e}")
            flash("Error extracting face encoding. Please try again.", "error")
            return redirect(url_for('signup'))

        # ---- ENCRYPT THE FACE VECTOR ----
        context = encryption_method.initialize_encryption_context()
        secret_context = context.serialize(save_secret_key=True)
        public_context = context.serialize()

        # Encrypt face vector
        enc_face_vector = encryption_method.encrypt_face_embedding(face_vector, context)

        # Save user data in the database
        new_user = User(
            username=username,
            email=email,
            enc_face=enc_face_vector,
            secret_key=secret_context,
            public_key=public_context
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! You can now login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        image_data = request.form.get('imageData')

        if not username or not email or not image_data:
            flash("All fields are required!", "error")
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        if not user:
            flash("User does not exist. Please sign up first.", "error")
            return redirect(url_for('login'))

        # Decode and preprocess the captured image
        img_array = decode_image(image_data)
        if img_array is None:
            flash("Invalid image data. Please try again.", "error")
            return redirect(url_for('login'))

        img_path = preprocess_and_save_image(img_array, username)
        if not img_path:
            flash("Error saving the image. Please try again.", "error")
            return redirect(url_for('login'))

        # ---- FACE RECOGNITION USING face_recognition ----
        try:
            loaded_image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(loaded_image)
            if len(encodings) == 0:
                flash("No face detected in the photo.", "error")
                return redirect(url_for('login'))

            face_vector_login = encodings[0]
        except Exception as e:
            logging.error(f"Error extracting face encoding during login: {e}")
            flash("Error in face recognition. Please try again.", "error")
            return redirect(url_for('login'))

        # ---- DECRYPT & COMPARE ----
        try:
            # Load encryption context from user's saved secret key
            context = decryption_method.load_encryption_context(user.secret_key)
            # Decrypt the stored encrypted face vector
            saved_face_vector = decryption_method.decrypt_face_vector(user.enc_face, context)

            # Encrypt the login face vector with the same context and decrypt it
            # (since we are doing a homomorphic approach, but we still need to compare in plain after decryption)
            login_enc_vector = encryption_method.encrypt_face_embedding(face_vector_login, context)
            login_enc_vector_obj = decryption_method.lazy_vector_from_bytes(login_enc_vector, context)
            login_face_vector_decrypted = login_enc_vector_obj.decrypt()

            # Compare face vectors
            match, distance = decryption_method.compare_face_vectors(saved_face_vector, login_face_vector_decrypted)
            if match:
                flash(f"Login successful! Distance={distance:.2f}", "success")
                return redirect(url_for('home'))
            else:
                flash(f"Login failed. Distance={distance:.2f} is above threshold.", "error")
        except Exception as e:
            logging.error(f"Error during login face vector comparison: {e}")
            flash("Error in face recognition. Please try again.", "error")

    return render_template('login.html')

if __name__ == '__main__':
    # For production, set debug=False and consider using a production server
    app.run(debug=True)
