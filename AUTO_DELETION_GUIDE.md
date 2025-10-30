# Auto-Deletion Feature Documentation

## Overview

The enhanced RSS bot now includes automatic message cleanup to prevent channel overflow. Messages are tracked and can be automatically deleted based on:

1. **Age** - Delete messages older than a specified time (hours)
2. **Count** - Keep only a specific number of most recent messages
3. **Both** - You can combine both rules

## How It Works

### Message Tracking

- Every message sent by the bot is tracked with a timestamp
- Tracking data is stored in `message_history.json`
- The file persists between bot restarts

### Deletion Strategy

**After each feed check session:**
1. Bot posts new articles
2. Bot checks which messages should be deleted:
   - Messages older than `DELETE_AFTER_HOURS` hours
   - Messages exceeding `MAX_MESSAGES_TO_KEEP` count
3. Bot deletes old messages
4. Bot updates the tracking file

## Configuration

### Using Environment Variables

```bash
# Delete messages older than 48 hours
export DELETE_AFTER_HOURS="48"

# Keep only 100 most recent messages
export MAX_MESSAGES_TO_KEEP="100"

# Run bot
source .env && python3 telegram_rss_bot_enhanced.py
```

### Using Command Line Arguments

```bash
# Delete messages older than 24 hours
python3 telegram_rss_bot_enhanced.py \
  --token "YOUR_TOKEN" \
  --chat "@yourchannel" \
  --delete-after 24

# Keep only 50 most recent messages
python3 telegram_rss_bot_enhanced.py \
  --token "YOUR_TOKEN" \
  --chat "@yourchannel" \
  --keep-messages 50

# Both rules together
python3 telegram_rss_bot_enhanced.py \
  --token "YOUR_TOKEN" \
  --chat "@yourchannel" \
  --delete-after 48 \
  --keep-messages 100
```

## Usage Examples

### Example 1: Time-Based Cleanup Only

Delete news older than 72 hours (3 days):

```bash
python3 telegram_rss_bot_enhanced.py \
  --token "YOUR_TOKEN" \
  --chat "@yourchannel" \
  --delete-after 72
```

**Use case:** Keep news relevant for 3 days, then remove it.

### Example 2: Count-Based Cleanup Only

Keep only the 200 most recent messages:

```bash
python3 telegram_rss_bot_enhanced.py \
  --token "YOUR_TOKEN" \
  --chat "@yourchannel" \
  --keep-messages 200
```

**Use case:** Maintain a fixed-size rolling window of news.

### Example 3: Combined Rules

Delete messages older than 24 hours OR keep only 50 messages (whichever comes first):

```bash
python3 telegram_rss_bot_enhanced.py \
  --token "YOUR_TOKEN" \
  --chat "@yourchannel" \
  --delete-after 24 \
  --keep-messages 50
```

**Use case:** Fast-moving news channel with both time and space constraints.

### Example 4: No Deletion (Default)

If you don't specify either parameter, no messages are deleted:

```bash
python3 telegram_rss_bot_enhanced.py \
  --token "YOUR_TOKEN" \
  --chat "@yourchannel"
```

## Recommended Settings

### High-Volume News Channel (50+ posts/day)
```bash
DELETE_AFTER_HOURS=24
MAX_MESSAGES_TO_KEEP=100
```
Keeps last 24 hours or 100 messages, whichever is less.

### Medium-Volume Channel (10-20 posts/day)
```bash
DELETE_AFTER_HOURS=48
MAX_MESSAGES_TO_KEEP=50
```
Keeps last 2 days or 50 messages.

### Low-Volume Archive Channel (1-5 posts/day)
```bash
DELETE_AFTER_HOURS=168  # 1 week
MAX_MESSAGES_TO_KEEP=0  # No limit
```
Keeps messages for a week, no count limit.

### Rolling News Ticker
```bash
DELETE_AFTER_HOURS=0     # No time limit
MAX_MESSAGES_TO_KEEP=20  # Only last 20
```
Always shows exactly the 20 most recent articles.

## Message History File

The bot stores tracking data in `message_history.json`:

```json
[
  {
    "message_id": 12345,
    "timestamp": "2025-10-30T10:30:00.123456"
  },
  {
    "message_id": 12346,
    "timestamp": "2025-10-30T10:35:00.123456"
  }
]
```

### File Management

- **Location:** Same directory as the bot script
- **Automatic:** Created on first message
- **Persistent:** Survives bot restarts
- **Safe to delete:** Bot will recreate it (but loses history)

### Backup

To backup message history:
```bash
cp message_history.json message_history.backup.json
```

## Bot Permissions

⚠️ **Important:** Your bot must have these permissions in the channel:

1. ✅ **Post messages** (to send news)
2. ✅ **Delete messages** (to remove old news)

Without "Delete messages" permission, the bot will log errors but continue posting.

