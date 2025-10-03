# ⚡ Quick Start Guide

Get your RSS bot running in 5 minutes!

## 🎯 Super Quick Setup

```bash
# 1. Install
git clone <repo-url> && cd rss-bot
pip3 install -r requirements.txt

# 2. Configure (interactive)
chmod +x setup.sh && ./setup.sh

# 3. Run
source .env && python3 rss_bot.py
```

Done! 🎉

---

## 📝 Manual Setup (3 steps)

### Step 1: Get Bot Token
1. Open Telegram → Find `@BotFather`
2. Send `/newbot` → Follow instructions
3. Copy token: `123456:ABC-DEF...`

### Step 2: Create Channel
1. Telegram → New Channel → Name it
2. Add bot as admin with "Post messages"
3. Note username: `@yourchannel`

### Step 3: Run Bot

```bash
python3 rss_bot.py \
  --token "123456:ABC-DEF..." \
  --chat "@yourchannel"
```

---

## 🌍 Translator Options

### Free Options (No API Key)

```bash
# Google Translate (default)
python3 rss_bot.py --token "..." --chat "@..." --translator google

# MyMemory
python3 rss_bot.py --token "..." --chat "@..." --translator mymemory

# LibreTranslate
python3 rss_bot.py --token "..." --chat "@..." --translator libretranslate
```

### Paid Options (Better Quality)

```bash
# DeepL (FREE tier: 500k chars/month) ⭐ Recommended
python3 rss_bot.py --token "..." --chat "@..." \
  --translator deepl --deepl-key "your-key"

# ChatGPT
python3 rss_bot.py --token "..." --chat "@..." \
  --translator openai --openai-key "sk-proj-..."

# Claude
python3 rss_bot.py --token "..." --chat "@..." \
  --translator anthropic --anthropic-key "sk-ant-..."
```

---

## 🎨 Common Scenarios

### Different Languages
```bash
python3 rss_bot.py --token "..." --chat "@..." \
  --source-lang "en" --target-lang "de"
```

### Different Feed
```bash
python3 rss_bot.py --token "..." --chat "@..." \
  --feed "https://example.com/rss"
```

### Custom Check Interval
```bash
# Check every 10 minutes
python3 rss_bot.py --token "..." --chat "@..." --interval 600
```

### Test Run (Once)
```bash
python3 rss_bot.py --token "..." --chat "@..." --once
```

### Debug Mode
```bash
python3 rss_bot.py --token "..." --chat "@..." --log-level DEBUG
```

---

## 🚀 Run as Daemon

### Quick Background Run
```bash
# Using nohup
nohup python3 rss_bot.py &

# Using screen
screen -S rssbot
python3 rss_bot.py
# Press Ctrl+A, then D to detach
```

### Systemd (Linux)
```bash
# 1. Create service
sudo nano /etc/systemd/system/rss-bot.service

# 2. Paste:
[Unit]
Description=RSS Bot
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername/rss-bot
EnvironmentFile=/home/yourusername/rss-bot/.env
ExecStart=/usr/bin/python3 /home/yourusername/rss-bot/rss_bot.py
Restart=always

[Install]
WantedBy=multi-user.target

# 3. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable rss-bot
sudo systemctl start rss-bot
sudo systemctl status rss-bot
```

### Docker
```bash
# Build
docker build -t rss-bot .

# Run
docker run -d --name rss-bot --restart=always \
  -e TELEGRAM_TOKEN="..." \
  -e CHAT_ID="@..." \
  rss-bot

# Or with .env file
docker run -d --name rss-bot --restart=always \
  --env-file .env \
  rss-bot
```

---

## 📊 All Options Quick Reference

| What | Environment Variable | Argument | Default |
|------|---------------------|----------|---------|
| Bot token | `TELEGRAM_TOKEN` | `--token` | Required |
| Channel ID | `CHAT_ID` | `--chat` | Required |
| RSS feed | `RSS_URL` | `--feed` | `https://24.hu/feed/` |
| Translator | `TRANSLATOR_TYPE` | `--translator` | `google` |
| From language | `SOURCE_LANGUAGE` | `--source-lang` | `hu` |
| To language | `TARGET_LANGUAGE` | `--target-lang` | `ru` |
| Check interval | `CHECK_INTERVAL` | `--interval` | `300` (5 min) |
| DeepL key | `DEEPL_API_KEY` | `--deepl-key` | - |
| OpenAI key | `OPENAI_API_KEY` | `--openai-key` | - |
| OpenAI model | `OPENAI_MODEL` | `--openai-model` | `gpt-4o-mini` |
| Anthropic key | `ANTHROPIC_API_KEY` | `--anthropic-key` | - |
| Log level | `LOG_LEVEL` | `--log-level` | `INFO` |

---

## 🆘 Troubleshooting

### Bot doesn't post messages
```bash
# Check token and chat ID
python3 rss_bot.py --token "..." --chat "@..." --once --log-level DEBUG
```
- Verify bot is admin in channel
- Check bot has "Post messages" permission
- Try numeric chat ID instead of @username

### Translation not working
```bash
# Test with different translator
python3 rss_bot.py --token "..." --chat "@..." --translator google --once
```

### No new articles
```bash
# Check if feed is accessible
curl https://24.hu/feed/

# Run once to see what's fetched
python3 rss_bot.py --token "..." --chat "@..." --once
```

### "No such process" error (systemd)
```bash
# Use your actual username
whoami  # Use this in User=
id -gn  # Use this in Group=

# Or remove User/Group lines from service file
```

---

## 💡 Pro Tips

### Create aliases
```bash
# Add to ~/.bashrc or ~/.zshrc
alias rss-start='cd ~/rss-bot && source .env && python3 rss_bot.py'
alias rss-test='cd ~/rss-bot && source .env && python3 rss_bot.py --once'
alias rss-debug='cd ~/rss-bot && source .env && python3 rss_bot.py --once --log-level DEBUG'
```

### Use .env for secrets
```bash
# .env
export TELEGRAM_TOKEN="secret"
export CHAT_ID="@channel"
export DEEPL_API_KEY="secret"

# Run
source .env && python3 rss_bot.py
```

### Multiple bots
```bash
# .env.ru
export TELEGRAM_TOKEN="token1"
export CHAT_ID="@channel_ru"
export TARGET_LANGUAGE="ru"

# .env.de
export TELEGRAM_TOKEN="token2"
export CHAT_ID="@channel_de"
export TARGET_LANGUAGE="de"

# Run both
source .env.ru && python3 rss_bot.py &
source .env.de && python3 rss_bot.py &
```

---

## 🔗 More Information

- **Full Documentation**: [README.md](README.md)
- **Detailed Usage**: [USAGE.md](USAGE.md)
- **Help Command**: `python3 rss_bot.py --help`

---

## 📞 Quick Help

```bash
# View all options
python3 rss_bot.py --help

# Test configuration
python3 rss_bot.py --once

# Check logs (systemd)
sudo journalctl -u rss-bot -f

# Check if running
ps aux | grep rss_bot
```

---

**Need help?** Check [README.md](README.md) or run `python3 rss_bot.py --help`