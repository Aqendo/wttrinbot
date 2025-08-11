FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ADD ./pyproject.toml .
ADD ./uv.lock .
RUN uv sync --locked
ADD ./wttrinbot ./wttrinbot
#CMD ["sleep", "10000"]
CMD ["uv", "run", "-m", "wttrinbot"]
