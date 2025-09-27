#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""用户模型，处理用户相关的业务逻辑"""

from database.db_manager import db_manager
from config.config import ROLES
import hashlib
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('user_model')


class User:
    """用户类，封装用户相关的业务逻辑"""
    
    @staticmethod
    def hash_password(password):
        """密码加密"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def login(username, password):
        """用户登录验证"""
        try:
            # 对密码进行哈希处理
            hashed_password = User.hash_password(password)
            
            # 查询用户
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            result = db_manager.execute_query(query, (username, hashed_password))
            
            if result and len(result) > 0:
                user = result[0]
                logger.info(f"用户 {username} 登录成功")
                return user
            else:
                logger.warning(f"用户 {username} 登录失败: 用户名或密码错误")
                return None
        except Exception as e:
            logger.error(f"登录验证失败: {e}")
            return None
    
    @staticmethod
    def register(username, password, role, name):
        """用户注册"""
        try:
            # 检查用户名是否已存在
            query = "SELECT * FROM users WHERE username = %s"
            result = db_manager.execute_query(query, (username,))
            
            if result and len(result) > 0:
                logger.warning(f"用户注册失败: 用户名 {username} 已存在")
                return False
            
            # 对密码进行哈希处理
            hashed_password = User.hash_password(password)
            
            # 插入新用户
            query = "INSERT INTO users (username, password, role, name) VALUES (%s, %s, %s, %s)"
            result = db_manager.execute_update(query, (username, hashed_password, role, name))
            
            if result > 0:
                logger.info(f"用户 {username} 注册成功")
                return True
            else:
                logger.warning(f"用户 {username} 注册失败")
                return False
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            return False
    
    @staticmethod
    def update_user(user_id, name=None, password=None, role=None, email=None):
        """更新用户信息"""
        try:
            # 构建更新语句
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            
            if password is not None:
                hashed_password = User.hash_password(password)
                updates.append("password = %s")
                params.append(hashed_password)
            
            if role is not None:
                updates.append("role = %s")
                params.append(role)
            
            if email is not None:
                updates.append("email = %s")
                params.append(email)
            
            if not updates:
                return True
            
            # 添加user_id到参数列表
            params.append(user_id)
            
            # 执行更新
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            result = db_manager.execute_update(query, tuple(params))
            
            if result > 0:
                logger.info(f"用户ID {user_id} 信息更新成功")
                return True
            else:
                logger.warning(f"用户ID {user_id} 信息更新失败")
                return False
        except Exception as e:
            logger.error(f"更新用户信息失败: {e}")
            return False
    
    @staticmethod
    def get_user_by_id(user_id):
        """根据用户ID获取用户信息"""
        try:
            query = "SELECT * FROM users WHERE id = %s"
            result = db_manager.execute_query(query, (user_id,))
            
            if result and len(result) > 0:
                return result[0]
            else:
                logger.warning(f"用户ID {user_id} 不存在")
                return None
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    @staticmethod
    def get_user_by_username(username):
        """根据用户名获取用户信息"""
        try:
            query = "SELECT * FROM users WHERE username = %s"
            result = db_manager.execute_query(query, (username,))
            
            if result and len(result) > 0:
                return result[0]
            else:
                logger.warning(f"用户名 {username} 不存在")
                return None
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    @staticmethod
    def get_all_users():
        """获取所有用户信息(管理员权限)"""
        try:
            query = "SELECT * FROM users"
            result = db_manager.execute_query(query)
            return result
        except Exception as e:
            logger.error(f"获取所有用户信息失败: {e}")
            return None
    
    @staticmethod
    def delete_user(user_id):
        """删除用户(管理员权限)"""
        try:
            query = "DELETE FROM users WHERE id = %s"
            result = db_manager.execute_update(query, (user_id,))
            
            if result > 0:
                logger.info(f"用户ID {user_id} 删除成功")
                return True
            else:
                logger.warning(f"用户ID {user_id} 删除失败")
                return False
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return False