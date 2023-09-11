FROM python:latest
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./main.py /usr/src/app/main.py
RUN mkdir /config
#COPY ./s77-status-bot-config.yaml /config/s77-status-bot-config.yaml

CMD [ "python", "/usr/src/app/main.py" ]
