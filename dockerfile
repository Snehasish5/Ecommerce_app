# Base Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install required OS packages for MySQL and Python
RUN apt-get update && apt-get install -y \
    default-mysql-server \
    default-libmysqlclient-dev \
    gcc \
    libssl-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose Flask app port
EXPOSE 5000

# Initialize MySQL
RUN service mysql start && \
    mysql -e "CREATE DATABASE IF NOT EXISTS ecommerce;" && \
    mysql -e "CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED BY 'user';" && \
    mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost'; FLUSH PRIVILEGES;"

# Set default command to run both MySQL and Flask
CMD service mysql start && python app.py
