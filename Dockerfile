FROM python:3.12.2-slim
WORKDIR /app/
ADD static /app
ADD templates /app
ADD main.py /app
ADD requirements.txt /tmp
RUN python -m pip install --no-cache-dir $(echo `cat /tmp/requirements.txt`)
ENTRYPOINT ["python", "-m", "uvicorn", "--host", "0.0.0.0"]
CMD ["main:app"]
