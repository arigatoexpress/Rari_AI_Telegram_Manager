#!/usr/bin/env python3
"""
Chat History Manager with Encryption
====================================
Securely fetch, encrypt, store, and retrieve entire chat history for AI insights.
"""

import os
import json
import base64
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sqlite3
import threading
import logging
import asyncio
import concurrent.futures

# Telegram imports
try:
    from telethon import TelegramClient, events
    from telethon.tl.types import User, Chat, Channel
    from telethon.errors import SessionPasswordNeededError
except ImportError:
    print("⚠️  Telethon not installed. Install with: pip install telethon")
    TelegramClient = None

class ChatHistoryManager:
    """Manage encrypted chat history with secure storage and retrieval"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.root_dir = Path.cwd()
        self.data_dir = self.root_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Encryption setup
        key: Optional[str] = encryption_key or os.getenv('FERNET_KEY')
        if not self._is_valid_encryption_key(key):
            key = self._generate_and_store_encryption_key()
        assert isinstance(key, str) and self._is_valid_encryption_key(key), "Encryption key must be a valid Fernet key string."
        self.encryption_key: str = key
        self.cipher = Fernet(self.encryption_key.encode())
        
        # Database setup
        self.db_path = self.data_dir / "chat_history.db"
        self._init_database()
        
        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Thread safety
        self.lock = threading.Lock()
    
    def _is_valid_encryption_key(self, key: Optional[str]) -> bool:
        if not key or not isinstance(key, str):
            return False
        try:
            Fernet(key.encode())
            return True
        except Exception:
            return False
    
    def _generate_and_store_encryption_key(self) -> str:
        key = Fernet.generate_key().decode()
        print(f"🔑 Generated new Fernet encryption key: {key}")
        self._update_env_file('FERNET_KEY', key)
        print("✅ Updated .env with new ENCRYPTION_KEY. Please keep this key safe!")
        return key
    
    def _update_env_file(self, var: str, value: str):
        env_path = self.root_dir / '.env'
        if not env_path.exists():
            with open(env_path, 'w') as f:
                f.write(f'{var}={value}\n')
            return
        lines = []
        found = False
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip().startswith(f'{var}='):
                    lines.append(f'{var}={value}\n')
                    found = True
                else:
                    lines.append(line)
        if not found:
            lines.append(f'{var}={value}\n')
        with open(env_path, 'w') as f:
            f.writelines(lines)
    
    def _init_database(self):
        """Initialize encrypted SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    message_id INTEGER NOT NULL,
                    sender_id TEXT,
                    sender_name TEXT,
                    message_text TEXT,
                    timestamp DATETIME,
                    encrypted_data BLOB,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(chat_id, message_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_metadata (
                    chat_id TEXT PRIMARY KEY,
                    chat_name TEXT,
                    chat_type TEXT,
                    total_messages INTEGER DEFAULT 0,
                    last_updated DATETIME,
                    encryption_hash TEXT
                )
            """)
            
            conn.commit()
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt data"""
        return self.cipher.encrypt(data.encode())
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data"""
        return self.cipher.decrypt(encrypted_data).decode()
    
    def fetch_full_chat_history(
        self,
        api_id: str,
        api_hash: str,
        phone: str,
        chat_id: Optional[str] = None,
        limit: int = 10000
    ) -> Dict[str, Any]:
        """Fetch entire chat history using Telethon"""
        if not TelegramClient:
            raise ImportError("Telethon not installed. Run: pip install telethon")

        print(f"📥 Fetching chat history for {chat_id or 'all chats'}...")

        # Create client
        session_name = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        client = TelegramClient(session_name, int(api_id), api_hash)

        messages = []

        async def fetch():
            try:
                if not await client.is_user_authorized():
                    # Use a lambda for phone callback
                    await client.start(phone=lambda: phone)
                else:
                    await client.start()
                
                if chat_id:
                    entity = await client.get_entity(chat_id)
                    async for message in client.iter_messages(entity, limit=limit):
                        if message.text:
                            messages.append({
                                'id': message.id,
                                'sender_id': message.sender_id,
                                'sender_name': self._get_sender_name(message),
                                'text': message.text,
                                'date': message.date.isoformat(),
                                'chat_id': str(chat_id)
                            })
                else:
                    async for dialog in client.iter_dialogs():
                        chat_messages = []
                        async for message in client.iter_messages(dialog, limit=limit//10):
                            if message.text:
                                chat_messages.append({
                                    'id': message.id,
                                    'sender_id': message.sender_id,
                                    'sender_name': self._get_sender_name(message),
                                    'text': message.text,
                                    'date': message.date.isoformat(),
                                    'chat_id': str(dialog.id)
                                })
                        if chat_messages:
                            messages.extend(chat_messages)
            except Exception as e:
                print(f"Error in fetch: {e}")
            finally:
                await client.disconnect()

        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create a task
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, fetch())
                    future.result(timeout=300)  # 5 minute timeout
            except RuntimeError:
                # No event loop running, we can use asyncio.run
                asyncio.run(fetch())
            
            print(f"✅ Fetched {len(messages)} messages")
            return {'messages': messages, 'total': len(messages)}
        except Exception as e:
            print(f"❌ Error fetching chat history: {e}")
            return {'messages': [], 'total': 0, 'error': str(e)}
    
    def _get_sender_name(self, message) -> str:
        """Extract sender name from message"""
        try:
            if message.sender:
                if hasattr(message.sender, 'first_name'):
                    return f"{message.sender.first_name} {message.sender.last_name or ''}".strip()
                elif hasattr(message.sender, 'title'):
                    return message.sender.title
            return "Unknown"
        except:
            return "Unknown"
    
    def store_encrypted_history(self, chat_data: Dict[str, Any]) -> bool:
        """Store encrypted chat history in database"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    for message in chat_data.get('messages', []):
                        # Encrypt message data
                        message_json = json.dumps(message)
                        encrypted_data = self.encrypt_data(message_json)
                        
                        # Store in database
                        conn.execute("""
                            INSERT OR REPLACE INTO chat_history 
                            (chat_id, message_id, sender_id, sender_name, message_text, timestamp, encrypted_data)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            message['chat_id'],
                            message['id'],
                            str(message['sender_id']),
                            message['sender_name'],
                            message['text'][:1000],  # Truncate for search
                            message['date'],
                            encrypted_data
                        ))
                    
                    # Update metadata
                    chat_id = chat_data.get('chat_id', 'all')
                    conn.execute("""
                        INSERT OR REPLACE INTO chat_metadata 
                        (chat_id, chat_name, chat_type, total_messages, last_updated, encryption_hash)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        chat_id,
                        chat_data.get('chat_name', 'Unknown'),
                        chat_data.get('chat_type', 'unknown'),
                        len(chat_data.get('messages', [])),
                        datetime.now().isoformat(),
                        hashlib.sha256(self.encryption_key.encode()).hexdigest()[:16]
                    ))
                    
                    conn.commit()
            
            print(f"✅ Stored {len(chat_data.get('messages', []))} encrypted messages")
            return True
            
        except Exception as e:
            print(f"❌ Error storing encrypted history: {e}")
            return False
    
    def get_encrypted_history(self, chat_id: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieve encrypted chat history"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    if chat_id:
                        cursor = conn.execute("""
                            SELECT encrypted_data FROM chat_history 
                            WHERE chat_id = ? 
                            ORDER BY timestamp DESC 
                            LIMIT ?
                        """, (chat_id, limit))
                    else:
                        cursor = conn.execute("""
                            SELECT encrypted_data FROM chat_history 
                            ORDER BY timestamp DESC 
                            LIMIT ?
                        """, (limit,))
                    
                    messages = []
                    for row in cursor.fetchall():
                        try:
                            encrypted_data = row[0]
                            decrypted_json = self.decrypt_data(encrypted_data)
                            message = json.loads(decrypted_json)
                            messages.append(message)
                        except Exception as e:
                            self.logger.warning(f"Failed to decrypt message: {e}")
                    
                    return messages
                    
        except Exception as e:
            print(f"❌ Error retrieving encrypted history: {e}")
            return []
    
    def search_encrypted_history(self, query: str, chat_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Search encrypted chat history"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    if chat_id:
                        cursor = conn.execute("""
                            SELECT encrypted_data FROM chat_history 
                            WHERE chat_id = ? AND message_text LIKE ?
                            ORDER BY timestamp DESC 
                            LIMIT ?
                        """, (chat_id, f"%{query}%", limit))
                    else:
                        cursor = conn.execute("""
                            SELECT encrypted_data FROM chat_history 
                            WHERE message_text LIKE ?
                            ORDER BY timestamp DESC 
                            LIMIT ?
                        """, (f"%{query}%", limit))
                    
                    messages = []
                    for row in cursor.fetchall():
                        try:
                            encrypted_data = row[0]
                            decrypted_json = self.decrypt_data(encrypted_data)
                            message = json.loads(decrypted_json)
                            messages.append(message)
                        except Exception as e:
                            self.logger.warning(f"Failed to decrypt message: {e}")
                    
                    return messages
                    
        except Exception as e:
            print(f"❌ Error searching encrypted history: {e}")
            return []
    
    def get_chat_insights(self, chat_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Generate insights from encrypted chat history"""
        try:
            messages = self.get_encrypted_history(chat_id, limit=10000)
            
            if not messages:
                return {"error": "No messages found"}
            
            # Filter by date
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_messages = [
                msg for msg in messages 
                if datetime.fromisoformat(msg['date']) > cutoff_date
            ]
            
            # Analyze patterns
            sender_counts = {}
            word_frequency = {}
            daily_activity = {}
            
            for message in recent_messages:
                # Sender analysis
                sender = message['sender_name']
                sender_counts[sender] = sender_counts.get(sender, 0) + 1
                
                # Word frequency
                words = message['text'].lower().split()
                for word in words:
                    if len(word) > 3:  # Skip short words
                        word_frequency[word] = word_frequency.get(word, 0) + 1
                
                # Daily activity
                date = message['date'][:10]
                daily_activity[date] = daily_activity.get(date, 0) + 1
            
            # Top insights
            top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            top_words = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            top_days = sorted(daily_activity.items(), key=lambda x: x[1], reverse=True)[:7]
            
            return {
                "total_messages": len(recent_messages),
                "time_period_days": days,
                "top_senders": top_senders,
                "top_words": top_words,
                "most_active_days": top_days,
                "average_messages_per_day": len(recent_messages) / days if days > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error generating insights: {e}")
            return {"error": str(e)}
    
    def export_encrypted_history(self, output_path: str, chat_id: Optional[str] = None) -> bool:
        """Export encrypted chat history to file"""
        try:
            messages = self.get_encrypted_history(chat_id, limit=100000)
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "chat_id": chat_id,
                "total_messages": len(messages),
                "encryption_hash": hashlib.sha256(self.encryption_key.encode()).hexdigest()[:16],
                "messages": messages
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Exported {len(messages)} messages to {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting history: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total messages
                total_messages = conn.execute("SELECT COUNT(*) FROM chat_history").fetchone()[0]
                
                # Unique chats
                unique_chats = conn.execute("SELECT COUNT(DISTINCT chat_id) FROM chat_history").fetchone()[0]
                
                # Storage size
                db_size = self.db_path.stat().st_size
                
                # Recent activity
                recent_messages = conn.execute("""
                    SELECT COUNT(*) FROM chat_history 
                    WHERE timestamp > datetime('now', '-7 days')
                """).fetchone()[0]
                
                return {
                    "total_messages": total_messages,
                    "unique_chats": unique_chats,
                    "database_size_mb": round(db_size / (1024 * 1024), 2),
                    "messages_last_7_days": recent_messages,
                    "encryption_enabled": True,
                    "encryption_key_valid": self._is_valid_encryption_key(self.encryption_key)
                }
                
        except Exception as e:
            return {"error": str(e)}

def main():
    """Test the chat history manager"""
    print("🔐 Chat History Manager Test")
    print("=" * 40)
    
    # Initialize manager
    manager = ChatHistoryManager()
    
    # Test encryption
    test_data = "Hello, this is a test message!"
    encrypted = manager.encrypt_data(test_data)
    decrypted = manager.decrypt_data(encrypted)
    
    print(f"✅ Encryption test: {test_data == decrypted}")
    print(f"📊 Database stats: {manager.get_database_stats()}")

if __name__ == "__main__":
    main() 