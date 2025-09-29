#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""数据库管理模块，处理数据库连接和基本操作"""

import pymysql
from pymysql.cursors import DictCursor
from config.config import DB_CONFIG
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('db_manager')


class DatabaseManager:
    """数据库管理类，封装数据库操作"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port'],
                cursorclass=DictCursor,
                autocommit=True
            )
            self.cursor = self.connection.cursor()
            logger.info("数据库连接成功")
            # 连接成功后执行必要的迁移（如新增 email 字段）
            self._migrate_schema()
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            # 如果数据库不存在，尝试创建
            if 'Unknown database' in str(e):
                self._create_database()
    
    def _create_database(self):
        """创建数据库和表结构"""
        try:
            # 先连接MySQL服务器
            temp_conn = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                port=DB_CONFIG['port'],
                cursorclass=DictCursor
            )
            temp_cursor = temp_conn.cursor()
            
            # 创建数据库
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            temp_conn.select_db(DB_CONFIG['database'])
            
            # 创建用户表
            temp_cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    email VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建学生表
            temp_cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
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
            temp_cursor.execute('''
                CREATE TABLE IF NOT EXISTS teachers (
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
            temp_cursor.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    course_code VARCHAR(20) UNIQUE NOT NULL,
                    course_name VARCHAR(100) NOT NULL,
                    credits FLOAT NOT NULL,
                    teacher_id INT,
                    semester VARCHAR(20),
                    class_time VARCHAR(100),
                    class_location VARCHAR(100),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
                )
            ''')
            
            # 创建成绩表
            temp_cursor.execute('''
                CREATE TABLE IF NOT EXISTS scores (
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

            # 创建选课表（用于表示学生选了哪些课程，不依赖成绩）
            temp_cursor.execute('''
                CREATE TABLE IF NOT EXISTS enrollments (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    student_id INT NOT NULL,
                    course_id INT NOT NULL,
                    semester VARCHAR(20),
                    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_enrollment (student_id, course_id, semester),
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
                )
            ''')
            
            # 插入管理员用户
            temp_cursor.execute('''
                INSERT IGNORE INTO users (username, password, role, name) 
                VALUES ('admin', 'admin123', 'admin', '系统管理员')
            ''')
            
            temp_conn.commit()
            temp_cursor.close()
            temp_conn.close()
            
            # 重新连接到新创建的数据库
            self.connect()
            logger.info("数据库和表结构创建成功")
        except Exception as e:
            logger.error(f"创建数据库失败: {e}")
    
    def _migrate_schema(self):
        """执行必要的数据库迁移（幂等）"""
        try:
            # 确保 users 表存在 email 字段（MySQL 8.0 支持 IF NOT EXISTS）
            self.cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(100)")
            
            # 确保 courses 表存在 class_time 字段
            try:
                self.cursor.execute("ALTER TABLE courses ADD COLUMN IF NOT EXISTS class_time VARCHAR(100)")
            except Exception as e:
                # 如果目标版本较低不支持 IF NOT EXISTS，则检查字段是否存在再添加
                try:
                    self.cursor.execute("SHOW COLUMNS FROM courses LIKE 'class_time'")
                    col = self.cursor.fetchone()
                    if not col:
                        self.cursor.execute("ALTER TABLE courses ADD COLUMN class_time VARCHAR(100)")
                except Exception as inner_e:
                    logger.warning(f"添加课程表上课时间字段失败: {inner_e}")
            
            # 确保 courses 表存在 class_location 字段
            try:
                self.cursor.execute("ALTER TABLE courses ADD COLUMN IF NOT EXISTS class_location VARCHAR(100)")
            except Exception:
                try:
                    self.cursor.execute("SHOW COLUMNS FROM courses LIKE 'class_location'")
                    col = self.cursor.fetchone()
                    if not col:
                        self.cursor.execute("ALTER TABLE courses ADD COLUMN class_location VARCHAR(100)")
                except Exception as inner_e:
                    logger.warning(f"添加课程表上课地点字段失败: {inner_e}")

            # 确保存在选课表 enrollments
            try:
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS enrollments (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        student_id INT NOT NULL,
                        course_id INT NOT NULL,
                        semester VARCHAR(20),
                        enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY unique_enrollment (student_id, course_id, semester),
                        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
                    )
                ''')
            except Exception as e:
                logger.warning(f"创建选课表失败: {e}")
        except Exception as e:
            # 如果目标版本较低不支持 IF NOT EXISTS，则检查字段是否存在再添加
            try:
                self.cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
                col = self.cursor.fetchone()
                if not col:
                    self.cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(100)")
                
                # 检查并添加class_time字段
                self.cursor.execute("SHOW COLUMNS FROM courses LIKE 'class_time'")
                col = self.cursor.fetchone()
                if not col:
                    self.cursor.execute("ALTER TABLE courses ADD COLUMN class_time VARCHAR(100)")
                # 检查选课表是否存在，不存在则创建
                self.cursor.execute("SHOW TABLES LIKE 'enrollments'")
                tbl = self.cursor.fetchone()
                if not tbl:
                    self.cursor.execute('''
                        CREATE TABLE enrollments (
                            id INT PRIMARY KEY AUTO_INCREMENT,
                            student_id INT NOT NULL,
                            course_id INT NOT NULL,
                            semester VARCHAR(20),
                            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE KEY unique_enrollment (student_id, course_id, semester),
                            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
                        )
                    ''')
            except Exception as inner_e:
                logger.warning(f"迁移检查失败: {inner_e}")
    
    def execute_query(self, query, params=None):
        """执行查询语句"""
        try:
            if not self.connection or not self.connection.open:
                self.connect()
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """执行更新语句(插入、更新、删除)"""
        try:
            if not self.connection or not self.connection.open:
                self.connect()
            result = self.cursor.execute(query, params)
            self.connection.commit()
            return result
        except Exception as e:
            logger.error(f"更新执行失败: {e}")
            if self.connection:
                self.connection.rollback()
            return 0
    
    def close(self):
        """关闭数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.open:
                self.connection.close()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")


# 创建全局数据库管理器实例
db_manager = DatabaseManager()