#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""数据库管理模块，处理数据库连接和基本操作"""

import pymysql
from pymysql.cursors import DictCursor
import logging
import os
import subprocess
import datetime
import shutil
from pathlib import Path

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',  # Docker数据库密码（与docker-compose.yml一致）
    'database': 'student_management',  # 数据库名称（与docker-compose.yml一致）
    'port': 3306,
    'charset': 'utf8mb4'
}

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('db_manager')

# 备份文件存储路径
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')
# 缓存目录
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache')


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
    
    def backup_database(self, use_docker=False):
        """备份数据库到文件
        
        Args:
            use_docker: 是否使用Docker方式备份（当MySQL运行在Docker容器中时设置为True）
            
        Returns:
            备份文件路径，如果失败则返回None
        """
        try:
            # 确保备份目录存在
            os.makedirs(BACKUP_DIR, exist_ok=True)
            
            # 生成带时间戳的备份文件名
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(BACKUP_DIR, f'student_management_backup_{timestamp}.sql')
            
            if use_docker:
                # 使用Docker方式备份（推荐）
                # 检查docker是否可用
                try:
                    subprocess.run(['docker', '--version'], capture_output=True, text=True, check=True)
                except Exception as e:
                    logger.error(f"找不到docker命令，请确保Docker已安装: {e}")
                    return None
                
                # 检查容器是否存在并运行
                try:
                    subprocess.run([
                        'docker', 'exec', 'student_management_mysql', 
                        'mysql', '-u', DB_CONFIG['user'], f"-p{DB_CONFIG['password']}", 
                        '-e', 'SELECT 1'
                    ], capture_output=True, text=True, check=True)
                except Exception as e:
                    logger.error(f"Docker容器不可用或数据库连接失败: {e}")
                    return None
                
                # 使用docker exec运行容器内的mysqldump命令
                cmd = [
                    'docker', 'exec', 'student_management_mysql',
                    'mysqldump',
                    '-u', DB_CONFIG['user'],
                    f"-p{DB_CONFIG['password']}",
                    DB_CONFIG['database'],
                    '--default-character-set=utf8mb4'
                ]
                
                # 执行命令并将输出写入文件
                try:
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                except Exception as e:
                    logger.error(f"执行Docker备份命令时发生错误: {e}")
                    return None
            else:
                # 传统方式备份（需要主机安装MySQL工具）
                # 检查mysqldump命令是否可用
                try:
                    subprocess.run(['mysqldump', '--version'], capture_output=True, text=True, check=True)
                    use_cmd = False
                except (subprocess.SubprocessError, FileNotFoundError):
                    # 如果mysqldump不在PATH中，尝试使用cmd /c调用
                    try:
                        subprocess.run(['cmd', '/c', 'mysqldump', '--version'], capture_output=True, text=True, check=True)
                        use_cmd = True
                    except Exception as e:
                        logger.error(f"找不到mysqldump命令，请确保MySQL已安装并添加到系统PATH中或使用Docker方式备份: {e}")
                        return None
                
                # 使用mysqldump命令备份数据库
                if use_cmd:
                    cmd = [
                        'cmd', '/c',
                        f'mysqldump -h {DB_CONFIG["host"]} -u {DB_CONFIG["user"]} -p{DB_CONFIG["password"]} -P {DB_CONFIG["port"]} {DB_CONFIG["database"]} --result-file={backup_file} --default-character-set=utf8mb4'
                    ]
                else:
                    cmd = [
                        'mysqldump',
                        '-h', DB_CONFIG['host'],
                        '-u', DB_CONFIG['user'],
                        f"-p{DB_CONFIG['password']}",  # 注意这里密码和参数连在一起
                        '-P', str(DB_CONFIG['port']),
                        DB_CONFIG['database'],
                        '--result-file', backup_file,
                        '--default-character-set=utf8mb4'
                    ]
                
                # 执行命令
                result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"数据库备份成功，文件保存至: {backup_file}")
                return backup_file
            else:
                logger.error(f"数据库备份失败: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"数据库备份过程中发生错误: {e}")
            return None
    
    def restore_database(self, backup_file, use_docker=False):
        """从备份文件恢复数据库
        
        Args:
            backup_file: 备份文件路径
            use_docker: 是否使用Docker方式恢复（当MySQL运行在Docker容器中时设置为True）
            
        Returns:
            恢复是否成功
        """
        try:
            # 检查备份文件是否存在
            if not os.path.exists(backup_file):
                logger.error(f"备份文件不存在: {backup_file}")
                return False
            
            if use_docker:
                # 使用Docker方式恢复（推荐）
                # 检查docker是否可用
                try:
                    subprocess.run(['docker', '--version'], capture_output=True, text=True, check=True)
                except Exception as e:
                    logger.error(f"找不到docker命令，请确保Docker已安装: {e}")
                    return False
                
                # 检查容器是否存在并运行
                try:
                    subprocess.run([
                        'docker', 'exec', 'student_management_mysql', 
                        'mysql', '-u', DB_CONFIG['user'], f"-p{DB_CONFIG['password']}", 
                        '-e', 'SELECT 1'
                    ], capture_output=True, text=True, check=True)
                except Exception as e:
                    logger.error(f"Docker容器不可用或数据库连接失败: {e}")
                    return False
                
                # 使用docker exec运行容器内的mysql命令导入数据
                cmd = [
                    'docker', 'exec', '-i', 'student_management_mysql',
                    'mysql',
                    '-u', DB_CONFIG['user'],
                    f"-p{DB_CONFIG['password']}",
                    DB_CONFIG['database'],
                    '--default-character-set=utf8mb4'
                ]
                
                # 执行命令并从文件读取输入
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        result = subprocess.run(cmd, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                except Exception as e:
                    logger.error(f"执行Docker恢复命令时发生错误: {e}")
                    return False
            else:
                # 传统方式恢复（需要主机安装MySQL工具）
                # 检查mysql命令是否可用
                try:
                    subprocess.run(['mysql', '--version'], capture_output=True, text=True, check=True)
                    use_cmd = False
                except (subprocess.SubprocessError, FileNotFoundError):
                    # 如果mysql不在PATH中，尝试使用cmd /c调用
                    try:
                        subprocess.run(['cmd', '/c', 'mysql', '--version'], capture_output=True, text=True, check=True)
                        use_cmd = True
                    except Exception as e:
                        logger.error(f"找不到mysql命令，请确保MySQL已安装并添加到系统PATH中或使用Docker方式恢复: {e}")
                        return False
                
                # 使用mysql命令恢复数据库
                if use_cmd:
                    cmd = [
                        'cmd', '/c',
                        f'mysql -h {DB_CONFIG["host"]} -u {DB_CONFIG["user"]} -p{DB_CONFIG["password"]} -P {DB_CONFIG["port"]} {DB_CONFIG["database"]} --default-character-set=utf8mb4 < "{backup_file}"'
                    ]
                else:
                    # 使用文件重定向方式导入数据
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        cmd = [
                            'mysql',
                            '-h', DB_CONFIG['host'],
                            '-u', DB_CONFIG['user'],
                            f"-p{DB_CONFIG['password']}",
                            '-P', str(DB_CONFIG['port']),
                            DB_CONFIG['database'],
                            '--default-character-set=utf8mb4'
                        ]
                        
                        result = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
                
                # 对于cmd方式，单独执行
                if use_cmd:
                    result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"数据库恢复成功，从文件: {backup_file}")
                # 恢复后重新连接数据库
                self.close()
                self.connect()
                return True
            else:
                logger.error(f"数据库恢复失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"数据库恢复过程中发生错误: {e}")
            return False
            
    def clear_cache(self):
        """清理系统缓存"""
        try:
            # 确保缓存目录存在
            if not os.path.exists(CACHE_DIR):
                os.makedirs(CACHE_DIR, exist_ok=True)
                logger.info("缓存目录不存在，已创建")
                return True
            
            # 遍历缓存目录并删除所有文件和子目录
            for item in os.listdir(CACHE_DIR):
                item_path = os.path.join(CACHE_DIR, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            
            logger.info("系统缓存清理成功")
            return True
        except Exception as e:
            logger.error(f"清理缓存过程中发生错误: {e}")
            return False
        
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