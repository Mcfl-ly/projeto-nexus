FROM node:24-bookworm-slim AS frontend
WORKDIR /build
COPY front/nexus/package*.json ./
RUN npm ci
COPY front/nexus/ ./
RUN npm run build

FROM python:3.15-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY ["api routes/requirements.txt", "/app/requirements.txt"]
RUN pip install --no-cache-dir -r requirements.txt
COPY ["api routes/", "/app/api routes/"]
COPY originais/ /app/originais/
COPY --from=frontend /build/dist /app/front/nexus/dist
RUN useradd --create-home nexus
USER nexus
WORKDIR /app/api routes
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
