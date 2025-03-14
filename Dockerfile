# Use an official Python 3.10 slim image as the base
FROM python:3.10-slim

ENV POETRY_VERSION=1.3.2
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python - --version $POETRY_VERSION

WORKDIR /app

# Copy dependency files and install them
COPY pyproject.toml poetry.lock* ./
RUN sed -i '/^package-mode/d' pyproject.toml
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Copy the rest of the project files
COPY . .

# Create the database by running the initialisation script.
RUN python src/initialise_db.py

EXPOSE 8002
CMD ["chainlit", "run", "src/app.py", "--host", "0.0.0.0", "--port", "8002"]
