FROM python:3.8-buster

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt -i https://mirrors.sjtug.sjtu.edu.cn/pypi/web/simple
COPY *.py /app/

CMD python main.py --upstream=caddy-blank:80 --port=80
