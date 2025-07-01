FROM python:3.11-slim

WORKDIR /app

COPY src/scraper_api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/scraper_api/common.py .
COPY src/scraper_api/models.py .
COPY src/scraper_api/api_main.py .

EXPOSE 8000

CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "8000"]