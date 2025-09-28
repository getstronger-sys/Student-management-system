#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""配置文件，存储数据库连接信息和网络配置"""

# 登录窗口配置
LOGIN_WINDOW_CONFIG = {
    'title': '学生管理系统登录',
    'x': 400,
    'y': 200,
    'width': 600,
    'height': 400,
    'min_width': 500,
    'min_height': 350
}

# 主窗口配置
MAIN_WINDOW_CONFIG = {
    'title': '学生管理系统',
    'x': 100,
    'y': 100,
    'width': 1000,
    'height': 800,
    'min_width': 800,
    'min_height': 600,
    'version': '1.0.0',
    'developers': '学生团队',
    'description': '一个用于学生成绩管理的系统'
}

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # 共享数据库用户
    'password': 'zhyzywxj1825907',  # 共享数据库密码
    'database': 'student_management',
    'port': 3306
}

# 网络配置
NETWORK_CONFIG = {
    'host': '0.0.0.0',
    'port': 8888
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'file': 'app.log'
}

# 用户角色定义
ROLES = {
    'ADMIN': 'admin',
    'TEACHER': 'teacher',
    'STUDENT': 'student'
}

# 用户角色显示名称映射
USER_ROLES = {
    'admin': '管理员',
    'teacher': '教师',
    'student': '学生'
}