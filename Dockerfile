FROM nginx/unit:1.34.2-python3.11

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app

# Provide Unit config on container startup
COPY unit.config.json /docker-entrypoint.d/unit.config.json

EXPOSE 8000

