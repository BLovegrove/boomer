FROM ghcr.io/astral-sh/uv:python3.13-alpine


WORKDIR /boomer/

ADD bot bot/
ADD util util/
ADD .python-version .python-version
ADD pyproject.toml pyproject.toml

CMD ["uv","run","-m","bot"]
