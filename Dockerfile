FROM python:3.10

COPY . boomer

# Remove local copies as these files get mounted instead.
# RUN rm -r /bot/files

WORKDIR /boomer

RUN python3.10 -m pip install -r requirements.txt

CMD ["python3.10", "-m", "bot"]