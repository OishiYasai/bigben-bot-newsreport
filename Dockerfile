# Use official Python slim image
FROM python:3.11-slim

# Install FFmpeg for audio processing
RUN apt-get update && apt-get install -y ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your bot code and assets into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    discord.py \
    apscheduler \
    pytz \
    python-dotenv \
    gtts \
    PyNaCl

# Run the bot
CMD ["python", "news_bot.py"]
