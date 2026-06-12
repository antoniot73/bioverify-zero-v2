FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV BIOVERIFY_PROJECT_ROOT=/opt/bioverify-zero

WORKDIR /opt/bioverify-zero

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY frontend ./frontend
COPY models ./models
COPY scripts ./scripts

RUN python scripts/download_models.py

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /opt/bioverify-zero

USER appuser

EXPOSE 7860

CMD ["sh", "-c", "echo 'Starting BioVerify-Zero v2 on port 7860...' && python -m uvicorn app.main:app --host 0.0.0.0 --port 7860"]
