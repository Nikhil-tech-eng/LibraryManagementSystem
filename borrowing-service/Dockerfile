# ---- builder stage ----
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip --no-cache-dir && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# ---- runtime stage ----
FROM python:3.12-slim AS runtime

RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/false -M appuser

WORKDIR /app

COPY --from=builder /venv /venv
COPY app/ ./app/

ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5003/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5003"]
