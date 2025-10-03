import asyncio
import feedparser
import hashlib
import argparse
import os
from telegram import Bot
from telegram.error import TelegramError
import logging
from abc import ABC, abstractmethod


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
    
    def __init__(self, source_lang: str, target_lang: str):
        from deep_translator import GoogleTranslator as GT
        self.translator = GT(source=source_lang, target=target_lang)
        self.max_length = 5000
    
    def translate(self, text: str) -> str:
        try:
            if len(text) > self.max_length:
                chunks = [text[i:i+self.max_length] 
                         for i in range(0, len(text), self.max_length)]
                return ' '.join([self.translator.translate(chunk) for chunk in chunks])
            return self.translator.translate(text)
        except Exception as e:
            logging.error(f"Google translation error: {e}")
            return text


class DeepLTranslator(Translator):
    """DeepL API - Best quality, requires API key"""
    
    def __init__(self, api_key: str, source_lang: str, target_lang: str):
        import deepl
        self.translator = deepl.Translator(api_key)
        self.source = source_lang.upper()
        self.target = target_lang.upper()
    
    def translate(self, text: str) -> str:
        try:
            result = self.translator.translate_text(
                text, 
                source_lang=self.source, 
                target_lang=self.target
            )
            return result.text
        except Exception as e:
            logging.error(f"DeepL translation error: {e}")
            return text


