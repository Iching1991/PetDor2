# PETdor2/backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Expõe porta
EXPOSE 8501

# Comando para iniciar
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
