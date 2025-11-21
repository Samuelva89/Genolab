# Stage 1: Base image
FROM python:3.10-slim-bullseye as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN groupadd -r app && useradd -r -g app appuser

WORKDIR /app


# Stage 2: Builder for python dependencies
FROM base as builder

# Install system dependencies required for building some python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./

# Install production dependencies
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# (Optional) If you need dev dependencies for a test stage, you could install them here
# RUN pip install --no-cache-dir -r requirements-dev.txt


# Stage 3: Production image
FROM base as production

# Copy wheels from builder stage and install them
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* && rm -rf /wheels



# Create data directory and set permissions for sqlite
RUN mkdir -p /app/data

# Change ownership of the app directory
RUN chown -R appuser:app /app

# Switch to the non-root user
USER appuser

# Set the command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
