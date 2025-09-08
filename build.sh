#!/bin/bash
# Build script for Railway deployment

echo "🚀 Starting Railway build process..."

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y wget gnupg unzip curl xvfb chromium chromium-driver

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p videos allure-results/screenshots

echo "✅ Build completed successfully!"
