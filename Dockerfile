FROM python:3.12.2-bookworm
WORKDIR /app/
ADD requirements /tmp
COPY assets /app/assets
COPY static /app/static
COPY templates /app/templates
ADD main.py /app
RUN apt update && apt upgrade -y \
  && apt install -y $(cat /tmp/apt) \
  && python -m pip install --no-cache-dir $(echo `cat /tmp/python`)
ENTRYPOINT ["python", "-m", "main.py"]