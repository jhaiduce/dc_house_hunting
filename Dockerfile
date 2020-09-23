FROM python:3.8.5-slim

WORKDIR /app

RUN apt-get update
RUN apt-get -y install python-numpy python-mysqldb python-scipy python-pandas python-shapely npm git libmariadb-dev python-cffi
RUN apt-get -y install python-matplotlib
RUN apt-get -y install libffi-dev

COPY requirements.txt /app
RUN pip3 install --trusted-host pypi.python.org --upgrade pip
RUN pip3 install -r /app/requirements.txt
COPY dc_house_hunting /app/dc_house_hunting
COPY setup.py /app
COPY pytest.ini /app
COPY MANIFEST.in /app
COPY CHANGES.txt /app
COPY README.md /app
RUN pip3 install --trusted-host pypi.python.org -e .
COPY check_celery_running.py /app
COPY celery_healthcheck.py /app

COPY pyramid_start.sh /app

EXPOSE 80

ENV NAME World

RUN groupadd --system appuser && \
    useradd --system --no-create-home -s /bin/sh -g appuser appuser

RUN apt-get -y install libcap2-bin

RUN setcap CAP_NET_BIND_SERVICE=+eip /usr/local/bin/python3.8

USER appuser

CMD ["/app/pyramid_start.sh"]
