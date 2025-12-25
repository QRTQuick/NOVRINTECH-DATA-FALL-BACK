#!/usr/bin/env python3
"""
PostgreSQL Database Manager for Novrintech Desktop Client
Handles direct database operations with Neon PostgreSQL
"""
import psycopg2
import json
from datetime import datetime
import os
from urllib.parse import urlparse

class DatabaseManager:
    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            self.database_url = "postgresql://neondb_owner:npg_0N1WuhVBDLIP@ep-weathered-math-afeq5max-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        
        self.connection = None
        self.setup_tables()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def setup_tables(self):
        """Create necessary tables if they don't exist"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Chat messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    message_type VARCHAR(50) NOT NULL,
                    title VARCHAR(500) NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id VARCHAR(255),
                    app_version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # AI chat history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_chat_history (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id VARCHAR(255),
                    app_version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # File uploads table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_uploads (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    file_name VARCHAR(500) NOT NULL,
                    file_id VARCHAR(255) UNIQUE,
                    file_size BIGINT,
                    file_hash VARCHAR(255),
                    upload_count INTEGER DEFAULT 1,
                    first_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    app_version VARCHAR(50),
                    platform VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            cursor.close()
            print("✅ Database tables setup completed")
            return True
            
        except Exception as e:
            print(f"❌ Database setup error: {e}")
            return False
        finally:
            self.disconnect()
    
    def save_chat_message(self, user_name, message_type, title, content, session_id=None):
        """Save chat message to database"""
        if not self.connect():
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO chat_messages (user_name, message_type, title, content, session_id, app_version)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (user_name, message_type, title, content, session_id, "2.0"))
            
            message_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            
            return {"success": True, "message_id": message_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.disconnect()
    
    def save_ai_chat(self, user_name, role, message, session_id=None):
        """Save AI chat to database"""
        if not self.connect():
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO ai_chat_history (user_name, role, message, session_id, app_version)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (user_name, role, message, session_id, "2.0"))
            
            chat_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            
            return {"success": True, "chat_id": chat_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.disconnect()
    
    def get_chat_history(self, user_name, limit=50):
        """Get chat history from database"""
        if not self.connect():
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT message_type, title, content, timestamp, session_id
                FROM chat_messages 
                WHERE user_name = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (user_name, limit))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    "type": row[0],
                    "title": row[1],
                    "content": row[2],
                    "timestamp": row[3].strftime("%Y-%m-%d %H:%M:%S"),
                    "session_id": row[4]
                })
            
            cursor.close()
            return {"success": True, "messages": messages}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.disconnect()
    
    def get_ai_chat_history(self, user_name, limit=50):
        """Get AI chat history from database"""
        if not self.connect():
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT role, message, timestamp, session_id
                FROM ai_chat_history 
                WHERE user_name = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (user_name, limit))
            
            chats = []
            for row in cursor.fetchall():
                chats.append({
                    "role": row[0],
                    "message": row[1],
                    "timestamp": row[2].strftime("%Y-%m-%d %H:%M:%S"),
                    "session_id": row[3]
                })
            
            cursor.close()
            return {"success": True, "chats": chats}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.disconnect()
    
    def save_file_upload(self, user_name, file_name, file_id, file_size=None, file_hash=None):
        """Save file upload record to database"""
        if not self.connect():
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = self.connection.cursor()
            
            # Check if file already exists
            cursor.execute("SELECT id, upload_count FROM file_uploads WHERE file_id = %s", (file_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE file_uploads 
                    SET upload_count = upload_count + 1, last_upload = CURRENT_TIMESTAMP
                    WHERE file_id = %s
                    RETURNING id
                """, (file_id,))
                upload_id = cursor.fetchone()[0]
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO file_uploads (user_name, file_name, file_id, file_size, file_hash)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (user_name, file_name, file_id, file_size, file_hash))
                upload_id = cursor.fetchone()[0]
            
            self.connection.commit()
            cursor.close()
            
            return {"success": True, "upload_id": upload_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.disconnect()
    
    def get_user_stats(self, user_name):
        """Get user statistics from database"""
        if not self.connect():
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = self.connection.cursor()
            
            # Get chat message count
            cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE user_name = %s", (user_name,))
            chat_count = cursor.fetchone()[0]
            
            # Get AI chat count
            cursor.execute("SELECT COUNT(*) FROM ai_chat_history WHERE user_name = %s", (user_name,))
            ai_chat_count = cursor.fetchone()[0]
            
            # Get file upload count
            cursor.execute("SELECT COUNT(*), SUM(upload_count) FROM file_uploads WHERE user_name = %s", (user_name,))
            file_stats = cursor.fetchone()
            unique_files = file_stats[0] or 0
            total_uploads = file_stats[1] or 0
            
            cursor.close()
            
            return {
                "success": True,
                "stats": {
                    "chat_messages": chat_count,
                    "ai_conversations": ai_chat_count,
                    "unique_files": unique_files,
                    "total_uploads": total_uploads
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.disconnect()
    
    def test_connection(self):
        """Test database connection"""
        if self.connect():
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return {"success": True, "message": "Database connection successful"}
            except Exception as e:
                return {"success": False, "error": str(e)}
            finally:
                self.disconnect()
        else:
            return {"success": False, "error": "Failed to connect to database"}