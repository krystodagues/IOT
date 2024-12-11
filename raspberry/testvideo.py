from flask import Flask, Response
from picamera import PiCamera
import time
import onnxruntime as ort
import numpy as np
from PIL import Image
import io

app = Flask(__name__)
camera = PiCamera()

camera.resolution = (640, 480)
camera.rotation = 0

model_path = "best2.onnx"
session = ort.InferenceSession(model_path)
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name


def preprocess(image):
    """Prétraiter l'image pour l'entrée du modèle ONNX."""
    image_array = np.array(image).astype(np.float32)

    image_array = image_array / 255.0

    image_array = np.transpose(image_array, (2, 0, 1))
    image_array = np.expand_dims(image_array, axis=0)
    return image_array


def infer(image):
    input_tensor = preprocess(image)
    result = session.run([output_name], {input_name: input_tensor})
    return result[0]


def gen():
    while True:
        # Capture une image dans un flux
        stream = io.BytesIO()
        camera.capture(stream, format='jpeg')
        stream.seek(0)
        image = Image.open(stream)

        result = infer(image)
        prediction = np.argmax(result)  # Modifier en fonction des résultats du modèle

        image_editable = image.copy()
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image_editable)
        font = ImageFont.load_default()
        draw.text((10, 10), f"Prédiction : {prediction}", fill="red", font=font)

        img_byte_arr = io.BytesIO()
        image_editable.save(img_byte_arr, format='JPEG')
        frame = img_byte_arr.getvalue()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Route pour le flux vidéo avec prédictions."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Page principale pour afficher le flux vidéo."""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Retour Vidéo avec Prédictions</title>
    </head>
    <body>
        <h1>Flux Vidéo avec Prédictions depuis la Raspberry Pi</h1>
        <img src="/video_feed" width="640" height="480" />
    </body>
    </html>
    '''


if __name__ == '__main__':
    # Démarrer le serveur Flask
    try:
        camera.start_preview()
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        camera.stop_preview()
        camera.close()
