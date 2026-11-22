FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY README.md LICENSE ./
COPY src ./src
COPY config/tmdb-token.enc.json ./config/tmdb-token.enc.json
RUN uv sync --locked --no-dev

RUN useradd --create-home app && mkdir /app/data && chown app:app /app/data
USER app

ENV PATH="/app/.venv/bin:$PATH"
ENV MOVIE_WATCHLIST_FILE=/app/data/watchlist.json
ENV MOVIE_WATCHLIST_TMDB_CACHE=/app/data/.tmdb-token
ENTRYPOINT ["movie_watchlist"]
CMD ["--help"]
