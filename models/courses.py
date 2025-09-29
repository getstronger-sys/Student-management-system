#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""课程模型，处理课程相关的业务逻辑"""

from database.db_manager import db_manager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('course_model')


class Course:
    """课程类，封装课程相关的业务逻辑"""
    
    @staticmethod
    def add_course(course_code, course_name, credits, teacher_id, semester, time=None):
        """添加课程信息"""
        try:
            # 检查课程代码是否已存在
            query = "SELECT * FROM courses WHERE course_code = %s"
            result = db_manager.execute_query(query, (course_code,))
            
            if result and len(result) > 0:
                logger.warning(f"添加课程失败: 课程代码 {course_code} 已存在")
                return False
            
            # 验证teacher_id是否存在
            if teacher_id is not None:
                teacher_query = "SELECT id FROM teachers WHERE id = %s"
                teacher_result = db_manager.execute_query(teacher_query, (teacher_id,))
                
                if not teacher_result:
                    logger.error(f"添加课程失败: 教师ID {teacher_id} 不存在")
                    return False
            
            # 插入课程信息
            query = "INSERT INTO courses (course_code, course_name, credits, teacher_id, semester) VALUES (%s, %s, %s, %s, %s)"
            result = db_manager.execute_update(query, (course_code, course_name, credits, teacher_id, semester))
            
            if result > 0:
                logger.info(f"课程 {course_name} (代码: {course_code}) 添加成功")
                return True
            else:
                logger.warning(f"课程 {course_name} (代码: {course_code}) 添加失败")
                return False
        except Exception as e:
            logger.error(f"添加课程信息失败: {e}")
            return False
    
    @staticmethod
    def update_course(course_id, code, name, credit, teacher_id, semester, time):
        """更新课程信息"""
        try:
            # 构建更新语句
            updates = []
            params = []
            
            # 验证teacher_id是否存在（如果提供了非空值）
            if teacher_id is not None:
                # 检查教师ID是否存在
                teacher_query = "SELECT id FROM teachers WHERE id = %s"
                teacher_result = db_manager.execute_query(teacher_query, (teacher_id,))
                
                if not teacher_result:
                    logger.error(f"更新课程失败: 教师ID {teacher_id} 不存在")
                    return False
                
                updates.append("teacher_id = %s")
                params.append(teacher_id)
            
            if code:
                updates.append("course_code = %s")
                params.append(code)
            
            if name:
                updates.append("course_name = %s")
                params.append(name)
            
            if credit is not None:
                updates.append("credits = %s")
                params.append(credit)
            
            if semester:
                updates.append("semester = %s")
                params.append(semester)
            
            if not updates:
                return True
            
            # 添加course_id到参数列表
            params.append(course_id)
            
            # 执行更新
            query = f"UPDATE courses SET {', '.join(updates)} WHERE id = %s"
            result = db_manager.execute_update(query, tuple(params))
            
            if result > 0:
                logger.info(f"课程 (ID: {course_id}) 信息更新成功")
                return True
            else:
                logger.warning(f"课程 (ID: {course_id}) 信息更新失败")
                return False
        except Exception as e:
            logger.error(f"更新课程信息失败: {e}")
            return False
    
    @staticmethod
    def get_course_by_code(course_code):
        """根据课程代码获取课程信息"""
        try:
            query = "SELECT * FROM courses WHERE course_code = %s"
            result = db_manager.execute_query(query, (course_code,))
            
            if result and len(result) > 0:
                return result[0]
            else:
                logger.warning(f"课程代码 {course_code} 不存在")
                return None
        except Exception as e:
            logger.error(f"获取课程信息失败: {e}")
            return None
    
    @staticmethod
    def get_courses_by_teacher_id(teacher_id):
        """根据教师ID获取教授的课程"""
        try:
            query = "SELECT * FROM courses WHERE teacher_id = %s"
            result = db_manager.execute_query(query, (teacher_id,))
            return result
        except Exception as e:
            logger.error(f"获取教师课程失败: {e}")
            return None
    
    @staticmethod
    def get_all_courses():
        """获取所有课程信息(管理员/教师权限)"""
        try:
            query = "SELECT * FROM courses"
            result = db_manager.execute_query(query)
            return result
        except Exception as e:
            logger.error(f"获取所有课程信息失败: {e}")
            return None
    
    @staticmethod
    def search_courses(keyword):
        """搜索课程信息(管理员/教师/学生权限)"""
        try:
            query = "SELECT * FROM courses WHERE course_code LIKE %s OR course_name LIKE %s OR semester LIKE %s"
            keyword = f"%{keyword}%"
            result = db_manager.execute_query(query, (keyword, keyword, keyword))
            return result
        except Exception as e:
            logger.error(f"搜索课程信息失败: {e}")
            return None
    
    @staticmethod
    def delete_course(course_id):
        """删除课程信息(管理员权限)"""
        try:
            query = "DELETE FROM courses WHERE id = %s"
            result = db_manager.execute_update(query, (course_id,))
            
            if result > 0:
                logger.info(f"课程 (ID: {course_id}) 删除成功")
                return True
            else:
                logger.warning(f"课程 (ID: {course_id}) 删除失败")
                return False
        except Exception as e:
            logger.error(f"删除课程信息失败: {e}")
            return False