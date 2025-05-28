FROM ghcr.io/astral-sh/uv:python3.13-alpine


WORKDIR /boomer/

ADD src/bot bot/
ADD src/util util/

CMD ["uv","run","-m","bot"]
