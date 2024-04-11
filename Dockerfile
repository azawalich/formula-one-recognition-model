FROM python:3.12.2-bookworm
WORKDIR /app/
ARG ROBOFLOW_API_KEY
ADD requirements /tmp
COPY assets /app/assets
COPY static /app/static
COPY templates /app/templates
ADD main.py /app
RUN apt update && apt upgrade -y \
  && apt install -y $(cat /tmp/apt) \
  && python -m pip install --no-cache-dir $(echo `cat /tmp/python`)
ENTRYPOINT ["python", "-m", "main.py", "--minio-url", "$MINIO_URL", , "--access-key", "$MINIO_ACCESS_KEY", "--secret-key", "$MINIO_SECRET_KEY", "--roboflow-api-key", "$ROBOFLOW_API_KEY"]