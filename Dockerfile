# 1. Use the official Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy your actual code (main.py) into the container
COPY . .

# 5. Tell Docker what port this uses
EXPOSE 8000

# 6. The command to start the server (0.0.0.0 lets it be accessed from outside the container)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]