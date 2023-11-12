FROM python:3.11-slim

RUN apt-get update && \
    apt-get upgrade -y


ENV PYTHONDONTWRITEBYTECODE 1 
ENV PYTHONUNBUFFERED 1 


COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt


RUN useradd --create-home appuser
WORKDIR /home/appuser

COPY ./src ./app/src

WORKDIR /home/appuser/app
USER appuser

CMD ["python", "./src/web.py"]

