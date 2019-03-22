FROM python:2.7-slim

# Expose any ports the app is expecting in the environment
ENV PORT 5000
EXPOSE $PORT

# Set up a working folder and install the pre-reqs
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt

# Add the code as the last Docker layer because it changes the most
ADD . /app/

# Run the service
ENV GUNICORN_BIND 0.0.0.0:$PORT
CMD ["gunicorn", "--log-file=-", "app:app"]
