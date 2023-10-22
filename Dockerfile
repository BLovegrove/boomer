#!/usr/bin/env -S docker build . --tag=boomer:latest --network=host --file

FROM gorialis/discord.py:full

COPY . /home/boomer

# Remove local copies as these files get mounted instead.
# RUN rm -r /bot/files

WORKDIR /home/boomer

RUN pip install -r requirements.txt

CMD ["python3", "-m", "bot"]