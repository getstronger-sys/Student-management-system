#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""学生模型，处理学生相关的业务逻辑"""

from database.db_manager import db_manager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('student_model')


class Student:
    """学生类，封装学生相关的业务逻辑"""
    
    @staticmethod
    def add_student(student_id, name, gender, birth, class_name, major, user_id):
        """添加学生信息"""
        try:
            # 检查学号是否已存在
            query = "SELECT * FROM students WHERE student_id = %s"
            result = db_manager.execute_query(query, (student_id,))
            
            if result and len(result) > 0:
                logger.warning(f"添加学生失败: 学号 {student_id} 已存在")
                return False
            
            # 插入学生信息
            query = "INSERT INTO students (student_id, name, gender, birth, class, major, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            result = db_manager.execute_update(query, (student_id, name, gender, birth, class_name, major, user_id))
            
            if result > 0:
                logger.info(f"学生 {name} (学号: {student_id}) 添加成功")
                return True
            else:
                logger.warning(f"学生 {name} (学号: {student_id}) 添加失败")
                return False
        except Exception as e:
            logger.error(f"添加学生信息失败: {e}")
            return False
    
    @staticmethod
    def update_student(student_id, name=None, gender=None, birth=None, class_name=None, major=None):
        """更新学生信息"""
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
            
            if birth:
                updates.append("birth = %s")
                params.append(birth)
            
            if class_name:
                updates.append("class = %s")
                params.append(class_name)
            
            if major:
                updates.append("major = %s")
                params.append(major)
            
            if not updates:
                return True
            
            # 添加student_id到参数列表
            params.append(student_id)
            
            # 执行更新
            query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = %s"
            result = db_manager.execute_update(query, tuple(params))
            
            if result > 0:
                logger.info(f"学生 (学号: {student_id}) 信息更新成功")
                return True
            else:
                logger.warning(f"学生 (学号: {student_id}) 信息更新失败")
                return False
        except Exception as e:
            logger.error(f"更新学生信息失败: {e}")
            return False
    
    @staticmethod
    def get_student_by_id(student_id):
        """根据学号获取学生信息"""
        try:
            query = "SELECT * FROM students WHERE student_id = %s"
            result = db_manager.execute_query(query, (student_id,))
            
            if result and len(result) > 0:
                return result[0]
            else:
                logger.warning(f"学号 {student_id} 不存在")
                return None
        except Exception as e:
            logger.error(f"获取学生信息失败: {e}")
            return None
    
    @staticmethod
    def get_student_by_user_id(user_id):
        """根据用户ID获取学生信息"""
        try:
            query = "SELECT * FROM students WHERE user_id = %s"
            result = db_manager.execute_query(query, (user_id,))
            
            if result and len(result) > 0:
                return result[0]
            else:
                logger.warning(f"用户ID {user_id} 对应的学生信息不存在")
                return None
        except Exception as e:
            logger.error(f"获取学生信息失败: {e}")
            return None
    
    @staticmethod
    def get_all_students():
        """获取所有学生信息(管理员/教师权限)"""
        try:
            query = "SELECT * FROM students"
            result = db_manager.execute_query(query)
            return result
        except Exception as e:
            logger.error(f"获取所有学生信息失败: {e}")
            return None
    
    @staticmethod
    def search_students(keyword):
        """搜索学生信息(管理员/教师权限)"""
        try:
            query = "SELECT * FROM students WHERE student_id LIKE %s OR name LIKE %s"
            keyword = f"%{keyword}%"
            result = db_manager.execute_query(query, (keyword, keyword))
            return result
        except Exception as e:
            logger.error(f"搜索学生信息失败: {e}")
            return None
    
    @staticmethod
    def delete_student(student_id):
        """删除学生信息(管理员权限)"""
        try:
            query = "DELETE FROM students WHERE student_id = %s"
            result = db_manager.execute_update(query, (student_id,))
            
            if result > 0:
                logger.info(f"学生 (学号: {student_id}) 删除成功")
                return True
            else:
                logger.warning(f"学生 (学号: {student_id}) 删除失败")
                return False
        except Exception as e:
            logger.error(f"删除学生信息失败: {e}")
            return False