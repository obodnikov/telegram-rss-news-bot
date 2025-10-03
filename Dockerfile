FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY rss_bot.py .
COPY config.py .

# Run the bot
CMD ["python", "rss_bot.py"]