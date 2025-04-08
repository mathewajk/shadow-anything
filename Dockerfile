# Use the Python 3 official image
# https://hub.docker.com/_/python
FROM python:3.12

# Run in unbuffered mode
ENV PYTHONUNBUFFERED=1 

# Create and change to the app directory.
WORKDIR /app

# Copy local code to the container image.
COPY . ./

# Install project dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN apt-get update && apt-get install -y praat && apt-get install -y ffmpeg

# Run the web service on container startup.
CMD ["gunicorn", "backend.app:app"]