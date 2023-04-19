FROM python:3.11.3-slim-buster

ENV PYTHONUNBUFFERED=1

ENV DIRPATH=/var/levenshtein-distance-service
WORKDIR $DIRPATH

# Now, be a web server.
EXPOSE 8001
CMD ["python", "./server.py"]
