from flask import Flask, Response
import subprocess
from PIL import Image
import io
import time

app = Flask(__name__)

def capture_image():
    """Capture une image en utilisant fswebcam et la retourne en tant qu'objet PIL.Image."""
    image_path = "capture.jpg"
    subprocess.run(["fswebcam", "-r", "352x288", "--no-banner", image_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Image.open(image_path)

def gen():
    while True:
        # Capture une image
        image = capture_image()

        # Convertit l'image en bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        frame = img_byte_arr.getvalue()

        # Envoie l'image sous forme de flux
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        # Ajout d'une petite pause pour ajuster la fréquence
        time.sleep(0.01)  # 0.1 secondes = 10 images par seconde (ajustable)

@app.route('/video_feed')
def video_feed():
    """Route pour le flux vidéo."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Page principale pour afficher le flux vidéo."""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Retour Vidéo</title>
    </head>
    <body>
        <h1>Flux Vidéo depuis la Raspberry Pi</h1>
        <img src="/video_feed" width="640" height="480" />
    </body>
    </html>
    '''

if __name__ == '__main__':
    # Démarrer le serveur Flask
    app.run(host='0.0.0.0', port=5000, debug=False)
