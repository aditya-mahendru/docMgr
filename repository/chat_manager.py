"""
Chat History Management Module
Handles chat conversations, LLM interactions, and conversation tracking
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from db import get_db_connection
from repository.user_manager import UserManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatManager:
    def __init__(self, user_manager: UserManager):
        """Initialize the chat manager"""
        self.user_manager = user_manager
        self.max_conversation_length = 50  # Maximum messages per conversation
    
    def start_conversation(self, user_id: int, session_id: int, 
                          initial_message: str = None) -> Dict[str, Any]:
        """Start a new conversation session"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if user has active session
            cursor.execute('''
                SELECT id FROM user_sessions 
                WHERE user_id = ? AND id = ? AND is_active = 1
            ''', (user_id, session_id))
            
            if not cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Invalid or expired session"}
            
            # Log conversation start
            self.user_manager._log_activity(
                user_id, 'conversation_started', 'New conversation started'
            )
            
            conn.close()
            
            conversation_id = f"conv_{user_id}_{session_id}_{int(datetime.now().timestamp())}"
            
            logger.info(f"Conversation started: {conversation_id} for user {user_id}")
            return {
                "success": True,
                "conversation_id": conversation_id,
                "session_id": session_id,
                "user_id": user_id,
                "started_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            return {"success": False, "error": str(e)}
    
    def add_user_message(self, user_id: int, session_id: int, 
                        content: str, conversation_id: str = None) -> Dict[str, Any]:
        """Add a user message to the chat history"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Validate session
            cursor.execute('''
                SELECT id FROM user_sessions 
                WHERE user_id = ? AND id = ? AND is_active = 1
            ''', (user_id, session_id))
            
            if not cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Invalid or expired session"}
            
            # Add user message
            cursor.execute('''
                INSERT INTO chat_history (user_id, session_id, message_type, content, conversation_id)
                VALUES (?, ?, 'user', ?, ?)
            ''', (user_id, session_id, content, conversation_id))
            
            message_id = cursor.lastrowid
            
            # Log user message activity
            self.user_manager._log_activity(
                user_id, 'chat_message', f'User message added: {len(content)} chars',
                metadata={'message_id': message_id, 'conversation_id': conversation_id}
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"User message added: {message_id} for user {user_id}")
            return {
                "success": True,
                "message_id": message_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error adding user message: {e}")
            return {"success": False, "error": str(e)}
    
    def add_assistant_message(self, user_id: int, session_id: int, 
                            content: str, conversation_id: str = None,
                            tokens_used: int = 0, llm_model: str = None,
                            response_time_ms: int = 0, cost_estimate: float = 0.0) -> Dict[str, Any]:
        """Add an assistant message to the chat history"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Validate session
            cursor.execute('''
                SELECT id FROM user_sessions 
                WHERE user_id = ? AND id = ? AND is_active = 1
            ''', (user_id, session_id))
            
            if not cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Invalid or expired session"}
            
            # Add assistant message
            cursor.execute('''
                INSERT INTO chat_history (user_id, session_id, message_type, content, 
                                       conversation_id, tokens_used, llm_model, 
                                       response_time_ms, cost_estimate)
                VALUES (?, ?, 'assistant', ?, ?, ?, ?, ?, ?)
            ''', (user_id, session_id, content, conversation_id, tokens_used, 
                  llm_model, response_time_ms, cost_estimate))
            
            message_id = cursor.lastrowid
            
            # Update user stats for LLM usage
            if tokens_used > 0:
                self.user_manager.update_user_stats(
                    user_id, 'llm_call', tokens_used, cost_estimate
                )
            
            # Log assistant message activity
            self.user_manager._log_activity(
                user_id, 'assistant_response', f'Assistant response: {tokens_used} tokens',
                metadata={
                    'message_id': message_id, 
                    'conversation_id': conversation_id,
                    'tokens_used': tokens_used,
                    'llm_model': llm_model,
                    'cost_estimate': cost_estimate
                }
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Assistant message added: {message_id} for user {user_id}")
            return {
                "success": True,
                "message_id": message_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error adding assistant message: {e}")
            return {"success": False, "error": str(e)}
    
    def get_conversation_history(self, user_id: int, session_id: int, 
                                conversation_id: str = None, limit: int = 20) -> Dict[str, Any]:
        """Get conversation history for a user session"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Validate session
            cursor.execute('''
                SELECT id FROM user_sessions 
                WHERE user_id = ? AND id = ? AND is_active = 1
            ''', (user_id, session_id))
            
            if not cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Invalid or expired session"}
            
            # Get conversation history
            if conversation_id:
                cursor.execute('''
                    SELECT id, message_type, content, timestamp, tokens_used, 
                           llm_model, response_time_ms, cost_estimate
                    FROM chat_history
                    WHERE user_id = ? AND session_id = ? AND conversation_id = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                ''', (user_id, session_id, conversation_id, limit))
            else:
                cursor.execute('''
                    SELECT id, message_type, content, timestamp, tokens_used, 
                           llm_model, response_time_ms, cost_estimate
                    FROM chat_history
                    WHERE user_id = ? AND session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, session_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    "id": row['id'],
                    "message_type": row['message_type'],
                    "content": row['content'],
                    "timestamp": row['timestamp'],
                    "tokens_used": row['tokens_used'],
                    "llm_model": row['llm_model'],
                    "response_time_ms": row['response_time_ms'],
                    "cost_estimate": row['cost_estimate']
                })
            
            conn.close()
            
            return {
                "success": True,
                "messages": messages,
                "total_messages": len(messages),
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_chat_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get chat statistics for a user"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get message counts by type
            cursor.execute('''
                SELECT message_type, COUNT(*) as count, SUM(tokens_used) as total_tokens
                FROM chat_history
                WHERE user_id = ? AND timestamp >= date('now', '-{} days')
                GROUP BY message_type
            '''.format(days), (user_id,))
            
            message_stats = {}
            total_tokens = 0
            for row in cursor.fetchall():
                message_stats[row['message_type']] = {
                    "count": row['count'],
                    "total_tokens": row['total_tokens'] or 0
                }
                total_tokens += row['total_tokens'] or 0
            
            # Get cost statistics
            cursor.execute('''
                SELECT SUM(cost_estimate) as total_cost, AVG(response_time_ms) as avg_response_time
                FROM chat_history
                WHERE user_id = ? AND message_type = 'assistant' 
                AND timestamp >= date('now', '-{} days')
            '''.format(days), (user_id,))
            
            cost_stats = cursor.fetchone()
            
            # Get conversation count
            cursor.execute('''
                SELECT COUNT(DISTINCT conversation_id) as conversation_count
                FROM chat_history
                WHERE user_id = ? AND timestamp >= date('now', '-{} days')
                AND conversation_id IS NOT NULL
            '''.format(days), (user_id,))
            
            conversation_count = cursor.fetchone()['conversation_count']
            
            conn.close()
            
            return {
                "success": True,
                "period_days": days,
                "message_stats": message_stats,
                "total_tokens": total_tokens,
                "total_cost": cost_stats['total_cost'] or 0.0,
                "avg_response_time_ms": cost_stats['avg_response_time'] or 0,
                "conversation_count": conversation_count
            }
            
        except Exception as e:
            logger.error(f"Error getting chat stats: {e}")
            return {"success": False, "error": str(e)}
    
    def cleanup_old_conversations(self, days: int = 90) -> int:
        """Clean up old conversation data and return count of cleaned records"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Delete old chat history
            cursor.execute('''
                DELETE FROM chat_history
                WHERE timestamp < date('now', '-{} days')
            '''.format(days))
            
            cleaned_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old chat records")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old conversations: {e}")
            return 0
    
    def search_chat_history(self, user_id: int, query: str, 
                           limit: int = 20) -> Dict[str, Any]:
        """Search through user's chat history"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Search in chat content
            cursor.execute('''
                SELECT id, message_type, content, timestamp, conversation_id
                FROM chat_history
                WHERE user_id = ? AND content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, f'%{query}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row['id'],
                    "message_type": row['message_type'],
                    "content": row['content'][:200] + "..." if len(row['content']) > 200 else row['content'],
                    "timestamp": row['timestamp'],
                    "conversation_id": row['conversation_id']
                })
            
            conn.close()
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_results": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error searching chat history: {e}")
            return {"success": False, "error": str(e)}
