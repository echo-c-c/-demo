import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

class DatabaseManager:
    def __init__(self, db_path: str = "chat_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建聊天记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT NOT NULL,
                user_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                character_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建角色评分表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS character_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                feedback TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户偏好表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                character_id TEXT NOT NULL,
                preference_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                avatar_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        ''')

        # 创建用户会话表
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

        # 创建角色收藏表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                character_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, character_id)
            )
        ''')

        # 创建用户设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                setting_key TEXT NOT NULL,
                setting_value TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, setting_key)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_chat_record(self, character_id: str, role: str, content: str, message_type: str, user_id: str = None):
        """保存聊天记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_records (character_id, role, content, message_type, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (character_id, role, content, message_type, user_id))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, character_id: str, limit: int = 50, user_id: str = None) -> List[Dict[str, Any]]:
        """获取聊天历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT role, content, message_type, timestamp
                FROM chat_records
                WHERE character_id = ? AND user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (character_id, user_id, limit))
        else:
            cursor.execute('''
                SELECT role, content, message_type, timestamp
                FROM chat_records
                WHERE character_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (character_id, limit))
        
        records = cursor.fetchall()
        conn.close()
        
        return [
            {
                "role": record[0],
                "content": record[1],
                "message_type": record[2],
                "timestamp": record[3]
            }
            for record in reversed(records)
        ]
    
    def get_user_chat_history(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户所有聊天历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT character_id, role, content, message_type, timestamp
            FROM chat_records
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 1000
        ''', (user_id,))
        
        records = cursor.fetchall()
        conn.close()
        
        # 按角色分组
        history_by_character = {}
        for record in records:
            character_id = record[0]
            if character_id not in history_by_character:
                history_by_character[character_id] = []
            history_by_character[character_id].append({
                "role": record[1],
                "content": record[2],
                "message_type": record[3],
                "timestamp": record[4]
            })
        
        return history_by_character
    
    def clear_chat_history(self, character_id: str, user_id: str) -> Dict[str, Any]:
        """清空与特定角色的聊天历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM chat_records
                WHERE character_id = ? AND user_id = ?
            ''', (character_id, user_id))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return {"success": True, "deleted_count": deleted_count, "message": f"已清空 {deleted_count} 条聊天记录"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"清空聊天记录失败: {e}"}
        finally:
            conn.close()
    
    def search_chat_history(self, query: str, user_id: str) -> List[Dict[str, Any]]:
        """搜索聊天历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT character_id, role, content, message_type, timestamp
            FROM chat_records
            WHERE user_id = ? AND content LIKE ?
            ORDER BY timestamp DESC
            LIMIT 100
        ''', (user_id, f'%{query}%'))
        
        records = cursor.fetchall()
        conn.close()
        
        return [
            {
                "character_id": record[0],
                "role": record[1],
                "content": record[2],
                "message_type": record[3],
                "timestamp": record[4]
            }
            for record in records
        ]
    
    def add_favorite_character(self, user_id: str, character_id: str) -> Dict[str, Any]:
        """添加角色到收藏"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO user_favorites (user_id, character_id)
                VALUES (?, ?)
            ''', (user_id, character_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                return {"success": True, "message": "角色已添加到收藏"}
            else:
                return {"success": False, "message": "角色已在收藏列表中"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"添加收藏失败: {e}"}
        finally:
            conn.close()
    
    def remove_favorite_character(self, user_id: str, character_id: str) -> Dict[str, Any]:
        """从收藏中移除角色"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM user_favorites
                WHERE user_id = ? AND character_id = ?
            ''', (user_id, character_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                return {"success": True, "message": "角色已从收藏中移除"}
            else:
                return {"success": False, "message": "角色不在收藏列表中"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"移除收藏失败: {e}"}
        finally:
            conn.close()
    
    def get_favorite_characters(self, user_id: str) -> List[str]:
        """获取用户收藏的角色列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT character_id FROM user_favorites
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        favorites = [record[0] for record in cursor.fetchall()]
        conn.close()
        
        return favorites
    
    def is_character_favorited(self, user_id: str, character_id: str) -> bool:
        """检查角色是否已收藏"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 1 FROM user_favorites
            WHERE user_id = ? AND character_id = ?
        ''', (user_id, character_id))
        
        result = cursor.fetchone() is not None
        conn.close()
        
        return result
    
    def save_user_setting(self, user_id: str, setting_key: str, setting_value: str) -> Dict[str, Any]:
        """保存用户设置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO user_settings (user_id, setting_key, setting_value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, setting_key, setting_value))
            
            conn.commit()
            return {"success": True, "message": "设置已保存"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"保存设置失败: {e}"}
        finally:
            conn.close()
    
    def get_user_setting(self, user_id: str, setting_key: str) -> str:
        """获取用户设置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT setting_value FROM user_settings
            WHERE user_id = ? AND setting_key = ?
        ''', (user_id, setting_key))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_all_user_settings(self, user_id: str) -> Dict[str, str]:
        """获取用户所有设置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT setting_key, setting_value FROM user_settings
            WHERE user_id = ?
        ''', (user_id,))
        
        settings = {record[0]: record[1] for record in cursor.fetchall()}
        conn.close()
        
        return settings
    
    def create_user_session(self, session_id: str, character_id: str) -> bool:
        """创建用户会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_sessions (session_id, character_id)
                VALUES (?, ?)
            ''', (session_id, character_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_session_activity(self, session_id: str):
        """更新会话活动时间"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_sessions
            SET last_activity = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    def save_character_rating(self, character_id: str, rating: int, feedback: str = ""):
        """保存角色评分"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO character_ratings (character_id, rating, feedback)
            VALUES (?, ?, ?)
        ''', (character_id, rating, feedback))
        
        conn.commit()
        conn.close()
    
    def get_character_ratings(self, character_id: str) -> Dict[str, Any]:
        """获取角色评分统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(rating), COUNT(rating)
            FROM character_ratings
            WHERE character_id = ?
        ''', (character_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result[0] is not None:
            return {
                "average_rating": round(result[0], 2),
                "total_ratings": result[1]
            }
        else:
            return {
                "average_rating": 0,
                "total_ratings": 0
            }
    
    def save_user_preference(self, user_id: str, character_id: str, preference_data: Dict[str, Any]):
        """保存用户偏好"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 先删除现有偏好
        cursor.execute('''
            DELETE FROM user_preferences
            WHERE user_id = ? AND character_id = ?
        ''', (user_id, character_id))
        
        # 插入新偏好
        cursor.execute('''
            INSERT INTO user_preferences (user_id, character_id, preference_data)
            VALUES (?, ?, ?)
        ''', (user_id, character_id, json.dumps(preference_data)))
        
        conn.commit()
        conn.close()
    
    def get_user_preference(self, user_id: str, character_id: str) -> Optional[Dict[str, Any]]:
        """获取用户偏好"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT preference_data
            FROM user_preferences
            WHERE user_id = ? AND character_id = ?
        ''', (user_id, character_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def get_popular_characters(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门角色"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT character_id, COUNT(*) as chat_count
            FROM chat_records
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY character_id
            ORDER BY chat_count DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {"character_id": result[0], "chat_count": result[1]}
            for result in results
        ]
    
    def cleanup_old_records(self, days: int = 30):
        """清理旧记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM chat_records
            WHERE timestamp < datetime('now', '-{} days')
        '''.format(days))
        
        cursor.execute('''
            DELETE FROM user_sessions
            WHERE last_activity < datetime('now', '-{} days')
        '''.format(days))
        
        conn.commit()
        conn.close()
