#!/usr/bin/env python3
"""
Telegram RSS Bot with auto-deletion of old messages.

This bot monitors RSS feeds, translates articles, posts them to Telegram,
and automatically deletes old messages to keep the channel clean.
"""

import asyncio
import feedparser
import hashlib
import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dotenv import load_dotenv

from telegram import Bot
from telegram.error import TelegramError
import logging
from abc import ABC, abstractmethod

# Load .env file before anything else
load_dotenv()


# ============================================================================
# MESSAGE TRACKING
# ============================================================================

class MessageTracker:
    """Track sent messages with timestamps for auto-deletion."""
    
    def __init__(self, storage_file: str = "message_history.json"):
        """
        Initialize message tracker.
        
        Args:
            storage_file: Path to JSON file for storing message history
        """
        self.storage_file = Path(storage_file)
        self.messages: List[Dict] = []
        self._load()
    
    def _load(self) -> None:
        """Load message history from file."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
                logging.info(f"Loaded {len(self.messages)} messages from history")
            except Exception as e:
                logging.error(f"Failed to load message history: {e}")
                self.messages = []
        else:
            self.messages = []
    
    def _save(self) -> None:
        """Save message history to file."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save message history: {e}")
    
    def add_message(self, message_id: int, timestamp: Optional[datetime] = None) -> None:
        """
        Add a sent message to tracking.
        
        Args:
            message_id: Telegram message ID
            timestamp: Message timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        self.messages.append({
            'message_id': message_id,
            'timestamp': timestamp.isoformat()
        })
        self._save()
        logging.debug(f"Tracked message {message_id}")
    
    def get_old_messages(self, max_age_hours: int) -> List[int]:
        """
        Get message IDs older than specified hours.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            List of message IDs to delete
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        old_messages = []
        
        for msg in self.messages:
            msg_time = datetime.fromisoformat(msg['timestamp'])
            if msg_time < cutoff:
                old_messages.append(msg['message_id'])
        
        return old_messages
    
    def remove_messages(self, message_ids: List[int]) -> None:
        """
        Remove messages from tracking after deletion.
        
        Args:
            message_ids: List of message IDs that were deleted
        """
        self.messages = [
            msg for msg in self.messages 
            if msg['message_id'] not in message_ids
        ]
        self._save()
        logging.info(f"Removed {len(message_ids)} messages from tracking")
    
    def get_stats(self) -> Dict:
        """Get statistics about tracked messages."""
        if not self.messages:
            return {
                'total': 0,
                'oldest': None,
                'newest': None
            }
        
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in self.messages]
        return {
            'total': len(self.messages),
            'oldest': min(timestamps).isoformat(),
            'newest': max(timestamps).isoformat()
        }


# ============================================================================
# TRANSLATION ENGINES
# ============================================================================

class Translator(ABC):
    """Abstract base class for translators."""
    
    @abstractmethod
    def translate(self, text: str) -> str:
        """Translate text."""
        pass


class GoogleTranslator(Translator):
    """Google Translate (via deep-translator)."""
    
    def __init__(self, source_lang: str, target_lang: str):
        from deep_translator import GoogleTranslator as GT
        self.translator = GT(source=source_lang, target=target_lang)
        self.max_length = 3000
    
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
    """DeepL API - Best quality, requires API key."""
    
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
    """OpenAI ChatGPT - High quality, requires API key."""
    
    def __init__(self, api_key: str, source_lang: str, target_lang: str, 
                 model: str = "gpt-4o-mini"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.source_lang = self._get_language_name(source_lang)
        self.target_lang = self._get_language_name(target_lang)
    
    def _get_language_name(self, code: str) -> str:
        """Convert language code to full name."""
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
                        "content": f"You are a professional translator. Translate the following {self.source_lang} text to {self.target_lang}. Follow these rules:\n"
                                f"1. Preserve the tone, style, and formatting\n"
                                f"2. Do NOT translate proper nouns: keep names of people, places, organizations, and brands in their original form\n"
                                f"3. Provide ONLY the translation, no explanations"
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
    """Anthropic Claude - High quality, requires API key."""
    
    def __init__(self, api_key: str, source_lang: str, target_lang: str, 
                 model: str = "claude-3-5-haiku-20241022"):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.source_lang = self._get_language_name(source_lang)
        self.target_lang = self._get_language_name(target_lang)
    
    def _get_language_name(self, code: str) -> str:
        """Convert language code to full name."""
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
                        "content": f"Translate the following {self.source_lang} text to {self.target_lang}.\n\n"
                                f"Rules:\n"
                                f"1. Preserve the tone, style, and formatting\n"
                                f"2. Do NOT translate proper nouns: keep names of people, places, organizations, and brands in their original form\n"
                                f"3. Provide ONLY the translation, no explanations\n\n"
                                f"Text to translate:\n{text}"
                    }
                ]
            )
            return message.content[0].text.strip()
        except Exception as e:
            logging.error(f"Anthropic translation error: {e}")
            return text


