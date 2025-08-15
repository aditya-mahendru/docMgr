"""
User Management Module
Handles user authentication, session management, and user analytics
"""

import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from db import get_db_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self):
        """Initialize the user manager"""
        self.session_duration = timedelta(hours=24)  # 24 hour sessions
        self.max_sessions_per_user = 5  # Maximum active sessions per user
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash a password with salt using SHA-256"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _generate_salt(self) -> str:
        """Generate a random salt for password hashing"""
        return secrets.token_hex(16)
    
    def _generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def create_user(self, username: str, email: str, password: str, 
                   subscription_tier: str = 'free') -> Dict[str, Any]:
        """Create a new user account"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute(
                "SELECT id FROM users WHERE username = ? OR email = ?",
                (username, email)
            )
            if cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Username or email already exists"}
            
            # Generate salt and hash password
            salt = self._generate_salt()
            password_hash = self._hash_password(password, salt)
            
            # Create user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, subscription_tier)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, subscription_tier))
            
            user_id = cursor.lastrowid
            
            # Log user creation
            self._log_activity(user_id, 'user_created', f'User {username} created')
            
            conn.commit()
            conn.close()
            
            logger.info(f"User created successfully: {username}")
            return {
                "success": True, 
                "user_id": user_id,
                "username": username,
                "email": email,
                "subscription_tier": subscription_tier
            }
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return {"success": False, "error": str(e)}
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Authenticate a user and create a session"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get user by username
            cursor.execute(
                "SELECT id, username, email, password_hash, salt, is_active, subscription_tier FROM users WHERE username = ?",
                (username,)
            )
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {"success": False, "error": "Invalid credentials", "status_code": 401}
            
            if not user['is_active']:
                conn.close()
                return {"success": False, "error": "Account is deactivated"}
            
            # Verify password
            if self._hash_password(password, user['salt']) != user['password_hash']:
                conn.close()
                return {"success": False, "error": "Invalid credentials"}
            
            # Create session
            session_result = self._create_session(
                user['id'], ip_address, user_agent
            )
            
            if not session_result['success']:
                conn.close()
                return session_result
            
            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now(), user['id'])
            )
            
            # Log login activity
            self._log_activity(
                user['id'], 'login', f'User {username} logged in',
                ip_address, user_agent
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"User authenticated successfully: {username}")
            return {
                "success": True,
                "user_id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "subscription_tier": user['subscription_tier'],
                "session_token": session_result['session_token'],
                "expires_at": session_result['expires_at']
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_session(self, user_id: int, ip_address: str = None, 
                       user_agent: str = None) -> Dict[str, Any]:
        """Create a new user session"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check existing sessions for this user
            cursor.execute(
                "SELECT COUNT(*) FROM user_sessions WHERE user_id = ? AND is_active = 1",
                (user_id,)
            )
            active_sessions = cursor.fetchone()[0]
            
            # If max sessions reached, deactivate oldest
            if active_sessions >= self.max_sessions_per_user:
                cursor.execute('''
                    UPDATE user_sessions 
                    SET is_active = 0 
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY last_activity ASC 
                    LIMIT 1
                ''', (user_id,))
            
            # Create new session
            session_token = self._generate_session_token()
            expires_at = datetime.now() + self.session_duration
            
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, session_token, expires_at, ip_address, user_agent))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "session_token": session_token,
                "expires_at": expires_at
            }
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate a session token and return user info"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get session and user info
            cursor.execute('''
                SELECT s.id, s.user_id, s.expires_at, s.last_activity,
                       u.username, u.email, u.subscription_tier, u.is_active
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = 1
            ''', (session_token,))
            
            session = cursor.fetchone()
            
            if not session:
                conn.close()
                return None
            
            # Check if session expired
            if datetime.fromisoformat(session['expires_at']) < datetime.now():
                # Deactivate expired session
                cursor.execute(
                    "UPDATE user_sessions SET is_active = 0 WHERE id = ?",
                    (session['id'],)
                )
                conn.commit()
                conn.close()
                return None
            
            # Update last activity
            cursor.execute(
                "UPDATE user_sessions SET last_activity = ? WHERE id = ?",
                (datetime.now(), session['id'])
            )
            
            conn.commit()
            conn.close()
            
            return {
                "session_id": session['id'],
                "user_id": session['user_id'],
                "username": session['username'],
                "email": session['email'],
                "subscription_tier": session['subscription_tier'],
                "expires_at": session['expires_at']
            }
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None
    
    def logout_user(self, session_token: str) -> bool:
        """Logout a user by deactivating their session"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get session info
            cursor.execute(
                "SELECT user_id FROM user_sessions WHERE session_token = ? AND is_active = 1",
                (session_token,)
            )
            session = cursor.fetchone()
            
            if not session:
                conn.close()
                return False
            
            # Deactivate session
            cursor.execute(
                "UPDATE user_sessions SET is_active = 0 WHERE session_token = ?",
                (session_token,)
            )
            
            # Log logout activity
            self._log_activity(session['user_id'], 'logout', 'User logged out')
            
            conn.commit()
            conn.close()
            
            logger.info(f"User logged out successfully: {session['user_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging out user: {e}")
            return False
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, created_at, last_login, is_active,
                       total_documents, total_llm_calls, total_tokens_processed,
                       subscription_tier, api_quota, api_quota_reset_date
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return None
            
            return dict(user)
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def update_user_stats(self, user_id: int, activity_type: str, 
                         tokens_used: int = 0, cost_estimate: float = 0.0) -> bool:
        """Update user statistics for analytics"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if activity_type == 'document_upload':
                cursor.execute('''
                    UPDATE users 
                    SET total_documents = total_documents + 1
                    WHERE id = ?
                ''', (user_id,))
            
            elif activity_type == 'llm_call':
                cursor.execute('''
                    UPDATE users 
                    SET total_llm_calls = total_llm_calls + 1,
                        total_tokens_processed = total_tokens_processed + ?
                    WHERE id = ?
                ''', (tokens_used, user_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating user stats: {e}")
            return False
    
    def _log_activity(self, user_id: int, activity_type: str, description: str,
                      ip_address: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Log user activity for analytics"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute('''
                INSERT INTO user_activity_log (user_id, activity_type, description, ip_address, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, activity_type, description, ip_address, metadata_json))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return False
    
    def get_user_activity_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get user activity summary for the last N days"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get activity counts
            cursor.execute('''
                SELECT activity_type, COUNT(*) as count
                FROM user_activity_log
                WHERE user_id = ? AND timestamp >= date('now', '-{} days')
                GROUP BY activity_type
            '''.format(days), (user_id,))
            
            activity_counts = dict(cursor.fetchall())
            
            # Get recent documents
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM documents
                WHERE user_id = ? AND upload_date >= date('now', '-{} days')
            '''.format(days), (user_id,))
            
            recent_docs = cursor.fetchone()['count']
            
            conn.close()
            
            return {
                "activity_counts": activity_counts,
                "recent_documents": recent_docs,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting activity summary: {e}")
            return {}
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions 
                SET is_active = 0 
                WHERE expires_at < ? AND is_active = 1
            ''', (datetime.now(),))
            
            cleaned_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired sessions")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
