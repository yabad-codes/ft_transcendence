FROM python:3.12-slim-bullseye

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

COPY config/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

CMD [ "/app/entrypoint.sh" ]