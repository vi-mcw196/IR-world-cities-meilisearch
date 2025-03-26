FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY stats_monitor.py .

CMD ["python", "stats_monitor.py"]