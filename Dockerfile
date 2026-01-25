FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Download speaker embedding model (sherpa-onnx CAM++)
RUN mkdir -p models && \
    curl -L -o models/3dspeaker_speech_campplus_sv_en_voxceleb_16k.onnx \
    https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/3dspeaker_speech_campplus_sv_en_voxceleb_16k.onnx

# Pre-download Whisper model to avoid loading delay at runtime
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')"

CMD ["python", "main.py"]
