# Step 1: Use official Python base image (version 3.9, slim variant)
FROM python:3.9-slim-buster

# Step 2: Set working directory inside the container
# All subsequent commands will execute from here
WORKDIR /app

# Step 3: Copy requirements and install dependencies
# Copy requirements.txt from the local project to the container
COPY requirements.txt .

# Install Python packages listed in requirements.txt
# --no-cache-dir reduces image size by skipping pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the rest of the application files into the container
COPY . .

# Step 5: Declare the port the app listens on inside the container
# (Note: this does not expose the port on the host)
EXPOSE 5000

# Step 6: Define the default command to run the app
# Runs your Python application when the container starts
CMD ["python", "app.py"]
