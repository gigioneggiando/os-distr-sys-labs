# 2a) Base image
FROM python:3.11-slim

# Create app dir
WORKDIR /app

# 2b) Install Flask
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2c) Copy server file
COPY app.py .

# (Optional) document port
EXPOSE 5000

# 2d) Run the server
CMD ["python", "app.py"]
