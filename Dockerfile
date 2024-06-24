# Official Python image.
FROM python:3.10-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file into the container.
COPY requirements.txt .

# Install any necessary dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI code into the container.
COPY . .

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run the FastAPI server using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]