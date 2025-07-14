# 🐍 Dockerfile: Django OCR App (Development)

FROM python:3.12-slim

# 🛠️ Install system dependencies (OCR & image processing)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ⚙️ Environment configuration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=doc_processor.settings

# 👤 Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# 📂 Set working directory
WORKDIR /app

# 📦 Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 📥 Copy project source code
COPY . .

# 📁 Create runtime directories
RUN mkdir -p /app/chroma_db /app/static /app/media /app/ocr-cache && \
    chown -R app:app /app

# 👤 Switch to non-root user
USER app

# 🌐 Expose application port
EXPOSE 8000

# ❤️ Healthcheck (basic app availability)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000', timeout=10)"

# 🚀 Default: Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
