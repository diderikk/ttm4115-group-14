# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the poetry.lock and pyproject.toml files to the container
COPY . .


RUN apt-get update && apt-get install -y curl libpq-dev gcc

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Activate Poetry
ENV PATH="/root/.local/bin:${PATH}"
RUN poetry config virtualenvs.create false

# Install project dependencies
RUN poetry install --only main --no-interaction --no-ansi

# Copy the project code to the container

# Run Django migrations
# RUN poetry run hermes runserver
# Expose port 8000
EXPOSE 8000

# Start the Django development server
CMD ["poetry", "run", "hermes", "runserver", "0.0.0.0:8000"]
