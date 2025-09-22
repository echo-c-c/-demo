import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import os

class AuthService:
    def __init__(self, db_path: str = "chat_database.db"):
        self.db_path = db_path
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.token_expire_hours = 24
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        try:
            salt, hash_hex = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return password_hash_check.hex() == hash_hex
        except:
            return False
    
    def create_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """创建用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查用户名和邮箱是否已存在
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                return {"success": False, "message": "用户名或邮箱已存在"}
            
            # 创建用户
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True,
                "message": "用户创建成功",
                "user_id": user_id,
                "username": username
            }
            
        except Exception as e:
            return {"success": False, "message": f"创建用户失败: {str(e)}"}
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """用户认证"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, email, password_hash, avatar_url
                FROM users
                WHERE (username = ? OR email = ?) AND is_active = 1
            ''', (username, username))
            
            user = cursor.fetchone()
            if not user:
                return {"success": False, "message": "用户不存在"}
            
            user_id, username, email, password_hash, avatar_url = user
            
            if not self.verify_password(password, password_hash):
                return {"success": False, "message": "密码错误"}
            
            # 更新最后登录时间
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            conn.commit()
            
            # 生成JWT token
            token = self.generate_token(user_id, username)
            
            return {
                "success": True,
                "message": "登录成功",
                "token": token,
                "user": {
                    "id": user_id,
                    "username": username,
                    "email": email,
                    "avatar_url": avatar_url
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"认证失败: {str(e)}"}
        finally:
            conn.close()
    
    def generate_token(self, user_id: int, username: str) -> str:
        """生成JWT token"""
        payload = {
            "user_id": user_id,
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return {
                "user_id": payload["user_id"],
                "username": payload["username"],
                "exp": payload["exp"]
            }
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, email, avatar_url, created_at, last_login
                FROM users
                WHERE id = ? AND is_active = 1
            ''', (user_id,))
            
            user = cursor.fetchone()
            if user:
                return {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "avatar_url": user[3],
                    "created_at": user[4],
                    "last_login": user[5]
                }
            return None
            
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
        finally:
            conn.close()
    
    def update_user_profile(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """更新用户资料"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 构建更新语句
            update_fields = []
            values = []
            
            allowed_fields = ["username", "email", "avatar_url"]
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
            
            if not update_fields:
                return {"success": False, "message": "没有可更新的字段"}
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount > 0:
                return {"success": True, "message": "资料更新成功"}
            else:
                return {"success": False, "message": "用户不存在"}
                
        except Exception as e:
            return {"success": False, "message": f"更新失败: {str(e)}"}
        finally:
            conn.close()
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """修改密码"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 获取当前密码哈希
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return {"success": False, "message": "用户不存在"}
            
            current_password_hash = result[0]
            
            # 验证旧密码
            if not self.verify_password(old_password, current_password_hash):
                return {"success": False, "message": "旧密码错误"}
            
            # 更新密码
            new_password_hash = self.hash_password(new_password)
            cursor.execute('''
                UPDATE users SET password_hash = ? WHERE id = ?
            ''', (new_password_hash, user_id))
            
            conn.commit()
            
            return {"success": True, "message": "密码修改成功"}
            
        except Exception as e:
            return {"success": False, "message": f"密码修改失败: {str(e)}"}
        finally:
            conn.close()
    
    def deactivate_user(self, user_id: int) -> Dict[str, Any]:
        """停用用户账户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET is_active = 0 WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                return {"success": True, "message": "账户已停用"}
            else:
                return {"success": False, "message": "用户不存在"}
                
        except Exception as e:
            return {"success": False, "message": f"停用失败: {str(e)}"}
        finally:
            conn.close()
