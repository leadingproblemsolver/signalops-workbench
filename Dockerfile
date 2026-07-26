FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 signalops
USER signalops
WORKDIR /home/signalops

ENTRYPOINT ["signalops"]
CMD ["--help"]