### Setting Permissions

1. Open your channel in Telegram
2. Go to: Channel Info → Administrators
3. Find your bot
4. Enable: "Delete messages of others"

## Logging

The bot provides detailed logs:

```
2025-10-30 10:30:00 - INFO - Found 15 messages older than 48 hours
2025-10-30 10:30:01 - INFO - Found 5 excess messages (keeping 100)
2025-10-30 10:30:05 - INFO - Successfully deleted 20 old messages
```

Enable debug logging to see individual deletions:

```bash
python3 telegram_rss_bot_enhanced.py \
  --token "YOUR_TOKEN" \
  --chat "@yourchannel" \
  --delete-after 48 \
  --log-level DEBUG
```

## Migration from Old Bot

If you're upgrading from the old bot:

1. **Install the new version:**
   ```bash
   cp telegram_rss_bot_enhanced.py telegram_rss_bot.py
   ```

2. **No existing messages are tracked:**
   - The bot only tracks NEW messages it sends
   - Old messages in the channel won't be deleted
   - Message history builds up over time

3. **Manual cleanup (optional):**
   - Delete old messages manually if needed
   - Bot will start tracking from its next post

## Systemd Integration

Update your service file to include the new parameters:

```ini
[Service]
Environment="TELEGRAM_TOKEN=your-token"
Environment="CHAT_ID=@yourchannel"
Environment="DELETE_AFTER_HOURS=48"
Environment="MAX_MESSAGES_TO_KEEP=100"
ExecStart=/usr/bin/python3 /path/to/telegram_rss_bot_enhanced.py
```

Or use an `.env` file:

```ini
[Service]
EnvironmentFile=/path/to/.env
ExecStart=/usr/bin/python3 /path/to/telegram_rss_bot_enhanced.py
```

## Troubleshooting

### Messages Not Being Deleted

1. **Check bot permissions:**
   ```bash
   # Bot must be admin with "Delete messages" permission
   ```

2. **Check logs for errors:**
   ```bash
   python3 telegram_rss_bot_enhanced.py --log-level DEBUG
   ```

3. **Verify settings:**
   ```bash
   # Make sure values are > 0
   echo $DELETE_AFTER_HOURS
   echo $MAX_MESSAGES_TO_KEEP
   ```

### "Failed to delete message" Errors

**Possible causes:**
- Bot lacks permissions
- Message already deleted
- Message is a pinned message

**Solution:** Review bot permissions in channel settings.

### Message History Growing Too Large

The `message_history.json` file only contains message IDs and timestamps - very small.

If concerned:
```bash
# Check file size
ls -lh message_history.json

# Archive and reset
mv message_history.json message_history.$(date +%Y%m%d).json
# Bot will create new file
```

## Performance

### Impact on Bot

- **CPU:** Negligible (simple timestamp comparisons)
- **Memory:** ~100 bytes per tracked message
- **Network:** One API call per deleted message
- **Storage:** ~50 bytes per message in JSON file

### Rate Limits

The bot includes a small delay between deletions (0.1s) to avoid hitting Telegram's rate limits:

- ~600 deletions per minute
- ~36,000 deletions per hour

This is more than sufficient for typical RSS channels.

## FAQ

### Q: Can I disable auto-deletion temporarily?

**A:** Yes, set both parameters to 0:
```bash
python3 telegram_rss_bot_enhanced.py \
  --delete-after 0 \
  --keep-messages 0
```

### Q: What happens if I change the settings?

**A:** The bot immediately applies new rules on the next feed check.

### Q: Can I manually trigger cleanup?

**A:** Yes, use `--once` flag:
```bash
python3 telegram_rss_bot_enhanced.py --once --delete-after 24
```

### Q: Does deletion work retroactively?

**A:** Only for messages the bot has tracked. Pre-existing messages aren't tracked.

### Q: What if message_history.json is deleted?

**A:** Bot loses tracking data but continues normally. It will start tracking new messages.

## Advanced: Custom Cleanup Logic

You can modify the `delete_old_messages()` method in the code to implement custom deletion logic:

```python
async def delete_old_messages(self) -> None:
    """Delete old messages based on configured rules."""
    # Your custom logic here
    # Examples:
    # - Delete messages on specific days of the week
    # - Keep messages with certain keywords
    # - Progressive deletion (older = higher priority)
    pass
```

## Best Practices

1. **Start conservative:** Begin with longer retention (e.g., 72 hours)
2. **Monitor logs:** Watch deletion patterns for a few days
3. **Adjust gradually:** Fine-tune based on channel activity
4. **Backup tracking file:** Occasionally backup `message_history.json`
5. **Test with `--once`:** Test deletion settings in single-run mode first

## Support

If you encounter issues:
1. Check logs with `--log-level DEBUG`
2. Verify bot permissions
3. Review `message_history.json` for anomalies
4. Test with `--once` flag first
