# secure-face-recognition-system-based-on-fully-homomorphic-encryption

Here is a **README.md** file for your project. It includes a **project overview, setup instructions, usage details, and future improvements**, making it easy for others to understand and contribute.  

---

```markdown
# Secure Face Recognition with Fully Homomorphic Encryption

## 📌 Project Overview
This project implements a **secure face recognition authorization system** that leverages **fully homomorphic encryption (FHE)** to protect biometric data. The system uses **Flask** for the backend, **face_recognition** for face embeddings, and **TenSEAL** to encrypt and compare encrypted embeddings securely.

🔒 **Key Features:**
- **Secure Face Authentication:** Uses **face_recognition** to extract 128-dimensional face embeddings.
- **Fully Homomorphic Encryption:** Encrypts embeddings using **TenSEAL (CKKS scheme)** to ensure privacy.
- **Real-time Processing:** Optimized from **10s (DeepFace)** to **<2s** using **face_recognition**.
- **Modular Architecture:** Separate encryption/decryption logic for better maintainability.
- **Flask-Based Web App:** Easy-to-use web interface with **signup** and **login** authentication.
- **SQLite Database:** Stores encrypted face data and encryption keys securely.

---

## 📂 Project Structure
```
├── app.py               # Main Flask application (handles routes, database, image processing)
├── encryption_method.py # Encrypts face embeddings using TenSEAL
├── decryption_method.py # Decrypts and compares face embeddings
├── templates/           # HTML templates for signup and login pages
├── static/              # JavaScript and CSS files for frontend
├── user_images/         # Directory for storing user face images
├── requirements.txt     # List of dependencies
└── README.md            # Documentation file
```

---

## 🛠️ Setup Instructions
### 1️⃣ Prerequisites
Ensure you have **Python 3.8+** and the following libraries installed:
- Flask
- Flask-SQLAlchemy
- OpenCV (`opencv-python`)
- face_recognition
- TenSEAL
- NumPy

### 2️⃣ Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-repo/secure-face-recognition.git
cd secure-face-recognition
pip install -r requirements.txt
```

### 3️⃣ Run the Application
Start the Flask server:
```bash
python app.py
```
Open the browser and visit:  
➡️ `http://127.0.0.1:5000`

---

## 📸 How It Works
### ✅ **User Signup**
1. User captures an image via the webcam.
2. Image is processed using **OpenCV** (resized to **160×160** for efficiency).
3. **face_recognition** extracts a **128-dimensional face embedding**.
4. Embedding is **encrypted using TenSEAL (CKKS scheme)**.
5. **Encrypted embedding & keys** are stored securely in the database.
6. User can now log in using their face.

### ✅ **User Login**
1. User captures a new image.
2. The system **extracts & encrypts** the face embedding.
3. The stored **encrypted embedding is decrypted**.
4. **Comparison using Euclidean distance**:
   - ✅ **Match found → Login successful**
   - ❌ **No match → Access denied**

---

## 🔍 Performance & Security
| Feature                  | Initial (DeepFace) | Optimized (face_recognition) |
|--------------------------|-------------------|------------------------------|
| **Processing Time**      | ~10 sec           | **<2 sec**                   |
| **Encryption Method**    | AES (initial)     | **TenSEAL (FHE)**            |
| **User Experience**      | Slow              | **Fast & Responsive**        |

🔒 **Security Highlights:**
- **Face embeddings are never stored in plaintext.**
- **Encryption ensures user privacy even in case of data breaches.**
- **Flask’s secure session handling prevents CSRF attacks.**

---

## 🚀 Future Improvements
- **🔄 Migrate to Django:** Improve scalability and session handling.
- **🎭 Multi-Factor Authentication (MFA):** Add a second layer of security.
- **⚡ GPU Acceleration:** Speed up encryption and face recognition with CUDA.
- **📊 Admin Dashboard:** Add logs and user analytics.
- **📱 Mobile Support:** Develop an Android/iOS version.

---

## 📜 License
This project is licensed under the **MIT License**. Feel free to modify and contribute!

---

## 🤝 Contributing
Want to contribute? Follow these steps:
1. Fork the repo
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m "Add new feature"`)
4. Push and submit a **Pull Request (PR)**!
