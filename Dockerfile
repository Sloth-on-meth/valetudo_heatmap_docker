FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Copy .env if present (user should mount or provide their own in production)
# ENV variables will be loaded by python-dotenv

EXPOSE 5000

CMD ["python", "app.py"]
