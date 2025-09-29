#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""检查数据库中的课程和成绩数据"""

import pymysql
import config.config as cfg

# 连接数据库
conn = pymysql.connect(
    host=cfg.DB_CONFIG['host'],
    port=cfg.DB_CONFIG['port'],
    user=cfg.DB_CONFIG['user'],
    password=cfg.DB_CONFIG['password'],
    database=cfg.DB_CONFIG['database'],
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()

# 检查课程数据
print('检查课程数据:')
cursor.execute('SELECT id, course_name, teacher_id FROM courses LIMIT 5')
courses = cursor.fetchall()
for course in courses:
    print(f"课程ID: {course['id']}, 课程名称: {course['course_name']}, 教师ID: {course['teacher_id']}")

# 检查成绩数据
print('\n检查成绩数据:')
cursor.execute('SELECT course_id, COUNT(DISTINCT student_id) as student_count FROM scores GROUP BY course_id LIMIT 5')
scores = cursor.fetchall()
for score in scores:
    print(f"课程ID: {score['course_id']}, 学生人数: {score['student_count']}")

# 检查特定教师的课程
print('\n检查特定教师的课程与学生人数:')
if courses:
    # 获取第一个教师的ID
    teacher_id = courses[0]['teacher_id']
    print(f"教师ID: {teacher_id}")
    
    # 查询该教师的所有课程
    cursor.execute('SELECT id, course_name FROM courses WHERE teacher_id = %s', (teacher_id,))
    teacher_courses = cursor.fetchall()
    
    for course in teacher_courses:
        # 查询该课程的学生人数
        cursor.execute('SELECT COUNT(DISTINCT student_id) as student_count FROM scores WHERE course_id = %s', (course['id'],))
        count_result = cursor.fetchone()
        student_count = count_result['student_count'] if count_result else 0
        print(f"课程ID: {course['id']}, 课程名称: {course['course_name']}, 学生人数: {student_count}")

cursor.close()
conn.close()