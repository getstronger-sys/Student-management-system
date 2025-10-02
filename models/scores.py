#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""成绩模型，处理成绩相关的业务逻辑"""

from database.db_manager import db_manager
import logging
import numpy as np
from datetime import datetime
from .enrollment import Enrollment

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('score_model')


class Score:
    """成绩类，封装成绩相关的业务逻辑"""
    
    @staticmethod
    def add_score(student_id, course_id, score, semester, exam_time=None):
        """添加成绩信息"""
        try:
            # 检查成绩是否已存在
            query = "SELECT * FROM scores WHERE student_id = %s AND course_id = %s AND semester = %s"
            result = db_manager.execute_query(query, (student_id, course_id, semester))
            
            if result and len(result) > 0:
                logger.warning(f"添加成绩失败: 该学生在该学期的该课程成绩已存在")
                return False
            
            # 如果没有提供考试时间，使用当前时间
            if not exam_time:
                exam_time = datetime.now().strftime('%Y-%m-%d')
            
            # 插入成绩信息
            query = "INSERT INTO scores (student_id, course_id, score, semester, exam_time) VALUES (%s, %s, %s, %s, %s)"
            result = db_manager.execute_update(query, (student_id, course_id, score, semester, exam_time))
            
            if result > 0:
                # 确保存在选课记录，以便学生管理界面展示
                try:
                    Enrollment.enroll(student_id, course_id, semester)
                except Exception:
                    pass
                logger.info(f"成绩添加成功")
                return True
            else:
                logger.warning(f"成绩添加失败")
                return False
        except Exception as e:
            logger.error(f"添加成绩信息失败: {e}")
            return False
    
    @staticmethod
    def update_score(student_id, course_id, semester, score=None, exam_time=None):
        """更新成绩信息"""
        try:
            # 构建更新语句
            updates = []
            params = []
            
            if score is not None:
                updates.append("score = %s")
                params.append(score)
            
            if exam_time:
                updates.append("exam_time = %s")
                params.append(exam_time)
            
            if not updates:
                return True
            
            # 添加条件参数
            params.extend([student_id, course_id, semester])
            
            # 执行更新
            query = f"UPDATE scores SET {', '.join(updates)} WHERE student_id = %s AND course_id = %s AND semester = %s"
            result = db_manager.execute_update(query, tuple(params))
            
            if result > 0:
                logger.info(f"成绩更新成功")
                return True
            else:
                logger.warning(f"成绩更新失败")
                return False
        except Exception as e:
            logger.error(f"更新成绩信息失败: {e}")
            return False

    @staticmethod
    def get_score_by_id(score_id):
        """根据成绩记录ID获取成绩信息"""
        try:
            query = "SELECT * FROM scores WHERE id = %s"
            result = db_manager.execute_query(query, (score_id,))
            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"获取成绩信息失败: {e}")
            return None

    @staticmethod
    def update_score_by_id(score_id, score=None, exam_time=None):
        """根据成绩记录ID更新成绩信息"""
        try:
            logger.info(f"尝试更新成绩记录 - ID: {score_id}, 分数: {score}, 考试时间: {exam_time}")
            updates = []
            params = []

            if score is not None:
                updates.append("score = %s")
                params.append(score)

            if exam_time:
                updates.append("exam_time = %s")
                params.append(exam_time)

            if not updates:
                logger.info("没有需要更新的字段")
                return True

            params.append(score_id)
            query = f"UPDATE scores SET {', '.join(updates)} WHERE id = %s"
            logger.info(f"生成的SQL查询: {query}")
            logger.info(f"查询参数: {params}")
            
            # 先检查记录是否存在
            existing_score = Score.get_score_by_id(score_id)
            if not existing_score:
                logger.warning(f"成绩记录不存在 - ID: {score_id}")
                return False
            
            logger.info(f"找到成绩记录: {existing_score}")
            result = db_manager.execute_update(query, tuple(params))
            logger.info(f"执行结果 - 影响行数: {result}")

            # MySQL在值没有变化时会返回0影响行数，但这并不意味着更新失败
            # 所以我们需要判断是否真的失败了
            if result > 0:
                logger.info("按ID更新成绩成功")
                return True
            else:
                # 检查是否是因为要更新的值与原值相同导致的
                value_changed = False
                if score is not None and existing_score.get('score') != score:
                    value_changed = True
                if exam_time and existing_score.get('exam_time') != exam_time:
                    value_changed = True
                
                if value_changed:
                    # 如果确实有值需要改变但更新失败
                    logger.warning("按ID更新成绩失败")
                    return False
                else:
                    # 如果要更新的值与原值相同，视为更新成功
                    logger.info("成绩值未变化，无需实际更新")
                    return True
        except Exception as e:
            logger.error(f"按ID更新成绩失败: {e}")
            return False
    
    @staticmethod
    def get_scores_by_student_id(student_id):
        """根据学生ID获取成绩信息"""
        try:
            query = """
                SELECT s.*, c.course_name, c.course_code, c.credits 
                FROM scores s 
                JOIN courses c ON s.course_id = c.id 
                WHERE s.student_id = %s
            """
            result = db_manager.execute_query(query, (student_id,))
            return result
        except Exception as e:
            logger.error(f"获取学生成绩失败: {e}")
            return None
    
    @staticmethod
    def get_scores_by_course_id(course_id):
        """根据课程ID获取成绩信息"""
        try:
            query = """
                SELECT s.*, st.student_id, st.name 
                FROM scores s 
                JOIN students st ON s.student_id = st.id 
                WHERE s.course_id = %s
            """
            result = db_manager.execute_query(query, (course_id,))
            return result
        except Exception as e:
            logger.error(f"获取课程成绩失败: {e}")
            return None
    
    @staticmethod
    def get_scores_by_course_and_semester(course_id, semester):
        """根据课程ID和学期获取成绩信息"""
        try:
            query = """
                SELECT s.*, st.student_id, st.name AS student_name, c.credits 
                FROM scores s 
                JOIN students st ON s.student_id = st.id 
                JOIN courses c ON s.course_id = c.id 
                WHERE s.course_id = %s AND s.semester = %s
            """
            result = db_manager.execute_query(query, (course_id, semester))
            return result
        except Exception as e:
            logger.error(f"获取课程学期成绩失败: {e}")
            return None
    
    @staticmethod
    def calculate_gpa(student_id):
        """计算学生的GPA"""
        try:
            query = """
                SELECT s.score, c.credits 
                FROM scores s 
                JOIN courses c ON s.course_id = c.id 
                WHERE s.student_id = %s
            """
            results = db_manager.execute_query(query, (student_id,))
            
            if not results:
                return 0.0
            
            total_credits = 0.0
            weighted_sum = 0.0
            
            for row in results:
                score = row['score']
                credits = row['credits']
                
                # 将分数转换为绩点 (4.0分制)
                if score >= 90:
                    gpa = 4.0
                elif score >= 85:
                    gpa = 3.7
                elif score >= 80:
                    gpa = 3.3
                elif score >= 75:
                    gpa = 3.0
                elif score >= 70:
                    gpa = 2.7
                elif score >= 65:
                    gpa = 2.3
                elif score >= 60:
                    gpa = 2.0
                else:
                    gpa = 0.0
                
                weighted_sum += gpa * credits
                total_credits += credits
            
            if total_credits == 0:
                return 0.0
            
            return round(weighted_sum / total_credits, 2)
        except Exception as e:
            logger.error(f"计算GPA失败: {e}")
            return 0.0
    
    @staticmethod
    def get_score_statistics(course_id, semester):
        """获取课程成绩统计信息"""
        try:
            query = "SELECT score FROM scores WHERE course_id = %s AND semester = %s"
            results = db_manager.execute_query(query, (course_id, semester))
            
            if not results:
                return None
            
            scores = [row['score'] for row in results]
            scores_array = np.array(scores)
            
            # 计算统计指标
            stats = {
                'count': len(scores),
                'average': round(np.mean(scores_array), 2),
                'median': round(np.median(scores_array), 2),
                'max': round(np.max(scores_array), 2),
                'min': round(np.min(scores_array), 2),
                'std': round(np.std(scores_array), 2),
                # 计算各分数段人数
                'excellent': len([s for s in scores if s >= 90]),
                'good': len([s for s in scores if 80 <= s < 90]),
                'medium': len([s for s in scores if 70 <= s < 80]),
                'pass': len([s for s in scores if 60 <= s < 70]),
                'fail': len([s for s in scores if s < 60])
            }
            
            return stats
        except Exception as e:
            logger.error(f"获取成绩统计信息失败: {e}")
            return None
    
    @staticmethod
    def delete_score(student_id, course_id, semester):
        """删除成绩信息"""
        try:
            query = "DELETE FROM scores WHERE student_id = %s AND course_id = %s AND semester = %s"
            result = db_manager.execute_update(query, (student_id, course_id, semester))
            
            if result > 0:
                logger.info(f"成绩删除成功")
                return True
            else:
                logger.warning(f"成绩删除失败")
                return False
        except Exception as e:
            logger.error(f"删除成绩信息失败: {e}")
            return False