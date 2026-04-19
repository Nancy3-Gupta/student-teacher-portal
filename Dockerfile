# 1. Start with Python 3.11
FROM python:3.11-slim

# 2. Set the folder inside the container where our code will live
WORKDIR /app

# 3. Install system tools needed for PostgreSQL to work on Linux
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# 4. Copy the requirements file and install the libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy all your code (main.py, models.py, static folder, etc.) into the container
COPY . .

# 6. Tell Docker to start the FastAPI server when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]