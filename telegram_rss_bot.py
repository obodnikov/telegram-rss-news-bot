import asyncio
import feedparser
import hashlib
from telegram import Bot
from telegram.error import TelegramError
import logging
from abc import ABC, abstractmethod

# Import configuration
import config

# Configure logging
logging.basicConfig(
    format=config.LOG_FORMAT,
    level=getattr(logging, config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)


# ============================================================================
# TRANSLATION ENGINES
# ============================================================================

class Translator(ABC):
    """Abstract base class for translators"""
    
    @abstractmethod
    def translate(self, text: str) -> str:
        pass


class GoogleTranslator(Translator):
    """Google Translate (via deep-translator)"""
    
    def __init__(self):
        from deep_translator import GoogleTranslator as GT
        self.translator = GT(source=config.SOURCE_LANGUAGE, target=config.TARGET_LANGUAGE)
    
    def translate(self, text: str) -> str:
        try:
            if len(text) > config.MAX_TRANSLATION_LENGTH:
                chunks = [text[i:i+config.MAX_TRANSLATION_LENGTH] 
                         for i in range(0, len(text), config.MAX_TRANSLATION_LENGTH)]
                return ' '.join([self.translator.translate(chunk) for chunk in chunks])
            return self.translator.translate(text)
        except Exception as e:
            logger.error(f"Google translation error: {e}")
            return text


class DeepLTranslator(Translator):
    """DeepL API - Best quality, requires API key"""
    
    def __init__(self, api_key: str):
        import deepl
        self.translator = deepl.Translator(api_key)
        # Map language codes to DeepL format
        self.source = config.SOURCE_LANGUAGE.upper()
        self.target = config.TARGET_LANGUAGE.upper()
    
    def translate(self, text: str) -> str:
        try:
            result = self.translator.translate_text(
                text, 
                source_lang=self.source, 
                target_lang=self.target
            )
            return result.text
        except Exception as e:
            logger.error(f"DeepL translation error: {e}")
            return text


class OpenAITranslator(Translator):
    """OpenAI ChatGPT - High quality, requires API key"""
    
    def __init__(self, api_key: str, model: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.source_lang = self._get_language_name(config.SOURCE_LANGUAGE)
        self.target_lang = self._get_language_name(config.TARGET_LANGUAGE)
    
    def _get_language_name(self, code: str) -> str:
        """Convert language code to full name"""
        lang_map = {
            'hu': 'Hungarian', 'ru': 'Russian', 'en': 'English',
            'de': 'German', 'fr': 'French', 'es': 'Spanish',
            'it': 'Italian', 'pt': 'Portuguese', 'pl': 'Polish'
        }
        return lang_map.get(code.lower(), code)
    
    def translate(self, text: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a professional translator. Translate the following {self.source_lang} text to {self.target_lang}. Preserve the tone, style, and formatting. Provide ONLY the translation, no explanations."
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI translation error: {e}")
            return text


class AnthropicTranslator(Translator):
    """Anthropic Claude - High quality, requires API key"""
    
    def __init__(self, api_key: str, model: str):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.source_lang = self._get_language_name(config.SOURCE_LANGUAGE)
        self.target_lang = self._get_language_name(config.TARGET_LANGUAGE)
    
    def _get_language_name(self, code: str) -> str:
        """Convert language code to full name"""
        lang_map = {
            'hu': 'Hungarian', 'ru': 'Russian', 'en': 'English',
            'de': 'German', 'fr': 'French', 'es': 'Spanish',
            'it': 'Italian', 'pt': 'Portuguese', 'pl': 'Polish'
        }
        return lang_map.get(code.lower(), code)
    
    def translate(self, text: str) -> str:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": f"Translate this {self.source_lang} text to {self.target_lang}. Preserve tone and style. Provide ONLY the translation:\n\n{text}"
                    }
                ]
            )
            return message.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic translation error: {e}")
            return text


class LibreTranslator(Translator):
    """LibreTranslate - Free and open source"""
    
    def __init__(self, api_url: str):
        import requests
        self.api_url = api_url
        self.session = requests.Session()
    
    def translate(self, text: str) -> str:
        try:
            response = self.session.post(self.api_url, json={
                "q": text,
                "source": config.SOURCE_LANGUAGE,
                "target": config.TARGET_LANGUAGE,
                "format": "text"
            })
            return response.json()["translatedText"]
        except Exception as e:
            logger.error(f"LibreTranslate error: {e}")
            return text


class MyMemoryTranslator(Translator):
    """MyMemory Translation API - Free, no API key needed"""
    
    def __init__(self):
        from deep_translator import MyMemoryTranslator as MMT
        self.translator = MMT(source=config.SOURCE_LANGUAGE, target=config.TARGET_LANGUAGE)
    
    def translate(self, text: str) -> str:
        try:
            if len(text) > 500:
                chunks = [text[i:i+500] for i in range(0, len(text), 500)]
                return ' '.join([self.translator.translate(chunk) for chunk in chunks])
            return self.translator.translate(text)
        except Exception as e:
            logger.error(f"MyMemory translation error: {e}")
            return text


# ============================================================================
# TRANSLATOR FACTORY
# ============================================================================

