# 📰 Telegram RSS News Bot

A Telegram bot that monitors RSS feeds, translates articles, and posts them to your Telegram channel. Perfect for translating news from any language to another!

## ✨ Features

- 🔄 **Automatic RSS Monitoring** - Periodically checks RSS feeds for new articles
- 🌍 **Multi-Language Translation** - Supports 6 different translation engines
- 📢 **Channel Broadcasting** - Posts directly to Telegram channels
- 🎯 **Smart Formatting** - Clean, readable messages with titles, summaries, and content
- 🔁 **Auto-Restart** - Runs as a daemon with automatic restart on failures
- 📝 **Full Content** - Extracts both description and full article content
- 🚫 **Duplicate Prevention** - Never posts the same article twice
- 📊 **Logging** - Comprehensive logging for monitoring and debugging

## 🎯 Use Case

This bot was created to translate Hungarian news from [24.hu](https://24.hu/) to Russian, but can be configured for any RSS feed and language pair!

## 📋 Requirements

- Python 3.8+
- Telegram Bot Token
- Telegram Channel
- Internet connection

## 🚀 Quick Start

### 1. Clone or Download

```bash
git clone <your-repo-url>
cd rss-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**For different translators:**
```bash
# Google Translate (free, default)
pip install python-telegram-bot feedparser deep-translator

# DeepL (best quality, free tier available)
pip install python-telegram-bot feedparser deepl

# OpenAI ChatGPT
pip install python-telegram-bot feedparser openai

# Anthropic Claude
pip install python-telegram-bot feedparser anthropic
```

### 3. Create Telegram Bot

1. Open Telegram and find `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the API token

### 4. Create Telegram Channel

1. In Telegram: Menu → New Channel
2. Set name (e.g., "24.hu Новости")
3. Choose Public or Private
4. Add your bot as administrator with "Post messages" permission

### 5. Configure the Bot

Edit `config.py`:

```python
# Required settings
TELEGRAM_TOKEN = "123456:ABC-your-bot-token-here"
CHAT_ID = "@yourchannel"  # or "-1001234567890" for private channels
RSS_URL = "https://24.hu/feed/"
TRANSLATOR_TYPE = "google"  # Start with free Google Translate
```

### 6. Run the Bot

```bash
python3 rss_bot.py
```

That's it! Your bot is now running and will post new articles to your channel.

## ⚙️ Configuration

All settings are in `config.py`:

### Basic Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `TELEGRAM_TOKEN` | Bot token from @BotFather | Required |
| `CHAT_ID` | Channel username or chat ID | Required |
| `RSS_URL` | RSS feed to monitor | Required |
| `CHECK_INTERVAL` | Seconds between checks | 300 (5 min) |
| `TRANSLATOR_TYPE` | Translation engine | "google" |

### Translation Engines

| Engine | Quality | Cost | API Key | Best For |
|--------|---------|------|---------|----------|
| `google` | ⭐⭐⭐ | FREE | No | Quick start |
| `mymemory` | ⭐⭐⭐ | FREE | No | Alternative |
| `libretranslate` | ⭐⭐⭐ | FREE | No | Privacy |
| `deepl` | ⭐⭐⭐⭐⭐ | FREE* | Yes | Best quality |
| `openai` | ⭐⭐⭐⭐⭐ | Paid | Yes | Context-aware |
| `anthropic` | ⭐⭐⭐⭐⭐ | Paid | Yes | High quality |

*DeepL: 500,000 characters/month free

### Advanced Settings

```python
SOURCE_LANGUAGE = "hu"           # Source language code
TARGET_LANGUAGE = "ru"           # Target language code
MAX_TRANSLATION_LENGTH = 5000    # Max chars per translation
MAX_DESCRIPTION_LENGTH = 500     # Max description length
MESSAGE_DELAY = 2                # Delay between messages (seconds)
LOG_LEVEL = "INFO"               # Logging level
```

## 🔑 Getting API Keys

### DeepL (Recommended - 500k chars/month FREE)

1. Visit https://www.deepl.com/pro-api
2. Sign up for free account
3. Copy your API key
4. Set in `config.py`:
   ```python
   TRANSLATOR_TYPE = "deepl"
   DEEPL_API_KEY = "your-key-here"
   ```

### OpenAI ChatGPT

1. Visit https://platform.openai.com/signup
2. Add payment method
3. Get API key from https://platform.openai.com/api-keys
4. Set in `config.py`:
   ```python
   TRANSLATOR_TYPE = "openai"
   OPENAI_API_KEY = "sk-proj-..."
   OPENAI_MODEL = "gpt-4o-mini"  # or "gpt-4o"
   ```

### Anthropic Claude

1. Visit https://console.anthropic.com/
2. Sign up and add payment
3. Get API key from settings
4. Set in `config.py`:
   ```python
   TRANSLATOR_TYPE = "anthropic"
   ANTHROPIC_API_KEY = "sk-ant-..."
   ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"
   ```

## 🔧 Running as Daemon

### Linux (systemd) - Recommended

1. Create service file:
   ```bash
   sudo nano /etc/systemd/system/rss-bot.service
   ```

2. Paste (replace paths and username):
   ```ini
   [Unit]
   Description=Telegram RSS Bot
   After=network-online.target

   [Service]
   Type=simple
   User=yourusername
   Group=yourusername
   WorkingDirectory=/home/yourusername/rss-bot
   ExecStart=/usr/bin/python3 /home/yourusername/rss-bot/rss_bot.py
   Restart=always
   RestartSec=10
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable rss-bot
   sudo systemctl start rss-bot
   sudo systemctl status rss-bot
   ```

4. View logs:
   ```bash
   sudo journalctl -u rss-bot -f
   ```

### macOS (launchd)

1. Create plist file:
   ```bash
   nano ~/Library/LaunchAgents/com.rssbot.plist
   ```

2. Paste (replace paths):
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.rssbot</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/local/bin/python3</string>
           <string>/Users/yourusername/rss-bot/rss_bot.py</string>
       </array>
       <key>WorkingDirectory</key>
       <string>/Users/yourusername/rss-bot</string>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
       <key>StandardOutPath</key>
       <string>/Users/yourusername/rss-bot/bot.log</string>
       <key>StandardErrorPath</key>
       <string>/Users/yourusername/rss-bot/bot.error.log</string>
   </dict>
   </plist>
   ```

3. Load:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.rssbot.plist
   ```

### Docker

1. Build:
   ```bash
   docker build -t rss-bot .
   ```

2. Run:
   ```bash
   docker run -d --name rss-bot --restart=always rss-bot
   ```

3. Logs:
   ```bash
   docker logs -f rss-bot
   ```

### Quick Options (Testing)

**screen:**
```bash
screen -S rssbot
python3 rss_bot.py
# Press Ctrl+A, then D to detach
```

**tmux:**
```bash
tmux new -s rssbot
python3 rss_bot.py
# Press Ctrl+B, then D to detach
```

**nohup:**
```bash
nohup python3 rss_bot.py > bot.log 2>&1 &
```

## 📊 Message Format

The bot creates nicely formatted messages:

```
📰 Article Title (translated)

Brief summary from description - emphasized as header

Full article content translated from the RSS feed.
Can be quite long, includes the complete article text.

🔗 Read full article
```

**Formatting:**
- Title: **Bold**
- Description: **Bold + Italic** (emphasized header)
- Content: Regular text
- Link: Clickable with emoji

## 🔍 Monitoring

### Check if bot is running

**systemd:**
```bash
sudo systemctl status rss-bot
```

**Process:**
```bash
ps aux | grep rss_bot.py
```

### View logs

**systemd:**
```bash
sudo journalctl -u rss-bot -f
```

**Docker:**
```bash
docker logs -f rss-bot
```

**File:**
```bash
tail -f bot.log
```

## 🐛 Troubleshooting

### Bot doesn't start

1. Check configuration:
   ```bash
   python3 rss_bot.py
   # Look for error messages
   ```

2. Verify bot token:
   ```python
   # In config.py, make sure TELEGRAM_TOKEN is correct
   ```

3. Check Python path:
   ```bash
   which python3
   # Use this path in service files
   ```

### No messages posted

1. Verify channel setup:
   - Bot is administrator
   - Bot has "Post messages" permission
   - Channel ID is correct (use @username or numeric ID)

2. Check RSS feed:
   ```bash
   curl https://24.hu/feed/
   # Should return XML content
   ```

3. Test manually:
   ```bash
   python3 rss_bot.py
   # Watch for errors in console
   ```

### Translation errors

1. **Google/MyMemory**: Check internet connection
2. **DeepL/OpenAI/Anthropic**: Verify API key is correct
3. Check logs for specific error messages

### "No such process" error (systemd)

Replace `User` and `Group` in service file:
```bash
whoami  # Use this as User
id -gn  # Use this as Group
```

## 📁 Project Structure

```
rss-bot/
├── rss_bot.py              # Main bot code
├── config.py               # Configuration (edit this!)
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── Dockerfile             # Docker container
├── docker-compose.yml     # Docker Compose config
└── rss-bot.service        # systemd service file
```

## 🔒 Security

### Protect your secrets

Add to `.gitignore`:
```
config.py
*.pyc
__pycache__/
*.log
subscribers.json
```

### Don't commit:
- API keys
- Bot tokens
- Channel IDs

## 📈 Cost Estimation

For ~50 articles/day, ~200 words each:

| Translator | Monthly Cost | Quality |
|------------|--------------|---------|
| Google | FREE | ⭐⭐⭐ |
| DeepL | FREE | ⭐⭐⭐⭐⭐ |
| ChatGPT (mini) | ~$2-5 | ⭐⭐⭐⭐⭐ |
| Claude (Haiku) | ~$3-7 | ⭐⭐⭐⭐⭐ |

## 🎯 Recommendations

### Getting Started
**Use Google Translate** - Free, works immediately, no setup

### Best Free Option
**Use DeepL free tier** - 500k chars/month, excellent quality

### Best Overall
**DeepL or ChatGPT (gpt-4o-mini)** - Great quality, very affordable

### Maximum Quality
**ChatGPT (gpt-4o) or Claude Sonnet** - Best translations, understands context

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📝 License

This project is open source. Feel free to use and modify!

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review logs for error messages
3. Verify configuration settings
4. Test components individually

## 🔗 Useful Links

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [DeepL API](https://www.deepl.com/pro-api)
- [OpenAI Platform](https://platform.openai.com/)
- [Anthropic Console](https://console.anthropic.com/)
- [RSS 2.0 Specification](https://www.rssboard.org/rss-specification)

## 🎉 Acknowledgments

Built with:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [feedparser](https://github.com/kurtmckee/feedparser)
- Various translation APIs

---

**Made with ❤️ for keeping you informed in your preferred language!**
