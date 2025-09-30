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

    @staticmethod
    def get_courses_by_student(student_internal_id, semester=None):
        """根据学生获取已选课程信息（返回 courses 表记录）"""
        try:
            if semester:
                query = (
                    "SELECT c.* FROM enrollments e "
                    "JOIN courses c ON e.course_id = c.id "
                    "WHERE e.student_id = %s AND e.semester = %s"
                )
                params = (student_internal_id, semester)
            else:
                query = (
                    "SELECT c.* FROM enrollments e "
                    "JOIN courses c ON e.course_id = c.id "
                    "WHERE e.student_id = %s"
                )
                params = (student_internal_id,)
            return db_manager.execute_query(query, params)
        except Exception as e:
            logger.error(f"获取学生课程失败: {e}")
            return None

    @staticmethod
    def check_time_conflict(student_internal_id, course_id, semester):
        """
        检查课程时间冲突
        返回: (bool, str) - (是否冲突, 冲突信息)
        """
        try:
            # 获取要选的课程的上课时间
            query = "SELECT course_name, class_time FROM courses WHERE id = %s"
            result = db_manager.execute_query(query, (course_id,))
            
            if not result or not result[0].get('class_time'):
                # 如果课程不存在或没有设置上课时间，不算冲突
                return False, ""
            
            target_course = result[0]
            target_time = target_course['class_time']
            
            # 解析上课时间（格式：周X HH:MM-HH:MM）
            target_day, target_period = Enrollment._parse_time(target_time)
            if not target_day:
                # 无法解析时间，不算冲突
                return False, ""
            
            # 获取学生在该学期已选的所有课程
            enrolled_courses = Enrollment.get_courses_by_student(student_internal_id, semester)
            
            if not enrolled_courses:
                return False, ""
            
            # 检查时间冲突
            for course in enrolled_courses:
                if not course.get('class_time'):
                    continue
                
                enrolled_day, enrolled_period = Enrollment._parse_time(course['class_time'])
                if not enrolled_day:
                    continue
                
                # 检查是否同一天
                if enrolled_day == target_day:
                    # 检查时间段是否重叠
                    if Enrollment._time_overlap(target_period, enrolled_period):
                        conflict_msg = f"与已选课程《{course['course_name']}》时间冲突（{course['class_time']}）"
                        logger.warning(f"选课时间冲突: {conflict_msg}")
                        return True, conflict_msg
            
            return False, ""
            
        except Exception as e:
            logger.error(f"检查时间冲突失败: {e}")
            return False, ""
    
    @staticmethod
    def _parse_time(time_str):
        """
        解析上课时间字符串
        输入格式: "周一 10:00-11:40" 或 "周一 08:00-09:40"
        返回: (day, (start_time, end_time)) 或 (None, None)
        """
        try:
            if not time_str:
                return None, None
            
            # 分割日期和时间
            parts = time_str.strip().split()
            if len(parts) < 2:
                return None, None
            
            day = parts[0]  # 周几
            time_range = parts[1]  # 时间段
            
            # 解析时间段
            if '-' not in time_range:
                return None, None
            
            start_str, end_str = time_range.split('-')
            
            # 将时间转换为分钟数（方便比较）
            start_minutes = Enrollment._time_to_minutes(start_str)
            end_minutes = Enrollment._time_to_minutes(end_str)
            
            if start_minutes is None or end_minutes is None:
                return None, None
            
            return day, (start_minutes, end_minutes)
            
        except Exception as e:
            logger.error(f"解析时间失败: {e}")
            return None, None
    
    @staticmethod
    def _time_to_minutes(time_str):
        """将时间字符串转换为分钟数（从0:00开始计算）"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return hour * 60 + minute
        except:
            return None
    
    @staticmethod
    def _time_overlap(period1, period2):
        """
        检查两个时间段是否重叠
        period1, period2: (start_minutes, end_minutes)
        """
        start1, end1 = period1
        start2, end2 = period2
        
        # 时间段重叠的条件：
        # period1的开始时间在period2范围内，或
        # period2的开始时间在period1范围内
        return (start1 < end2 and start2 < end1)
    
    @staticmethod
    def get_available_courses(student_internal_id, semester):
        """
        获取学生可选的课程列表（排除已选课程）
        """
        try:
            # 获取所有该学期的课程
            query = """
                SELECT c.*, t.name as teacher_name
                FROM courses c
                LEFT JOIN teachers t ON c.teacher_id = t.id
                WHERE c.semester = %s
            """
            all_courses = db_manager.execute_query(query, (semester,))
            
            if not all_courses:
                return []
            
            # 获取学生已选课程的ID列表
            enrolled_query = """
                SELECT course_id 
                FROM enrollments 
                WHERE student_id = %s AND semester = %s
            """
            enrolled = db_manager.execute_query(enrolled_query, (student_internal_id, semester))
            enrolled_ids = {e['course_id'] for e in enrolled} if enrolled else set()
            
            # 过滤掉已选课程
            available_courses = [c for c in all_courses if c['id'] not in enrolled_ids]
            
            return available_courses
            
        except Exception as e:
            logger.error(f"获取可选课程失败: {e}")
            return []
    
    @staticmethod
    def check_already_enrolled(student_internal_id, course_id, semester):
        """检查学生是否已选该课程"""
        try:
            query = """
                SELECT id FROM enrollments 
                WHERE student_id = %s AND course_id = %s AND semester = %s
            """
            result = db_manager.execute_query(query, (student_internal_id, course_id, semester))
            return result and len(result) > 0
        except Exception as e:
            logger.error(f"检查选课状态失败: {e}")
            return False


