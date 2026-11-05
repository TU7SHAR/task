# Use a small, official Python base image. 3.10-slim keeps the image lean
# while remaining compatible with Flask 2.0.2 / pymongo 3.12.0.
FROM python:3.10-slim

# Prevent Python from writing .pyc files and force stdout/stderr to be
# unbuffered so logs show up immediately in `kubectl logs`.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create and switch to an application directory.
WORKDIR /app

# Install dependencies first (separate layer) to leverage Docker's build cache:
# dependencies only re-install when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source.
COPY app.py .

# Run as a non-root user for better security.
RUN useradd --create-home appuser
USER appuser

# The Flask app listens on port 5000.
EXPOSE 5000

# Start the application.
CMD ["python", "app.py"]
