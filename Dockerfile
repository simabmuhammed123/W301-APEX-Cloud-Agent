FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "google-adk[extensions]"

COPY . .

EXPOSE 8508

CMD ["streamlit", "run", "app.py", "--server.port=8508", "--server.address=0.0.0.0", "--server.headless=true"]
