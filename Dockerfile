FROM python:3.9.6-alpine

WORKDIR /src
COPY . /src
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./src/main.py"]