def create_translator() -> Translator:
    """Create translator instance based on config"""
    translator_type = config.TRANSLATOR_TYPE.lower()
    
    if translator_type == "google":
        logger.info("Using Google Translate")
        return GoogleTranslator()
        
    elif translator_type == "mymemory":
        logger.info("Using MyMemory Translator")
        return MyMemoryTranslator()
        
    elif translator_type == "libretranslate":
        logger.info("Using LibreTranslate")
        return LibreTranslator(api_url=config.LIBRETRANSLATE_API_URL)
        
    elif translator_type == "deepl":
        logger.info("Using DeepL")
        if config.DEEPL_API_KEY == "your-deepl-key-here":
            raise ValueError("Please set DEEPL_API_KEY in config.py")
        return DeepLTranslator(api_key=config.DEEPL_API_KEY)
        
    elif translator_type == "openai":
        logger.info(f"Using OpenAI ({config.OPENAI_MODEL})")
        if config.OPENAI_API_KEY == "your-openai-key-here":
            raise ValueError("Please set OPENAI_API_KEY in config.py")
        return OpenAITranslator(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL
        )
        
    elif translator_type == "anthropic":
        logger.info(f"Using Anthropic Claude ({config.ANTHROPIC_MODEL})")
        if config.ANTHROPIC_API_KEY == "your-anthropic-key-here":
            raise ValueError("Please set ANTHROPIC_API_KEY in config.py")
        return AnthropicTranslator(
            api_key=config.ANTHROPIC_API_KEY,
            model=config.ANTHROPIC_MODEL
        )
    
    else:
        raise ValueError(f"Unknown translator type: {translator_type}")


# ============================================================================
# RSS BOT
# ============================================================================

class RSSBot:
    def __init__(self, telegram_token, chat_id, rss_url, translator: Translator, check_interval):
        """
        Initialize the RSS bot
        
        Args:
            telegram_token: Your Telegram Bot API token
            chat_id: Telegram chat ID or channel username
            rss_url: URL of the RSS feed to monitor
            translator: Translator instance
            check_interval: Seconds between feed checks
        """
        self.bot = Bot(token=telegram_token)
        self.chat_id = chat_id
        self.rss_url = rss_url
        self.check_interval = check_interval
        self.seen_entries = set()
        self.translator = translator
        
    def get_entry_id(self, entry):
        """Generate a unique ID for an RSS entry"""
        if hasattr(entry, 'id'):
            return entry.id
        elif hasattr(entry, 'link'):
            return entry.link
        else:
            content = f"{entry.title}{entry.get('published', '')}"
            return hashlib.md5(content.encode()).hexdigest()
    
    def format_message(self, entry):
        """Format and translate RSS entry for Telegram"""
        # Translate title
        title = self.translator.translate(entry.title)
        
        # Translate summary/description if available
        description = ""
        if hasattr(entry, 'summary'):
            import re
            clean_summary = re.sub('<[^<]+?>', '', entry.summary)
            # Limit description length for translation
            description = self.translator.translate(clean_summary[:config.MAX_DESCRIPTION_LENGTH])
        
        # Get link
        link = entry.link if hasattr(entry, 'link') else ""
        
        # Format message
        message = f"📰 <b>{title}</b>\n\n"
        if description:
            message += f"{description}\n\n"
        if link:
            message += f"🔗 <a href='{link}'>Читать полностью</a>"
        
        return message
    
    async def send_message(self, text):
        """Send message to Telegram chat"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            logger.info("Message sent successfully")
        except TelegramError as e:
            logger.error(f"Failed to send message: {e}")
    
    async def check_feed(self):
        """Check RSS feed for new entries"""
        try:
            logger.info(f"Checking feed: {self.rss_url}")
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning: {feed.bozo_exception}")
            
            # Process entries in reverse order (oldest first)
            new_entries = []
            for entry in reversed(feed.entries):
                entry_id = self.get_entry_id(entry)
                if entry_id not in self.seen_entries:
                    new_entries.append(entry)
                    self.seen_entries.add(entry_id)
            
            # Send new entries
            for entry in new_entries:
                message = self.format_message(entry)
                await self.send_message(message)
                await asyncio.sleep(config.MESSAGE_DELAY)
            
            if new_entries:
                logger.info(f"Processed {len(new_entries)} new entries")
            else:
                logger.info("No new entries found")
                
        except Exception as e:
            logger.error(f"Error checking feed: {e}")
    
    async def start(self):
        """Start the bot and continuously monitor the feed"""
        logger.info("Starting RSS bot...")
        logger.info(f"Feed: {self.rss_url}")
        logger.info(f"Target: {self.chat_id}")
        logger.info(f"Translator: {self.translator.__class__.__name__}")
        logger.info(f"Check interval: {self.check_interval} seconds")
        
        # Initial feed check to populate seen_entries
        await self.check_feed()
        
        # Continuous monitoring loop
        while True:
            await asyncio.sleep(self.check_interval)
            await self.check_feed()
    
    async def run_once(self):
        """Run a single check (useful for testing)"""
        await self.check_feed()


# ============================================================================
# MAIN
# ============================================================================

async def main():
    # Create translator from config
    translator = create_translator()
    
    # Create and start bot
    bot = RSSBot(
        telegram_token=config.TELEGRAM_TOKEN,
        chat_id=config.CHAT_ID,
        rss_url=config.RSS_URL,
        translator=translator,
        check_interval=config.CHECK_INTERVAL
    )
    
    # Start continuous monitoring
    await bot.start()
    
    # Or for testing, run once:
    # await bot.run_once()


if __name__ == "__main__":
    asyncio.run(main())
