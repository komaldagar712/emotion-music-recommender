from flask import Flask, render_template, request, jsonify, session, redirect
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import base64

app = Flask(__name__)
app.secret_key = "secret123"

# Load model
# TEMP FAKE MODEL (for deployment demo)
def predict_emotion(face):
    import random
    emotions = ["Happy", "Sad", "Angry", "Surprise", "Neutral"]
    return random.choice(emotions), 90

emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

ADMIN_PASSWORD = "admin123"

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- DETECT ----------------
@app.route('/detect', methods=['POST'])
def detect():
    try:
        data = request.get_json()
        image_data = data['image']

        # Decode image
        image_data = image_data.split(',')[1]
        image = base64.b64decode(image_data)

        np_arr = np.frombuffer(image, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Improve lighting
        gray = cv2.equalizeHist(gray)

        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Load face detector
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        if face_cascade.empty():
            return jsonify({'emotion': 'Error loading model', 'songs': []})

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(20, 20)
        )

        print("Faces detected:", len(faces))

        if len(faces) == 0:
            return jsonify({
                'emotion': 'No face detected',
                'songs': []
            })

        # Take first face
        x, y, w, h = faces[0]
        face = gray[y:y+h, x:x+w]

        # Resize properly
        face = cv2.resize(face, (48, 48))
        face = face / 255.0
        face = np.reshape(face, (1, 48, 48, 1))

        # Predict
        prediction = model.predict(face)
        emotion_index = np.argmax(prediction)
        emotion = emotion_labels[emotion_index]

        confidence = round(float(np.max(prediction)) * 100, 2)

        # Songs
        songs = {
            "Happy": ["Shape of You", "Kala Chashma", "Uptown Funk", "Happy - Pharrell", "Good Time", "On Top of the World"],
            "Sad": ["Let Her Go", "Channa Mereya", "Someone Like You", "Fix You", "Hurt", "All I Want"],
            "Angry": ["Believer", "Animals", "Lose Yourself", "Stronger", "Numb", "In The End"],
            "Surprise": ["On Top of the World", "Good Time", "Happy", "Firework", "Counting Stars", "Best Day"],
            "Neutral": ["Perfect", "Raabta", "Counting Stars", "Let Me Down Slowly", "Stay", "Memories"],
            "Fear": ["Demons", "Fix You", "Boulevard of Broken Dreams", "Creep", "Unsteady", "Control"],
            "Disgust": ["Numb", "Faded", "In The End", "Believer", "Enemy", "Thunder"]
        }

        return jsonify({
            'emotion': f"{emotion} ({confidence}%)",
            'songs': songs.get(emotion, [])
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            'emotion': 'Error occurred',
            'songs': []
        })


# ---------------- ABOUT ----------------
@app.route('/about')
def about():
    return render_template('about.html')


# ---------------- ADMIN LOGIN ----------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')

        if password == "1234":   # 👈 apna password
            session['admin'] = True
            return redirect('/admin')

        return render_template('admin_login.html', error="Wrong Password")

    return render_template('admin_login.html')
# ---------------- ADMIN ----------------
@app.route('/admin')
def admin():
    print("SESSION:", session.get('admin'))  # 👈 ADD THIS
    if not session.get('admin'):
        return redirect('/admin_login')
    return render_template('admin.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)