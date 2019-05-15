FROM python:3.7

RUN apt update && apt upgrade -y && apt install -y locales locales-all cron postgresql
COPY requirements.txt /tmp/
COPY requirements_dev.txt /tmp/
RUN pip install -r /tmp/requirements_dev.txt && rm /tmp/requirements*.txt

# French ENV for date
RUN sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL fr_FR
ENV LANG fr_FR
ENV LANGUAGE fr_FR

RUN useradd ateliersoude && \
    mkdir -p /srv/app/tmp && \
    mkdir -p /srv/app/media && \
    chown ateliersoude /srv/app/tmp && \
    chown ateliersoude /srv/app/media

WORKDIR /srv/app

COPY ateliersoude ateliersoude
RUN chown -R ateliersoude ateliersoude
COPY manage.py .
COPY deployment/docker-app/start.sh /start.sh
COPY deployment/docker-app/ateliersoude.cron /etc/cron.d/ateliersoude

EXPOSE 8000

CMD /start.sh && bash
