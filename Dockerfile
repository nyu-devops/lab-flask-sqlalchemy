# Start with a Linux micro-container to keep the image tiny
FROM alpine:3.7

# Document who is responsible for this image
MAINTAINER John Rofrano "rofrano@gmail.com"

# Install just the Python runtime (no dev)
RUN apk add --no-cache \
    python \
    py-pip \
    ca-certificates

# Expose any ports the app is expecting in the environment
ENV PORT 5000
EXPOSE $PORT

# Set up a working folder and install the pre-reqs
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt

# Add the code as the last Docker layer because it changes the most
ADD *.py /app/
ADD app /app/app/

# Run the service
ENV GUNICORN_BIND 0.0.0.0:$PORT
CMD ["gunicorn", "--log-file=-", "app:app"]
