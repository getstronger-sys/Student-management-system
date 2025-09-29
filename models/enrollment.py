#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""选课模型，处理学生与课程的选课关系"""

from database.db_manager import db_manager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('enrollment_model')


class Enrollment:
    """选课类，封装选课相关的业务逻辑"""

    @staticmethod
    def enroll(student_internal_id, course_id, semester=None):
        """学生选课（使用内部自增学生ID，不是学号）"""
        try:
            query = "INSERT INTO enrollments (student_id, course_id, semester) VALUES (%s, %s, %s)"
            result = db_manager.execute_update(query, (student_internal_id, course_id, semester))
            return result > 0
        except Exception as e:
            logger.error(f"选课失败: {e}")
            return False

    @staticmethod
    def unenroll(student_internal_id, course_id, semester=None):
        """退选课程"""
        try:
            if semester:
                query = "DELETE FROM enrollments WHERE student_id = %s AND course_id = %s AND semester = %s"
                params = (student_internal_id, course_id, semester)
            else:
                query = "DELETE FROM enrollments WHERE student_id = %s AND course_id = %s"
                params = (student_internal_id, course_id)
            result = db_manager.execute_update(query, params)
            return result > 0
        except Exception as e:
            logger.error(f"退选失败: {e}")
            return False

    @staticmethod
    def get_students_by_course(course_id, semester=None):
        """根据课程获取已选该课的学生信息（返回 students 表记录）"""
        try:
            if semester:
                query = (
                    "SELECT st.* FROM enrollments e "
                    "JOIN students st ON e.student_id = st.id "
                    "WHERE e.course_id = %s AND e.semester = %s"
                )
                params = (course_id, semester)
            else:
                query = (
                    "SELECT st.* FROM enrollments e "
                    "JOIN students st ON e.student_id = st.id "
                    "WHERE e.course_id = %s"
                )
                params = (course_id,)
            return db_manager.execute_query(query, params)
        except Exception as e:
            logger.error(f"获取课程学生失败: {e}")
            return None

    @staticmethod
    def count_students_by_course(course_id, semester=None):
        """统计选了该课程的学生人数"""
        try:
            if semester:
                query = "SELECT COUNT(DISTINCT student_id) AS cnt FROM enrollments WHERE course_id = %s AND semester = %s"
                params = (course_id, semester)
            else:
                query = "SELECT COUNT(DISTINCT student_id) AS cnt FROM enrollments WHERE course_id = %s"
                params = (course_id,)
            result = db_manager.execute_query(query, params)
            return (result and result[0]['cnt']) or 0
        except Exception as e:
            logger.error(f"统计课程学生数失败: {e}")
            return 0


