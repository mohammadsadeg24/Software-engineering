# Use official Python image
FROM python:3.11-slim

# Set environment vars for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    libpq-dev gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv or requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files (optional if you serve via whitenoise or S3)
RUN python manage.py collectstatic --noinput || true

# Expose Django port
EXPOSE 8000

# Use gunicorn for production
CMD ["gunicorn", "honey_site.wsgi:application", "--bind", "0.0.0.0:8000"]