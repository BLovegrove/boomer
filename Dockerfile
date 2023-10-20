FROM python:3.10-bullseye

COPY requirements.txt /home/boomer/
WORKDIR /home/boomer
RUN pip install -r requirements.txt
COPY . .
CMD ["python3","-m","bot"]
