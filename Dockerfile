# Use a python base image
FROM python:3.8-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpoppler-cpp-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*


# Create a working directory
WORKDIR /app

# Copy the requirements file and install the dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Expose port 5000 to access our application from browser
EXPOSE 5000

# The command to run the python application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]

