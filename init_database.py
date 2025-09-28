#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""数据库初始化脚本

此脚本用于初始化学生管理系统的数据库，包括：
1. 检查MySQL服务是否可用
2. 创建数据库和表结构
3. 插入测试数据（管理员、教师、学生、课程和成绩）

使用方法：
python init_database.py
"""

import pymysql
import sys
import os
import hashlib
from pymysql.cursors import DictCursor
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('init_database')

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'zhyzywxj1825907',  # 默认密码，实际使用时应修改
    'database': 'student_management',
    'port': 3306
}

def check_mysql_connection():
    """检查MySQL服务是否可用"""
    try:
        # 尝试连接MySQL服务器
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port'],
            connect_timeout=5
        )
        conn.close()
        logger.info("MySQL服务连接成功")
        return True
    except Exception as e:
        logger.error(f"MySQL服务连接失败: {e}")
        logger.error("请确认MySQL服务是否已启动，以及用户名和密码是否正确")
        logger.error("如果需要修改数据库配置，请编辑此脚本中的DB_CONFIG变量")
        return False

def init_database():
    """初始化数据库，创建表结构并插入测试数据"""
    try:
        # 连接MySQL服务器
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port'],
            cursorclass=DictCursor
        )
        cursor = conn.cursor()
        
        # 创建数据库
        logger.info(f"创建数据库: {DB_CONFIG['database']}")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.select_db(DB_CONFIG['database'])
        
        # 创建用户表
        logger.info("创建用户表")
        cursor.execute('''
            CREATE TABLE users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                role VARCHAR(20) NOT NULL,
                name VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建学生表
        logger.info("创建学生表")
        cursor.execute('''
            CREATE TABLE students (
                id INT PRIMARY KEY AUTO_INCREMENT,
                student_id VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(50) NOT NULL,
                gender VARCHAR(10),
                birth DATE,
                class VARCHAR(50),
                major VARCHAR(50),
                user_id INT UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # 创建教师表
        logger.info("创建教师表")
        cursor.execute('''
            CREATE TABLE teachers (
                id INT PRIMARY KEY AUTO_INCREMENT,
                teacher_id VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(50) NOT NULL,
                gender VARCHAR(10),
                title VARCHAR(50),
                department VARCHAR(50),
                user_id INT UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # 创建课程表
        logger.info("创建课程表")
        cursor.execute('''
            CREATE TABLE courses (
                id INT PRIMARY KEY AUTO_INCREMENT,
                course_code VARCHAR(20) UNIQUE NOT NULL,
                course_name VARCHAR(100) NOT NULL,
                credits FLOAT NOT NULL,
                teacher_id INT,
                semester VARCHAR(20),
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
            )
        ''')
        
        # 创建成绩表
        logger.info("创建成绩表")
        cursor.execute('''
            CREATE TABLE scores (
                id INT PRIMARY KEY AUTO_INCREMENT,
                student_id INT NOT NULL,
                course_id INT NOT NULL,
                score FLOAT NOT NULL,
                semester VARCHAR(20),
                exam_time DATE,
                UNIQUE KEY unique_score (student_id, course_id, semester),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        ''')
        
        # 插入测试数据
        logger.info("插入测试数据")
        
        # 密码哈希函数，与models/user.py中保持一致
        def hash_password(password):
            """密码加密"""
            return hashlib.sha256(password.encode()).hexdigest()

        # 插入管理员用户
        admin_password = hash_password('admin123')
        cursor.execute('''
            INSERT INTO users (username, password, role, name) 
            VALUES ('admin', %s, 'admin', '系统管理员')
        ''', (admin_password,))
        admin_user_id = cursor.lastrowid
        
        # 插入教师用户
        teachers = [
            ('teacher1', hash_password('teacher123'), 'teacher', '张教授'),
            ('teacher2', hash_password('teacher123'), 'teacher', '李讲师')
        ]
        for teacher in teachers:
            cursor.execute(
                'INSERT INTO users (username, password, role, name) VALUES (%s, %s, %s, %s)',
                teacher
            )
        
        # 插入教师信息
        cursor.execute('''
            INSERT INTO teachers (teacher_id, name, gender, title, department, user_id) 
            VALUES ('T001', '张教授', '男', '教授', '计算机学院', (SELECT id FROM users WHERE username='teacher1'))
        ''')
        teacher1_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO teachers (teacher_id, name, gender, title, department, user_id) 
            VALUES ('T002', '李讲师', '女', '讲师', '信息学院', (SELECT id FROM users WHERE username='teacher2'))
        ''')
        teacher2_id = cursor.lastrowid
        
        # 插入学生用户
        students = [
            ('student1', hash_password('student123'), 'student', '王同学'),
            ('student2', hash_password('student123'), 'student', '陈同学'),
            ('student3', hash_password('student123'), 'student', '赵同学')
        ]
        for student in students:
            cursor.execute(
                'INSERT INTO users (username, password, role, name) VALUES (%s, %s, %s, %s)',
                student
            )
        
        # 插入学生信息
        cursor.execute('''
            INSERT INTO students (student_id, name, gender, birth, class, major, user_id) 
            VALUES ('S001', '王同学', '男', '2003-01-15', '计科2101', '计算机科学与技术', (SELECT id FROM users WHERE username='student1'))
        ''')
        student1_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO students (student_id, name, gender, birth, class, major, user_id) 
            VALUES ('S002', '陈同学', '女', '2003-03-22', '计科2101', '计算机科学与技术', (SELECT id FROM users WHERE username='student2'))
        ''')
        student2_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO students (student_id, name, gender, birth, class, major, user_id) 
            VALUES ('S003', '赵同学', '男', '2002-11-30', '计科2102', '计算机科学与技术', (SELECT id FROM users WHERE username='student3'))
        ''')
        student3_id = cursor.lastrowid
        
        # 插入课程
        courses = [
            ('CS101', 'Python程序设计', 3.0, teacher1_id, '2025-2026-1'),
            ('CS102', '数据结构', 4.0, teacher1_id, '2025-2026-1'),
            ('CS201', '计算机网络', 3.0, teacher2_id, '2025-2026-1')
        ]
        for course in courses:
            cursor.execute(
                'INSERT INTO courses (course_code, course_name, credits, teacher_id, semester) VALUES (%s, %s, %s, %s, %s)',
                course
            )
        
        # 获取课程ID
        cursor.execute('SELECT id FROM courses WHERE course_code="CS101"')
        cs101_id = cursor.fetchone()['id']
        
        cursor.execute('SELECT id FROM courses WHERE course_code="CS102"')
        cs102_id = cursor.fetchone()['id']
        
        cursor.execute('SELECT id FROM courses WHERE course_code="CS201"')
        cs201_id = cursor.fetchone()['id']
        
        # 插入成绩
        scores = [
            # 王同学的成绩
            (student1_id, cs101_id, 85.5, '2025-2026-1', '2025-12-20'),
            (student1_id, cs102_id, 92.0, '2025-2026-1', '2025-12-22'),
            (student1_id, cs201_id, 78.5, '2025-2026-1', '2025-12-25'),
            # 陈同学的成绩
            (student2_id, cs101_id, 90.0, '2025-2026-1', '2025-12-20'),
            (student2_id, cs102_id, 88.5, '2025-2026-1', '2025-12-22'),
            (student2_id, cs201_id, 94.0, '2025-2026-1', '2025-12-25'),
            # 赵同学的成绩
            (student3_id, cs101_id, 76.0, '2025-2026-1', '2025-12-20'),
            (student3_id, cs102_id, 82.5, '2025-2026-1', '2025-12-22'),
            (student3_id, cs201_id, 79.0, '2025-2026-1', '2025-12-25')
        ]
        for score in scores:
            cursor.execute(
                'INSERT INTO scores (student_id, course_id, score, semester, exam_time) VALUES (%s, %s, %s, %s, %s)',
                score
            )
        
        # 提交事务
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("数据库初始化成功！")
        logger.info("\n测试账号信息：")
        logger.info("1. 管理员账号：")
        logger.info("   用户名: admin")
        logger.info("   密码: admin123")
        logger.info("   角色: 管理员")
        logger.info("\n2. 教师账号：")
        logger.info("   用户名: teacher1")
        logger.info("   密码: teacher123")
        logger.info("   角色: 教师")
        logger.info("   用户名: teacher2")
        logger.info("   密码: teacher123")
        logger.info("   角色: 教师")
        logger.info("\n3. 学生账号：")
        logger.info("   用户名: student1")
        logger.info("   密码: student123")
        logger.info("   角色: 学生")
        logger.info("   用户名: student2")
        logger.info("   密码: student123")
        logger.info("   角色: 学生")
        logger.info("   用户名: student3")
        logger.info("   密码: student123")
        logger.info("   角色: 学生")
        logger.info("\n现在您可以运行 'python main.py' 启动学生管理系统客户端了！")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def main():
    """主函数"""
    logger.info("开始初始化学生管理系统数据库...")
    
    # 检查MySQL连接
    if not check_mysql_connection():
        logger.error("数据库初始化失败，请先确保MySQL服务正常运行。")
        sys.exit(1)
    
    # 初始化数据库
    if init_database():
        logger.info("数据库初始化完成！")
        sys.exit(0)
    else:
        logger.error("数据库初始化失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()