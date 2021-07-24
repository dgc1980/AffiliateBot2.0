FROM python:3.9

WORKDIR /app

COPY ./requirements.txt /tmp

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY bot/ .
RUN chmod +x bot.py

CMD [ "python3", "/app/bot.py" ]
