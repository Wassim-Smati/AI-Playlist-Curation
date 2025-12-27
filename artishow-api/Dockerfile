# On s'aligne sur ta version locale exacte
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# On installe TensorFlow CPU (la dernière version va s'installer, donc la 2.19 comme toi)
RUN pip install --no-cache-dir --default-timeout=100 tensorflow-cpu

# On installe le reste
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# On copie le code
COPY . .

# PLUS DE VARIABLE D'ENVIRONNEMENT LEGACY ICI !
# On laisse Keras 3 faire son travail.

EXPOSE 7860
CMD ["python", "api.py"] 