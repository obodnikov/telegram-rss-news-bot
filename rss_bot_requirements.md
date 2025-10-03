# RSS Bot Setup Guide with Multiple Translators

## Installation

### Base Requirements
```
python-telegram-bot==20.7
feedparser==6.0.10
```

### Translation Engine Requirements

**Install based on which translator you want to use:**

#### Free Options (No API Key):
```bash
# Google Translate (basic quality, free)
pip install deep-translator==1.11.4

# MyMemory (alternative free option)
pip install deep-translator==1.11.4

# LibreTranslate (open source, can self-host)
pip install requests
```

#### Paid Options (API Key Required):
```bash
# DeepL (best quality, 500k chars/month free tier)
pip install deepl==1.16.1

# OpenAI ChatGPT (high quality, flexible)
pip install openai==1.12.0

# Anthropic Claude (high quality)
pip install anthropic==0.18.1
```

## Translator Comparison

### 🆓 **Google Translate** (Recommended to start)
- **Quality**: ⭐⭐⭐ (3/5) - Basic but usable
- **Cost**: FREE
- **Speed**: Fast
- **Setup**: No API key needed
- **Best for**: Testing, low-budget projects
- **Set**: `TRANSLATOR_TYPE = "google"`

### 🆓 **MyMemory**
- **Quality**: ⭐⭐⭐ (3/5) - Similar to Google
- **Cost**: FREE (limited to 500 chars per request)
- **Speed**: Medium
- **Setup**: No API key needed
- **Best for**: Alternative to Google
- **Set**: `TRANSLATOR_TYPE = "mymemory"`

### 🆓 **LibreTranslate**
- **Quality**: ⭐⭐⭐ (3/5) - Open source
- **Cost**: FREE (can self-host)
- **Speed**: Medium-Slow
- **Setup**: No API key for public instance
- **Best for**: Privacy-conscious, self-hosting
- **Set**: `TRANSLATOR_TYPE = "libretranslate"`

### 💰 **DeepL** ⭐ (Recommended for quality)
- **Quality**: ⭐⭐⭐⭐⭐ (5/5) - Best neural translation
- **Cost**: FREE tier (500k chars/month), then $5.49/month
- **Speed**: Fast
- **Setup**: Get API key at https://www.deepl.com/pro-api
- **Best for**: Professional quality on budget
- **Set**: `TRANSLATOR_TYPE = "deepl"`

### 💰 **OpenAI ChatGPT**
- **Quality**: ⭐⭐⭐⭐⭐ (5/5) - Excellent, context-aware
- **Cost**: Pay per use (~$0.15 per 1M input tokens with gpt-4o-mini)
- **Speed**: Medium
- **Setup**: Get API key at https://platform.openai.com/api-keys
- **Best for**: Context-aware translation, idiomatic expressions
- **Models**: 
  - `gpt-4o-mini` - Cheap and good
  - `gpt-4o` - Best quality
- **Set**: `TRANSLATOR_TYPE = "openai"`

### 💰 **Anthropic Claude**
- **Quality**: ⭐⭐⭐⭐⭐ (5/5) - Excellent
- **Cost**: Pay per use (~$1 per 1M input tokens with Haiku)
- **Speed**: Fast
- **Setup**: Get API key at https://console.anthropic.com/
- **Best for**: High quality, good value
- **Models**:
  - `claude-3-5-haiku-20241022` - Fast and cheap
  - `claude-3-5-sonnet-20241022` - Best quality
- **Set**: `TRANSLATOR_TYPE = "anthropic"`

## Configuration Examples

### Using Google Translate (Free):
```python
TRANSLATOR_TYPE = "google"
# No API key needed!
```

### Using DeepL (Best Quality):
```python
TRANSLATOR_TYPE = "deepl"
DEEPL_API_KEY = "your-deepl-api-key-here"
```

### Using ChatGPT:
```python
TRANSLATOR_TYPE = "openai"
OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxx"
```

### Using Claude:
```python
TRANSLATOR_TYPE = "anthropic"
ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxx"
```

## Getting API Keys

### DeepL (500k chars/month FREE):
1. Go to https://www.deepl.com/pro-api
2. Sign up for free account
3. Get API key from account settings
4. Free tier includes 500,000 characters per month

### OpenAI:
1. Go to https://platform.openai.com/signup
2. Add payment method (pay as you go)
3. Get API key: https://platform.openai.com/api-keys
4. Cost: ~$0.15 per 1M tokens (very cheap with gpt-4o-mini)

### Anthropic:
1. Go to https://console.anthropic.com/
2. Sign up and add payment
3. Get API key from settings
4. Cost: ~$1 per 1M tokens with Haiku

## Quick Start

### 1. Install dependencies:
```bash
# For Google Translate (free):
pip install python-telegram-bot feedparser deep-translator

# For DeepL:
pip install python-telegram-bot feedparser deepl

# For ChatGPT:
pip install python-telegram-bot feedparser openai

# For Claude:
pip install python-telegram-bot feedparser anthropic
```

### 2. Configure the bot:
```python
TELEGRAM_TOKEN = "your_bot_token"
CHAT_ID = "@yourchannel"
RSS_URL = "https://24.hu/feed/"
TRANSLATOR_TYPE = "google"  # Change to your choice
```

### 3. Run:
```bash
python rss_bot.py
```

## Cost Estimation (per month)

Assuming ~50 news items per day, ~200 words each:

| Translator | Cost/Month | Quality |
|------------|-----------|---------|
| Google     | FREE      | ⭐⭐⭐   |
| MyMemory   | FREE      | ⭐⭐⭐   |
| LibreTranslate | FREE  | ⭐⭐⭐   |
| DeepL      | FREE*     | ⭐⭐⭐⭐⭐ |
| ChatGPT (mini) | ~$2-5 | ⭐⭐⭐⭐⭐ |
| Claude (Haiku) | ~$3-7 | ⭐⭐⭐⭐⭐ |

*DeepL free tier: 500k chars/month (plenty for news)

## My Recommendations

### For Testing:
**Start with Google Translate** - it's free and works immediately

### For Best Free Quality:
**Use DeepL free tier** - 500k chars/month is more than enough for a news bot

### For Best Overall:
**DeepL or ChatGPT with gpt-4o-mini** - excellent quality, very affordable

### For Maximum Quality:
**ChatGPT with gpt-4o or Claude Sonnet** - best translations, understands context

## Switching Translators

You can easily switch translators by just changing one variable:

```python
TRANSLATOR_TYPE = "deepl"  # Just change this!
```

Start with **Google** (free), test the bot, then upgrade to **DeepL** (still free for 500k chars/month) for much better quality!

## Example Output Comparison

**Original Hungarian:**
"A miniszterelnök ma bejelentette az új intézkedéseket"

**Google Translate:**
"Премьер-министр объявил сегодня о новых мерах"

**DeepL/ChatGPT:**
"Премьер-министр сегодня объявил о новых мерах"

(DeepL and ChatGPT typically produce more natural word order and better grammar)
