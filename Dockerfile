# Dockerfile

# pull the official docker image
FROM python:3.11.7

USER root

ARG API_KEY
ARG DSN_SENTRY

ENV API_KEY=${API_KEY}
ENV DSN_SENTRY=${DSN_SENTRY}

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /scraping

RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
	&& localedef -i pt_BR -c -f UTF-8 -A /usr/share/locale/locale.alias pt_BR.UTF-8
ENV LANG pt_BR.UTF-8
ENV LC_ALL pt_BR.UTF-8

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /scraping/requirements.txt
RUN pip install --no-cache-dir -r /scraping/requirements.txt

# copy project
COPY ./api /scraping/api
COPY ./auth /scraping/auth
COPY ./core /scraping/core
COPY ./models /scraping/models
COPY ./src /scraping/src
COPY ./main.py /scraping/
COPY ./Dockerfile /scraping/Dockerfile

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
