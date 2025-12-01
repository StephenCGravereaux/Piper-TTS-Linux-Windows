# Ollama + Piper TTS Chatbot Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio (optional, for container audio playback)
RUN apt-get update && apt-get install -y --no-install-recommends \
    alsa-utils \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY chatbot.py .
COPY voices/ ./voices/

# Set environment variables
ENV PYTHONUNBUFFERED=1
# Default Ollama URL - points to host machine from container
ENV OLLAMA_URL=http://host.docker.internal:11434

# Create a non-root user for security
RUN useradd -m -u 1000 chatbot
USER chatbot

# Default command
CMD ["python", "chatbot.py", "--url", "http://host.docker.internal:11434"]