class LibreTranslator(Translator):
    """LibreTranslate - Free and open source."""
    
    def __init__(self, source_lang: str, target_lang: str, 
                 api_url: str = "https://libretranslate.com/translate"):
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
    """MyMemory Translation API - Free, no API key needed."""
    
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
                      api_key: Optional[str] = None, model: Optional[str] = None, 
                      api_url: Optional[str] = None) -> Translator:
    """Create translator instance based on type."""
    translator_type = translator_type.lower()
    
    if translator_type == "google":
        logging.info("Using Google Translate")
        return GoogleTranslator(source_lang, target_lang)
        
    elif translator_type == "mymemory":
        logging.info("Using MyMemory Translator")
        return MyMemoryTranslator(source_lang, target_lang)
        
    elif translator_type == "libretranslate":
        logging.info("Using LibreTranslate")
        return LibreTranslator(source_lang, target_lang, 
                              api_url or "https://libretranslate.com/translate")
        
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
        return AnthropicTranslator(api_key, source_lang, target_lang, 
                                  model or "claude-3-5-haiku-20241022")
    
    else:
        raise ValueError(f"Unknown translator type: {translator_type}")


# ============================================================================
# RSS BOT
# ============================================================================

class RSSBot:
    """RSS Bot with automatic message cleanup."""
    
    def __init__(self, telegram_token: str, chat_id: str, rss_url: str, 
                 translator: Translator, check_interval: int, 
                 max_description_length: int = 500, max_content_length: int = 3000,
                 delete_after_hours: Optional[int] = None, 
                 max_messages_to_keep: Optional[int] = None):
        """
        Initialize the RSS bot.
        
        Args:
            telegram_token: Your Telegram Bot API token
            chat_id: Telegram chat ID or channel username
            rss_url: URL of the RSS feed to monitor
            translator: Translator instance
            check_interval: Seconds between feed checks
            max_description_length: Max chars for description
            max_content_length: Max chars for content
            delete_after_hours: Delete messages older than N hours (None = disabled)
            max_messages_to_keep: Keep only N most recent messages (None = unlimited)
        """
        self.bot = Bot(token=telegram_token)
        self.chat_id = chat_id
        self.rss_url = rss_url
        self.check_interval = check_interval
        self.seen_entries: Set[str] = set()
        self.translator = translator
        self.max_description_length = max_description_length
        self.max_content_length = max_content_length
        self.delete_after_hours = delete_after_hours
        self.max_messages_to_keep = max_messages_to_keep
        self.message_tracker = MessageTracker()
        
    def get_entry_id(self, entry) -> str:
        """Generate a unique ID for an RSS entry."""
        if hasattr(entry, 'id'):
            return entry.id
        elif hasattr(entry, 'link'):
            return entry.link
        else:
            content = f"{entry.title}{entry.get('published', '')}"
            return hashlib.md5(content.encode()).hexdigest()
    
    def format_message(self, entry) -> str:
        """Format and translate RSS entry for Telegram."""
        import re
        
        # Translate title
        title = self.translator.translate(entry.title)
        
        # Extract and translate description (use as header/summary)
        header = ""
        if hasattr(entry, 'summary') or hasattr(entry, 'description'):
            raw_description = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            clean_description = re.sub('<[^<]+?>', '', raw_description)
            clean_description = re.sub(r'The post.*?first appeared on.*', '', 
                                      clean_description, flags=re.DOTALL)
            clean_description = clean_description.strip()
            
            if clean_description and len(clean_description) > 10:
                header = self.translator.translate(clean_description[:self.max_description_length])
        
        # Extract and translate main content from content:encoded
        main_content = ""
        if hasattr(entry, 'content'):
            for content_item in entry.content:
                if content_item.get('type') == 'text/html':
                    raw_content = content_item.get('value', '')
                    clean_content = re.sub('<[^<]+?>', '', raw_content)
                    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                    clean_content = re.sub(r'The post.*?first appeared on.*', '', 
                                          clean_content, flags=re.DOTALL)
                    clean_content = clean_content.strip()
                    
                    if clean_content and len(clean_content) > 10:
                        if len(clean_content) > self.max_content_length:
                            clean_content = clean_content[:self.max_content_length] + "..."
                        main_content = self.translator.translate(clean_content)
                    break
        
        link = entry.link if hasattr(entry, 'link') else ""
        
        # Format message
        message = f"📰 <b>{title}</b>\n\n"
        
        if header:
            message += f"<b><i>{header}</i></b>\n\n"
        
        if main_content:
            message += f"{main_content}\n\n"
        
        if link:
            message += f"🔗 <a href='{link}'>Читать полностью</a>"
        
        return message
    
    async def send_message(self, text: str) -> Optional[int]:
        """
        Send message to Telegram chat.
        
        Returns:
            Message ID if successful, None otherwise
        """
        try:
            msg = await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            logging.info(f"Message sent successfully (ID: {msg.message_id})")
            return msg.message_id
        except TelegramError as e:
            logging.error(f"Failed to send message: {e}")
            return None
    
    async def delete_old_messages(self) -> None:
        """Delete old messages based on configured rules."""
        deleted_count = 0
        messages_to_delete: List[int] = []
        
        # Delete by age
        if self.delete_after_hours:
            old_messages = self.message_tracker.get_old_messages(self.delete_after_hours)
            messages_to_delete.extend(old_messages)
            logging.info(f"Found {len(old_messages)} messages older than {self.delete_after_hours} hours")
        
        # Delete by count (keep only N most recent)
        if self.max_messages_to_keep:
            stats = self.message_tracker.get_stats()
            total_messages = stats['total']
            if total_messages > self.max_messages_to_keep:
                # Sort messages by timestamp and get oldest ones to delete
                sorted_messages = sorted(
                    self.message_tracker.messages,
                    key=lambda m: m['timestamp']
                )
                excess_count = total_messages - self.max_messages_to_keep
                excess_messages = [m['message_id'] for m in sorted_messages[:excess_count]]
                messages_to_delete.extend(excess_messages)
                logging.info(f"Found {len(excess_messages)} excess messages (keeping {self.max_messages_to_keep})")
        
        # Remove duplicates
        messages_to_delete = list(set(messages_to_delete))
        
        # Delete messages
        for msg_id in messages_to_delete:
            try:
                await self.bot.delete_message(chat_id=self.chat_id, message_id=msg_id)
                deleted_count += 1
                logging.debug(f"Deleted message {msg_id}")
                await asyncio.sleep(0.1)  # Small delay to avoid rate limits
            except TelegramError as e:
                logging.warning(f"Failed to delete message {msg_id}: {e}")
        
        # Remove deleted messages from tracker
        if deleted_count > 0:
            self.message_tracker.remove_messages(messages_to_delete)
            logging.info(f"Successfully deleted {deleted_count} old messages")
    
    async def check_feed(self) -> None:
        """Check RSS feed for new entries."""
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
            
            # Send new entries and track them
            for entry in new_entries:
                message = self.format_message(entry)
                message_id = await self.send_message(message)
                if message_id:
                    self.message_tracker.add_message(message_id)
                await asyncio.sleep(2)
            
            if new_entries:
                logging.info(f"Processed {len(new_entries)} new entries")
                
                # Delete old messages after posting new ones
                if self.delete_after_hours or self.max_messages_to_keep:
                    await self.delete_old_messages()
            else:
                logging.info("No new entries found")
                
        except Exception as e:
            logging.error(f"Error checking feed: {e}")
    
    async def start(self) -> None:
        """Start the bot and continuously monitor the feed."""
        logging.info("Starting RSS bot...")
        logging.info(f"Feed: {self.rss_url}")
        logging.info(f"Target: {self.chat_id}")
        logging.info(f"Translator: {self.translator.__class__.__name__}")
        logging.info(f"Check interval: {self.check_interval} seconds")
        
        if self.delete_after_hours:
            logging.info(f"Auto-delete: Messages older than {self.delete_after_hours} hours")
        if self.max_messages_to_keep:
            logging.info(f"Auto-delete: Keep only {self.max_messages_to_keep} most recent messages")
        
        # Show current stats
        stats = self.message_tracker.get_stats()
        logging.info(f"Message tracker: {stats['total']} messages in history")
        
        # Initial feed check to populate seen_entries
        await self.check_feed()
        
        # Continuous monitoring loop
        while True:
            await asyncio.sleep(self.check_interval)
            await self.check_feed()
    
    async def run_once(self) -> None:
        """Run a single check (useful for testing)."""
        await self.check_feed()


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Telegram RSS Bot - Translate and post RSS feeds to Telegram with auto-cleanup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with auto-deletion after 48 hours
  python rss_bot.py --token "YOUR_TOKEN" --chat "@channel" --delete-after 48
  
  # Keep only 50 most recent messages
  python rss_bot.py --token "YOUR_TOKEN" --chat "@channel" --keep-messages 50
  
  # Both: delete after 24h AND keep max 100 messages
  python rss_bot.py --token "YOUR_TOKEN" --chat "@channel" --delete-after 24 --keep-messages 100

Environment variables:
  DELETE_AFTER_HOURS    - Delete messages older than N hours
  MAX_MESSAGES_TO_KEEP  - Keep only N most recent messages
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
                        default=int(os.getenv('MAX_CONTENT_LENGTH', '3000')),
                        help='Max content length (default: 3000)')
    
    # Auto-deletion settings
    parser.add_argument('--delete-after',
                        type=int,
                        default=int(os.getenv('DELETE_AFTER_HOURS', '0')) or None,
                        help='Delete messages older than N hours (0 = disabled)')
    
    parser.add_argument('--keep-messages',
                        type=int,
                        default=int(os.getenv('MAX_MESSAGES_TO_KEEP', '0')) or None,
                        help='Keep only N most recent messages (0 = unlimited)')
    
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
    """Main entry point."""
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
        max_content_length=args.max_content,
        delete_after_hours=args.delete_after,
        max_messages_to_keep=args.keep_messages
    )
    
    # Run bot
    if args.once:
        logging.info("Running single check...")
        await bot.run_once()
    else:
        await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
