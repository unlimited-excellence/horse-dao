FROM python:3.11-slim

# Set working directory
WORKDIR .

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the Python program (update `main.py` to your entry point)
CMD ["python", "main.py"]