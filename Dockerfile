# Step 1: Use official lightweight Python base image
FROM python:3.11-alpine

# Step 2: Set secure working directory inside container
WORKDIR /app

# Step 3: Prevent Python from writing .pyc files & buffer streams
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Step 4: Install system dependencies (if any are needed later)
RUN apk add --no-cache gcc musl-dev linux-headers

# Step 5: Copy dependencies and install them
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the rest of the modular application code
COPY . /app/

# Step 7: Expose port 5000 for network routing
EXPOSE 5000

# Step 8: Run app via production server (Gunicorn WSGI)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
