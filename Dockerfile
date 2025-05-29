FROM ghcr.io/astral-sh/uv:python3.13-alpine


WORKDIR /boomer/

ADD bot bot/
ADD util util/

CMD ["uv","run","-m","bot"]
