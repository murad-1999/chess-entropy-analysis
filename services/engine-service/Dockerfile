FROM python:3.11-slim

WORKDIR /app

# Safely install necessary tools, download stockfish, extract it directly to the bin, and purge caches
RUN apt-get update && apt-get install -y wget tar \
    && wget -q https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar -O stockfish.tar \
    && tar -xf stockfish.tar \
    && find . -name "stockfish-ubuntu-x86-64-avx2" -type f -exec mv {} /usr/local/bin/stockfish \; \
    && chmod +x /usr/local/bin/stockfish \
    && rm -rf stockfish* \
    && apt-get remove -y wget \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Ensure security with a hardened non-root container profile
RUN useradd -m appuser \
    && chown -R appuser:appuser /app

USER appuser

# Run in single process mode to avoid singleton lock collision (No --workers flag)
CMD sh -c "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}"
