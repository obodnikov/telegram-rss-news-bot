"""
Configuration file for Telegram RSS Bot
Edit these values according to your setup
"""

# ============================================================================
# TELEGRAM CONFIGURATION
# ============================================================================

# Your bot token from @BotFather
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Channel username (e.g., "@yourchannel") or chat ID (e.g., "-1001234567890")
CHAT_ID = "@yourchannel"


# ============================================================================
# RSS FEED CONFIGURATION
# ============================================================================

# RSS feed URL to monitor
RSS_URL = "https://24.hu/feed/"

# How often to check the feed (in seconds)
# 300 = 5 minutes, 600 = 10 minutes, 900 = 15 minutes
CHECK_INTERVAL = 300


# ============================================================================
# TRANSLATION CONFIGURATION
# ============================================================================

# Choose translator: "google", "mymemory", "libretranslate", "deepl", "openai", "anthropic"
TRANSLATOR_TYPE = "google"

# Source and target languages (ISO 639-1 codes)
SOURCE_LANGUAGE = "hu"  # Hungarian
TARGET_LANGUAGE = "ru"  # Russian


# ============================================================================
# API KEYS (Only needed for paid services)
# ============================================================================

# DeepL API Key (Free tier: 500k chars/month)
# Get it at: https://www.deepl.com/pro-api
DEEPL_API_KEY = "your-deepl-key-here"

# OpenAI API Key
# Get it at: https://platform.openai.com/api-keys
OPENAI_API_KEY = "your-openai-key-here"

# OpenAI Model: "gpt-4o-mini" (cheap) or "gpt-4o" (best quality)
OPENAI_MODEL = "gpt-4o-mini"

# Anthropic API Key
# Get it at: https://console.anthropic.com/
ANTHROPIC_API_KEY = "your-anthropic-key-here"

# Anthropic Model: "claude-3-5-haiku-20241022" (fast) or "claude-3-5-sonnet-20241022" (best)
ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"


# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Maximum length of text to translate at once (characters)
MAX_TRANSLATION_LENGTH = 5000

# Maximum length of description to include in messages (characters)
MAX_DESCRIPTION_LENGTH = 500

# Delay between sending messages to avoid rate limiting (seconds)
MESSAGE_DELAY = 2

# LibreTranslate API URL (only if using libretranslate)
LIBRETRANSLATE_API_URL = "https://libretranslate.com/translate"


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Logging level: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_LEVEL = "INFO"

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'