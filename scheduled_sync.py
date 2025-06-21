#!/usr/bin/env python3
"""
scheduled_sync.py
==================
Run a scheduled sync of all Telegram chat history using a user account (not bot),
and store them encrypted in the local database for use by the Telegram Manager Bot.

- Reads credentials from environment variables or .env file:
    TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
- By default, syncs all chats every day at 3:00am.

Usage:
  python scheduled_sync.py

To test immediately, run with --now:
  python scheduled_sync.py --now
"""
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import schedule
from chat_history_manager import ChatHistoryManager

# Load environment variables
load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')
SYNC_LIMIT = int(os.getenv('SYNC_LIMIT', '100000'))
SYNC_TIME = os.getenv('SYNC_TIME', '03:00')  # 24h format

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)

def sync_all_chats():
    logger.info('Starting scheduled chat history sync...')
    if not (API_ID and API_HASH and PHONE):
        logger.error('Missing TELEGRAM_API_ID, TELEGRAM_API_HASH, or TELEGRAM_PHONE in environment.')
        return
    manager = ChatHistoryManager()
    result = manager.fetch_full_chat_history(
        api_id=API_ID,
        api_hash=API_HASH,
        phone=PHONE,
        chat_id=None,
        limit=SYNC_LIMIT
    )
    if result.get('messages'):
        logger.info(f'Fetched {len(result["messages"])} messages. Storing...')
        success = manager.store_encrypted_history({
            'messages': result['messages'],
            'chat_id': 'all',
            'chat_name': 'All Chats',
            'chat_type': 'unknown',
        })
        if success:
            logger.info('✅ Scheduled sync and storage complete!')
        else:
            logger.error('❌ Failed to store messages.')
    else:
        logger.error(f'❌ No messages fetched: {result.get("error", "Unknown error")}')

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Run scheduled Telegram chat history sync.')
    parser.add_argument('--now', action='store_true', help='Run sync immediately and exit')
    args = parser.parse_args()

    if args.now:
        sync_all_chats()
        return

    logger.info(f'Scheduling daily sync at {SYNC_TIME}...')
    schedule.every().day.at(SYNC_TIME).do(sync_all_chats)
    logger.info('Scheduled sync running. Press Ctrl+C to stop.')
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == '__main__':
    main() 