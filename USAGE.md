# 🚀 Quick Usage Guide

The bot now supports **command-line arguments** and **environment variables** for configuration!

## 📋 Three Ways to Configure

### 1️⃣ Command Line Arguments (Best for testing)

```bash
python rss_bot.py \
  --token "YOUR_BOT_TOKEN" \
  --chat "@yourchannel" \
  --feed "https://24.hu/feed/" \
  --translator google
```

### 2️⃣ Environment Variables (Best for production)

```bash
# Set environment variables
export TELEGRAM_TOKEN="YOUR_BOT_TOKEN"
export CHAT_ID="@yourchannel"
export RSS_URL="https://24.hu/feed/"
export TRANSLATOR_TYPE="google"

# Run bot
python rss_bot.py
```

### 3️⃣ Using .env File (Recommended)

```bash
# Copy example file
cp .env.example .env

# Edit .env with your values
nano .env

# Load and run
source .env
python rss_bot.py
```

---

## 🎯 Quick Examples

### Free Translation (Google Translate)

```bash
python rss_bot.py \
  --token "123456:ABC-DEF" \
  --chat "@mynewschannel" \
  --feed "https://24.hu/feed/"
```

### Using DeepL (Best Quality)

```bash
python rss_bot.py \
  --token "123456:ABC-DEF" \
  --chat "@mynewschannel" \
  --feed "https://24.hu/feed/" \
  --translator deepl \
  --deepl-key "your-deepl-key"
```

### Using ChatGPT

```bash
python rss_bot.py \
  --token "123456:ABC-DEF" \
  --chat "@mynewschannel" \
  --feed "https://24.hu/feed/" \
  --translator openai \
  --openai-key "sk-proj-..." \
  --openai-model "gpt-4o-mini"
```

### Different Languages

```bash
python rss_bot.py \
  --token "123456:ABC-DEF" \
  --chat "@mynewschannel" \
  --feed "https://example.com/feed/" \
  --source-lang "en" \
  --target-lang "de"
```

### Custom Check Interval

```bash
python rss_bot.py \
  --token "123456:ABC-DEF" \
  --chat "@mynewschannel" \
  --interval 600  # Check every 10 minutes
```

### Test Run (Single Check)

```bash
python rss_bot.py \
  --token "123456:ABC-DEF" \
  --chat "@mynewschannel" \
  --once
```

---

## 📝 All Available Arguments

### Required

| Argument | Short | Environment Variable | Description |
|----------|-------|---------------------|-------------|
| `--token` | `-t` | `TELEGRAM_TOKEN` | Bot token from @BotFather |
| `--chat` | `-c` | `CHAT_ID` | Channel username or chat ID |

### Optional

| Argument | Short | Environment Variable | Default | Description |
|----------|-------|---------------------|---------|-------------|
| `--feed` | `-f` | `RSS_URL` | `https://24.hu/feed/` | RSS feed URL |
| `--translator` | `-tr` | `TRANSLATOR_TYPE` | `google` | Translation engine |
| `--source-lang` | `-sl` | `SOURCE_LANGUAGE` | `hu` | Source language code |
| `--target-lang` | `-tl` | `TARGET_LANGUAGE` | `ru` | Target language code |
| `--interval` | `-i` | `CHECK_INTERVAL` | `300` | Check interval (seconds) |
| `--max-description` | | `MAX_DESCRIPTION_LENGTH` | `500` | Max description chars |
| `--max-content` | | `MAX_CONTENT_LENGTH` | `5000` | Max content chars |
| `--log-level` | | `LOG_LEVEL` | `INFO` | Logging level |
| `--once` | | | `false` | Run once and exit |

### API Keys

| Argument | Environment Variable | Used For |
|----------|---------------------|----------|
| `--deepl-key` | `DEEPL_API_KEY` | DeepL translator |
| `--openai-key` | `OPENAI_API_KEY` | OpenAI translator |
| `--openai-model` | `OPENAI_MODEL` | OpenAI model name |
| `--anthropic-key` | `ANTHROPIC_API_KEY` | Anthropic translator |
| `--anthropic-model` | `ANTHROPIC_MODEL` | Anthropic model name |
| `--libretranslate-url` | `LIBRETRANSLATE_API_URL` | LibreTranslate API |

---

## 🔧 Running as Daemon

### With systemd (Environment Variables)

Edit service file:

```ini
[Service]
Environment="TELEGRAM_TOKEN=your-token"
Environment="CHAT_ID=@yourchannel"
Environment="TRANSLATOR_TYPE=google"
ExecStart=/usr/bin/python3 /path/to/rss_bot.py
```

### With systemd (.env file)

```ini
[Service]
EnvironmentFile=/path/to/rss-bot/.env
ExecStart=/usr/bin/python3 /path/to/rss_bot.py
```

### With Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install