class OpenAITranslator(Translator):
    """OpenAI ChatGPT - High quality, requires API key"""
    
    def __init__(self, api_key: str, source_lang: str, target_lang: str, model: str = "gpt-4o-mini"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.source_lang = self._get_language_name(source_lang)
        self.target_lang = self._get_language_name(target_lang)
    
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
            logging.error(f"OpenAI translation error: {e}")
            return text


class AnthropicTranslator(Translator):
    """Anthropic Claude - High quality, requires API key"""
    
    def __init__(self, api_key: str, source_lang: str, target_lang: str, model: str = "claude-3-5-haiku-20241022"):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.source_lang = self._get_language_name(source_lang)
        self.target_lang = self._get_language_name(target_lang)
    
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
            logging.error(f"Anthropic translation error: {e}")
            return text


class LibreTranslator(Translator):
    """LibreTranslate - Free and open source"""
    
    def __init__(self, source_lang: str, target_lang: str, api_url: str = "https://libretranslate.com/translate"):
        import requests
        self.api_url = api_url
        self.session = requests.Session()
        self.source = source_lang
        self.target = target_lang
    
    def translate(self, text: str) -> str:
        try:
            response = self.session.post(self.api_url, json={
                "q": text,
                "source": self.source,
                "target": self.target,
                "format": "text"
            })
            return response.json()["translatedText"]
        except Exception as e:
            logging.error(f"LibreTranslate error: {e}")
            return text


class MyMemoryTranslator(Translator):
    """MyMemory Translation API - Free, no API key needed"""
    
    def __init__(self, source_lang: str, target_lang: str):
        from deep_translator import MyMemoryTranslator as MMT
        self.translator = MMT(source=source_lang, target=target_lang)
    
    def translate(self, text: str) -> str:
        try:
            if len(text) > 500:
                chunks = [text[i:i+500] for i in range(0, len(text), 500)]
                return ' '.join([self.translator.translate(chunk) for chunk in chunks])
            return self.translator.translate(text)
        except Exception as e:
            logging.error(f"MyMemory translation error: {e}")
            return text


# ============================================================================
# TRANSLATOR FACTORY
# ============================================================================

def create_translator(translator_type: str, source_lang: str, target_lang: str, 
                      api_key: str = None, model: str = None, api_url: str = None) -> Translator:
    """Create translator instance based on type"""
    translator_type = translator_type.lower()
    
    if translator_type == "google":
        logging.info("Using Google Translate")
        return GoogleTranslator(source_lang, target_lang)
        
    elif translator_type == "mymemory":
        logging.info("Using MyMemory Translator")
        return MyMemoryTranslator(source_lang, target_lang)
        
    elif translator_type == "libretranslate":
        logging.info("Using LibreTranslate")
        return LibreTranslator(source_lang, target_lang, api_url or "https://libretranslate.com/translate")
        
    elif translator_type == "deepl":
        logging.info("Using DeepL")
        if not api_key:
            raise ValueError("DeepL requires API key. Use --deepl-key or DEEPL_API_KEY env variable")
        return DeepLTranslator(api_key, source_lang, target_lang)
        
    elif translator_type == "openai":
        logging.info(f"Using OpenAI ({model or 'gpt-4o-mini'})")
        if not api_key:
            raise ValueError("OpenAI requires API key. Use --openai-key or OPENAI_API_KEY env variable")
        return OpenAITranslator(api_key, source_lang, target_lang, model or "gpt-4o-mini")
        
    elif translator_type == "anthropic":
        logging.info(f"Using Anthropic Claude ({model or 'claude-3-5-haiku-20241022'})")
        if not api_key:
            raise ValueError("Anthropic requires API key. Use --anthropic-key or ANTHROPIC_API_KEY env variable")
        return AnthropicTranslator(api_key, source_lang, target_lang, model or "claude-3-5-haiku-20241022")
    
    else:
        raise ValueError(f"Unknown translator type: {translator_type}")


# ============================================================================
# RSS BOT
# ============================================================================

class RSSBot:
    def __init__(self, telegram_token, chat_id, rss_url, translator: Translator, 
                 check_interval, max_description_length=500, max_content_length=5000):
        """
        Initialize the RSS bot
        
        Args:
            telegram_token: Your Telegram Bot API token
            chat_id: Telegram chat ID or channel username
            rss_url: URL of the RSS feed to monitor
            translator: Translator instance
            check_interval: Seconds between feed checks
            max_description_length: Max chars for description
            max_content_length: Max chars for content
        """
        self.bot = Bot(token=telegram_token)
        self.chat_id = chat_id
        self.rss_url = rss_url
        self.check_interval = check_interval
        self.seen_entries = set()
        self.translator = translator
        self.max_description_length = max_description_length
        self.max_content_length = max_content_length
        
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
        import re
        
        # Translate title
        title = self.translator.translate(entry.title)
        
        # Extract and translate description (use as header/summary)
        header = ""
        if hasattr(entry, 'summary') or hasattr(entry, 'description'):
            raw_description = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            # Clean HTML tags
            clean_description = re.sub('<[^<]+?>', '', raw_description)
            # Remove "The post ... first appeared on ..." footer
            clean_description = re.sub(r'The post.*?first appeared on.*', '', clean_description, flags=re.DOTALL)
            clean_description = clean_description.strip()
            
            if clean_description and len(clean_description) > 10:
                # Limit length and translate
                header = self.translator.translate(clean_description[:self.max_description_length])
        
        # Extract and translate main content from content:encoded
        main_content = ""
        if hasattr(entry, 'content'):
            # feedparser stores content in entry.content as a list of dicts
            for content_item in entry.content:
                if content_item.get('type') == 'text/html':
                    raw_content = content_item.get('value', '')
                    # Clean HTML tags
                    clean_content = re.sub('<[^<]+?>', '', raw_content)
                    # Remove extra whitespace
                    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                    # Remove "The post ... first appeared on ..." footer
                    clean_content = re.sub(r'The post.*?first appeared on.*', '', clean_content, flags=re.DOTALL)
                    clean_content = clean_content.strip()
                    
                    if clean_content and len(clean_content) > 10:
                        # Translate content (limit to reasonable length)
                        if len(clean_content) > self.max_content_length:
                            clean_content = clean_content[:self.max_content_length] + "..."
                        main_content = self.translator.translate(clean_content)
                    break
        
        # Get link
        link = entry.link if hasattr(entry, 'link') else ""
        
        # Format message with emphasis on description as header
        message = f"📰 <b>{title}</b>\n\n"
        
        # Add description as prominent header/summary
        if header:
            message += f"<b><i>{header}</i></b>\n\n"
        
        # Add main content if available
        if main_content:
            message += f"{main_content}\n\n"
        
        # Add link
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
            logging.info("Message sent successfully")
        except TelegramError as e:
            logging.error(f"Failed to send message: {e}")
    
    async def check_feed(self):
        """Check RSS feed for new entries"""
        try:
            logging.info(f"Checking feed: {self.rss_url}")
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:
                logging.warning(f"Feed parsing warning: {feed.bozo_exception}")
            
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
                await asyncio.sleep(2)
            
            if new_entries:
                logging.info(f"Processed {len(new_entries)} new entries")
            else:
                logging.info("No new entries found")
                
        except Exception as e:
            logging.error(f"Error checking feed: {e}")
    
    async def start(self):
        """Start the bot and continuously monitor the feed"""
        logging.info("Starting RSS bot...")
        logging.info(f"Feed: {self.rss_url}")
        logging.info(f"Target: {self.chat_id}")
        logging.info(f"Translator: {self.translator.__class__.__name__}")
        logging.info(f"Check interval: {self.check_interval} seconds")
        
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
# COMMAND LINE INTERFACE
# ============================================================================

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Telegram RSS Bot - Translate and post RSS feeds to Telegram',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using Google Translate (free)
  python rss_bot.py --token "YOUR_TOKEN" --chat "@channel" --feed "https://24.hu/feed/"
  
  # Using DeepL
  python rss_bot.py --token "YOUR_TOKEN" --chat "@channel" --feed "https://24.hu/feed/" \\
    --translator deepl --deepl-key "YOUR_DEEPL_KEY"
  
  # Using OpenAI
  python rss_bot.py --token "YOUR_TOKEN" --chat "@channel" --feed "https://24.hu/feed/" \\
    --translator openai --openai-key "YOUR_OPENAI_KEY"
  
  # Using environment variables
  export TELEGRAM_TOKEN="YOUR_TOKEN"
  export CHAT_ID="@channel"
  python rss_bot.py --feed "https://24.hu/feed/"

Environment variables:
  TELEGRAM_TOKEN    - Telegram bot token
  CHAT_ID          - Channel username or chat ID
  RSS_URL          - RSS feed URL
  DEEPL_API_KEY    - DeepL API key
  OPENAI_API_KEY   - OpenAI API key
  ANTHROPIC_API_KEY - Anthropic API key
        """
    )
    
    # Required arguments (can be set via env vars)
    parser.add_argument('--token', '-t',
                        default=os.getenv('TELEGRAM_TOKEN'),
                        help='Telegram bot token (or set TELEGRAM_TOKEN env var)')
    
    parser.add_argument('--chat', '-c',
                        default=os.getenv('CHAT_ID'),
                        help='Channel username (@channel) or chat ID (or set CHAT_ID env var)')
    
    parser.add_argument('--feed', '-f',
                        default=os.getenv('RSS_URL', 'https://24.hu/feed/'),
                        help='RSS feed URL (default: https://24.hu/feed/)')
    
    # Translation settings
    parser.add_argument('--translator', '-tr',
                        default=os.getenv('TRANSLATOR_TYPE', 'google'),
                        choices=['google', 'deepl', 'openai', 'anthropic', 'libretranslate', 'mymemory'],
                        help='Translation engine (default: google)')
    
    parser.add_argument('--source-lang', '-sl',
                        default=os.getenv('SOURCE_LANGUAGE', 'hu'),
                        help='Source language code (default: hu)')
    
    parser.add_argument('--target-lang', '-tl',
                        default=os.getenv('TARGET_LANGUAGE', 'ru'),
                        help='Target language code (default: ru)')
    
    # API keys
    parser.add_argument('--deepl-key',
                        default=os.getenv('DEEPL_API_KEY'),
                        help='DeepL API key')
    
    parser.add_argument('--openai-key',
                        default=os.getenv('OPENAI_API_KEY'),
                        help='OpenAI API key')
    
    parser.add_argument('--openai-model',
                        default=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                        help='OpenAI model (default: gpt-4o-mini)')
    
    parser.add_argument('--anthropic-key',
                        default=os.getenv('ANTHROPIC_API_KEY'),
                        help='Anthropic API key')
    
    parser.add_argument('--anthropic-model',
                        default=os.getenv('ANTHROPIC_MODEL', 'claude-3-5-haiku-20241022'),
                        help='Anthropic model (default: claude-3-5-haiku-20241022)')
    
    parser.add_argument('--libretranslate-url',
                        default=os.getenv('LIBRETRANSLATE_API_URL', 'https://libretranslate.com/translate'),
                        help='LibreTranslate API URL')
    
    # Bot settings
    parser.add_argument('--interval', '-i',
                        type=int,
                        default=int(os.getenv('CHECK_INTERVAL', '300')),
                        help='Check interval in seconds (default: 300)')
    
    parser.add_argument('--max-description',
                        type=int,
                        default=int(os.getenv('MAX_DESCRIPTION_LENGTH', '500')),
                        help='Max description length (default: 500)')
    
    parser.add_argument('--max-content',
                        type=int,
                        default=int(os.getenv('MAX_CONTENT_LENGTH', '5000')),
                        help='Max content length (default: 5000)')
    
    # Other options
    parser.add_argument('--once',
                        action='store_true',
                        help='Run once and exit (for testing)')
    
    parser.add_argument('--log-level',
                        default=os.getenv('LOG_LEVEL', 'INFO'),
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level (default: INFO)')
    
    return parser.parse_args()


# ============================================================================
# MAIN
# ============================================================================

async def main():
    args = parse_args()
    
    # Configure logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, args.log_level)
    )
    
    # Validate required arguments
    if not args.token:
        logging.error("Telegram token is required. Use --token or set TELEGRAM_TOKEN env var")
        return
    
    if not args.chat:
        logging.error("Chat ID is required. Use --chat or set CHAT_ID env var")
        return
    
    # Select API key based on translator
    api_key = None
    model = None
    api_url = None
    
    if args.translator == 'deepl':
        api_key = args.deepl_key
    elif args.translator == 'openai':
        api_key = args.openai_key
        model = args.openai_model
    elif args.translator == 'anthropic':
        api_key = args.anthropic_key
        model = args.anthropic_model
    elif args.translator == 'libretranslate':
        api_url = args.libretranslate_url
    
    # Create translator
    translator = create_translator(
        args.translator,
        args.source_lang,
        args.target_lang,
        api_key,
        model,
        api_url
    )
    
    # Create bot
    bot = RSSBot(
        telegram_token=args.token,
        chat_id=args.chat,
        rss_url=args.feed,
        translator=translator,
        check_interval=args.interval,
        max_description_length=args.max_description,
        max_content_length=args.max_content
    )
    
    # Run bot
    if args.once:
        logging.info("Running single check...")
        await bot.run_once()
    else:
        await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
