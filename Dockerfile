# Use Python 3.11 slim image for Railway deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Chrome and video recording
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libxrandr2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf-2.0-0 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrender1 \
    libsm6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for Chrome
RUN ln -sf /usr/bin/chromium /usr/bin/chrome
RUN ln -sf /usr/bin/chromium /usr/bin/google-chrome

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p videos allure-results/screenshots

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PATH="/usr/bin/chromium:/usr/bin/chromedriver:$PATH"

# Expose port
EXPOSE $PORT

# Create startup script
RUN echo '#!/bin/bash\n\
# Start xvfb in background\n\
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &\n\
# Wait a moment for xvfb to start\n\
sleep 2\n\
# Start the application\n\
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120' > /app/start.sh && \
    chmod +x /app/start.sh

# Start command
CMD ["/app/start.sh"]
