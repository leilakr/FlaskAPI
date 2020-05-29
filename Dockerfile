# pull official base image
FROM python:3.8.0-alpine

# set work directory
WORKDIR /usr/src/app

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/
#EXPOSE 5000
RUN ls -la app/

CMD ["gunicorn", "-b 0.0.0.0:8000","api_server:app"]