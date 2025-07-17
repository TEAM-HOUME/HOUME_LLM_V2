# Stage 1: 빌드 & 의존성 설치
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libffi-dev \
    curl \
    poppler-utils \
 && pip install --upgrade pip setuptools wheel cython build \
 && pip install numpy \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get purge -y --auto-remove \
    build-essential \
    gcc \
    libpq-dev \
    libffi-dev \
 && rm -rf /var/lib/apt/lists/*


# Stage 2: 실행 환경용 경량 이미지
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
