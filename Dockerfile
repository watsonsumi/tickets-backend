FROM python:3.7.7-alpine3.10

ADD ./requirements.txt /app/requirements.txt
RUN set -ex \
    && apk add --no-cache --virtual .build-deps libffi-dev musl-dev mariadb-connector-c-dev  jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev build-base \
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir -r /app/requirements.txt \
    && runDeps="$(scanelf --needed --nobanner --recursive /env \
        | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
        | sort -u \
        | xargs -r apk info --installed \
        | sort -u)" \
    && apk add --virtual rundeps $runDeps \
    && apk del .build-deps



ADD . /app
WORKDIR /app

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

RUN pip install gunicorn


EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "sistema_tickets.wsgi:application"]