# Utiliser une image de base Raspberry Pi compatible
FROM balenalib/raspberrypi4-64-debian:latest

# Installer les dépendances système et les bibliothèques spécifiques Raspberry Pi
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libatlas-base-dev \
    libjpeg-dev \
    libopencv-dev \
    libopenblas-dev \
    liblapack-dev \
    ffmpeg \
    libraspberrypi-bin \
    libraspberrypi-dev \
    libraspberrypi0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Définir pip3 comme pip par défaut
RUN [ ! -e /usr/bin/pip ] || rm /usr/bin/pip && ln -s /usr/bin/pip3 /usr/bin/pip

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Définir le répertoire de travail
WORKDIR /app

# Copier le script Python et le modèle dans l'image
COPY testvideo.py /app/testvideo.py
COPY best2.onnx /app/best2.onnx

# Exposer le port utilisé par Flask
EXPOSE 5000

# Commande pour exécuter l'application
CMD ["python3", "testvideo.py"]
