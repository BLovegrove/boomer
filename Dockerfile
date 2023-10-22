#!/usr/bin/env -S docker build . --tag=boomer:latest --network=host --file

FROM python:3.10

COPY . /home/boomer

# Remove local copies as these files get mounted instead.
# RUN rm -r /bot/files

WORKDIR /home/boomer

RUN python3 -m pip install -r requirements.txt

CMD ["python3", "-m", "bot"]