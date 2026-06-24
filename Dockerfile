FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --upgrade pip setuptools wheel \
    && pip install --prefer-binary "akshare>=1.16.26" "httpx>=0.28.1" "mcp[cli]>=1.3.0"

COPY . .

CMD ["python", "start.py"]
