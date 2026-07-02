FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    IQCARDS_DATA_DIR=/app/data \
    IQCARDS_IMPORT_DIR=/app/import

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY iq_cards ./iq_cards
COPY import ./import

EXPOSE 8000

CMD ["python", "-m", "iq_cards", "--host", "0.0.0.0", "--port", "8000", "--no-browser"]
