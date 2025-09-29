#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""教师模型，处理教师相关的业务逻辑"""

from database.db_manager import db_manager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('teacher_model')


class Teacher:
    """教师类，封装教师相关的业务逻辑"""
    
    @staticmethod
    def add_teacher(teacher_id, name, gender, title, department, user_id):
        """添加教师信息"""
        try:
            # 检查教师编号是否已存在
            query = "SELECT * FROM teachers WHERE teacher_id = %s"
            result = db_manager.execute_query(query, (teacher_id,))
            
            if result and len(result) > 0:
                logger.warning(f"添加教师失败: 教师编号 {teacher_id} 已存在")
                return False
            
            # 插入教师信息
            query = "INSERT INTO teachers (teacher_id, name, gender, title, department, user_id) VALUES (%s, %s, %s, %s, %s, %s)"
            result = db_manager.execute_update(query, (teacher_id, name, gender, title, department, user_id))
            
            if result > 0:
                logger.info(f"教师 {name} (编号: {teacher_id}) 添加成功")
                return True
            else:
                logger.warning(f"教师 {name} (编号: {teacher_id}) 添加失败")
                return False
        except Exception as e:
            logger.error(f"添加教师信息失败: {e}")
            return False
    
    @staticmethod
    def update_teacher(teacher_id, name=None, gender=None, title=None, department=None):
        """更新教师信息"""
        try:
            # 构建更新语句
            updates = []
            params = []
            
            if name:
                updates.append("name = %s")
                params.append(name)
            
            if gender:
                updates.append("gender = %s")
                params.append(gender)
            
            if title:
                updates.append("title = %s")
                params.append(title)
            
            if department:
                updates.append("department = %s")
                params.append(department)
            
            if not updates:
                return True
            
            # 添加teacher_id到参数列表
            params.append(teacher_id)
            
            # 执行更新
            query = f"UPDATE teachers SET {', '.join(updates)} WHERE teacher_id = %s"
            result = db_manager.execute_update(query, tuple(params))
            
            if result > 0:
                logger.info(f"教师 (编号: {teacher_id}) 信息更新成功")
                return True
            else:
                logger.warning(f"教师 (编号: {teacher_id}) 信息更新失败")
                return False
        except Exception as e:
            logger.error(f"更新教师信息失败: {e}")
            return False
    
    @staticmethod
    def get_teacher_by_id(teacher_id):
        """根据教师内部ID获取教师信息"""
        try:
            query = "SELECT * FROM teachers WHERE id = %s"
            result = db_manager.execute_query(query, (teacher_id,))
            
            if result and len(result) > 0:
                return result[0]
            else:
                logger.warning(f"教师ID {teacher_id} 不存在")
                return None
        except Exception as e:
            logger.error(f"获取教师信息失败: {e}")
            return None

    @staticmethod
    def get_teacher_by_teacher_id(teacher_id):
        """根据教师编号获取教师信息"""
        try:
            query = "SELECT * FROM teachers WHERE teacher_id = %s"
            result = db_manager.execute_query(query, (teacher_id,))
            
            if result and len(result) > 0:
                return result[0]
            else:
                logger.warning(f"教师编号 {teacher_id} 不存在")
                return None
        except Exception as e:
            logger.error(f"获取教师信息失败: {e}")
            return None
    
    @staticmethod
    def get_teacher_by_user_id(user_id):
        """根据用户ID获取教师信息"""
        try:
            query = "SELECT * FROM teachers WHERE user_id = %s"
            result = db_manager.execute_query(query, (user_id,))
            
            if result and len(result) > 0:
                return result[0]
            else:
                logger.warning(f"用户ID {user_id} 对应的教师信息不存在")
                return None
        except Exception as e:
            logger.error(f"获取教师信息失败: {e}")
            return None
    
    @staticmethod
    def get_all_teachers():
        """获取所有教师信息(管理员权限)"""
        try:
            query = "SELECT * FROM teachers"
            result = db_manager.execute_query(query)
            return result
        except Exception as e:
            logger.error(f"获取所有教师信息失败: {e}")
            return None
    
    @staticmethod
    def search_teachers(keyword):
        """搜索教师信息(管理员权限)"""
        try:
            query = "SELECT * FROM teachers WHERE teacher_id LIKE %s OR name LIKE %s"
            keyword = f"%{keyword}%"
            result = db_manager.execute_query(query, (keyword, keyword))
            return result
        except Exception as e:
            logger.error(f"搜索教师信息失败: {e}")
            return None
    
    @staticmethod
    def delete_teacher(teacher_id):
        """删除教师信息(管理员权限)"""
        try:
            query = "DELETE FROM teachers WHERE teacher_id = %s"
            result = db_manager.execute_update(query, (teacher_id,))
            
            if result > 0:
                logger.info(f"教师 (编号: {teacher_id}) 删除成功")
                return True
            else:
                logger.warning(f"教师 (编号: {teacher_id}) 删除失败")
                return False
        except Exception as e:
            logger.error(f"删除教师信息失败: {e}")
            return False