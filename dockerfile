FROM python:3.9

RUN apt-get update
RUN apt-get install curl vim wget bash nano -y

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /cnc
COPY . /cnc

EXPOSE 8000
EXPOSE 9092
ENTRYPOINT ["/cnc/docker-entrypoint.sh"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]