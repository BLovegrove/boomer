FROM ghcr.io/astral-sh/uv:python3.13-alpine


WORKDIR /boomer/

ADD src/bot bot/
ADD src/util util/
ADD src/requirements.txt .
ADD src/config.py .c

RUN sudo apt install -y libffi-dev python3.13dev 
RUN uv sync --locked


CMD ["uv","run","python","-m","bot"]
