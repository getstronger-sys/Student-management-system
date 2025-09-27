#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""管理员仪表盘模块"""

import sys
import logging
import matplotlib
matplotlib.use('Qt5Agg')  # 使用Qt5后端
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QTabWidget, QFrame, QMessageBox, QComboBox,
    QPushButton, QLineEdit, QFormLayout, QGroupBox, QDialog, 
    QDialogButtonBox, QInputDialog, QCheckBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from network.client import client
from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.courses import Course
from models.scores import Score
import utils.data_visualization

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('admin_dashboard')


class AdminDashboard(QWidget):
    """管理员仪表盘类"""
    
    def __init__(self, user_info):
        """初始化管理员仪表盘"""
        super().__init__()
        
        # 保存用户信息
        self.user_info = user_info
        
        # 初始化UI
        self.init_ui()
        
        # 加载数据
        self.load_users()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 创建个人信息标签页
        self.create_profile_tab()
        
        # 创建用户管理标签页
        self.create_users_tab()
        
        # 创建学生管理标签页
        self.create_students_tab()
        
        # 创建教师管理标签页
        self.create_teachers_tab()
        
        # 创建课程管理标签页
        self.create_courses_tab()
        
        # 创建系统设置标签页
        self.create_settings_tab()
        
        # 添加标签页到标签部件
        self.tab_widget.addTab(self.profile_widget, "个人信息")
        self.tab_widget.addTab(self.users_widget, "用户管理")
        self.tab_widget.addTab(self.students_widget, "学生管理")
        self.tab_widget.addTab(self.teachers_widget, "教师管理")
        self.tab_widget.addTab(self.courses_widget, "课程管理")
        self.tab_widget.addTab(self.settings_widget, "系统设置")
        
        # 添加标签部件到主布局
        main_layout.addWidget(self.tab_widget)
    
    def create_profile_tab(self):
        """创建个人信息标签页"""
        self.profile_widget = QWidget()
        profile_layout = QVBoxLayout(self.profile_widget)
        
        # 创建个人信息组框
        profile_group = QFrame()
        profile_group.setFrameShape(QFrame.StyledPanel)
        profile_group.setStyleSheet("QFrame { background-color: #f0f0f0; border-radius: 10px; padding: 10px; }")
        profile_form_layout = QVBoxLayout(profile_group)
        
        # 用户ID
        self.user_id_label = QLabel("用户ID: ")
        profile_form_layout.addWidget(self.user_id_label)
        
        # 用户名
        self.username_label = QLabel("用户名: ")
        profile_form_layout.addWidget(self.username_label)
        
        # 姓名
        self.name_label = QLabel("姓名: ")
        profile_form_layout.addWidget(self.name_label)
        
        # 角色
        self.role_label = QLabel("角色: ")
        profile_form_layout.addWidget(self.role_label)
        
        # 更新界面显示
        self.user_id_label.setText(f"用户ID: {self.user_info.get('id', '')}")
        self.username_label.setText(f"用户名: {self.user_info.get('username', '')}")
        self.name_label.setText(f"姓名: {self.user_info.get('name', '')}")
        self.role_label.setText(f"角色: 管理员")
        
        # 添加个人信息组框到布局
        profile_layout.addWidget(profile_group)
    
    def create_users_tab(self):
        """创建用户管理标签页"""
        self.users_widget = QWidget()
        users_layout = QVBoxLayout(self.users_widget)
        
        # 创建操作按钮布局
        actions_layout = QHBoxLayout()
        
        # 添加用户按钮
        self.add_user_button = QPushButton("添加用户")
        self.add_user_button.clicked.connect(self.add_user)
        actions_layout.addWidget(self.add_user_button)
        
        # 刷新按钮
        self.refresh_users_button = QPushButton("刷新")
        self.refresh_users_button.clicked.connect(self.load_users)
        actions_layout.addWidget(self.refresh_users_button)
        
        # 搜索框
        self.users_search_edit = QLineEdit()
        self.users_search_edit.setPlaceholderText("搜索用户名")
        self.users_search_edit.returnPressed.connect(self.search_users)
        actions_layout.addWidget(self.users_search_edit)
        
        # 搜索按钮
        self.search_users_button = QPushButton("搜索")
        self.search_users_button.clicked.connect(self.search_users)
        actions_layout.addWidget(self.search_users_button)
        
        # 添加操作按钮布局到主布局
        users_layout.addLayout(actions_layout)
        
        # 创建用户表格
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["用户ID", "用户名", "姓名", "角色", "邮箱", "操作"])
        
        # 设置表格样式
        self.users_table.horizontalHeader().setStretchLastSection(True)
        
        # 添加用户表格到布局
        users_layout.addWidget(self.users_table)
    
    def create_students_tab(self):
        """创建学生管理标签页"""
        self.students_widget = QWidget()
        students_layout = QVBoxLayout(self.students_widget)
        
        # 创建操作按钮布局
        actions_layout = QHBoxLayout()
        
        # 添加学生按钮
        self.add_student_button = QPushButton("添加学生")
        self.add_student_button.clicked.connect(self.add_student)
        actions_layout.addWidget(self.add_student_button)
        
        # 刷新按钮
        self.refresh_students_button = QPushButton("刷新")
        actions_layout.addWidget(self.refresh_students_button)
        
        # 搜索框
        self.students_search_edit = QLineEdit()
        self.students_search_edit.setPlaceholderText("搜索学生姓名或学号")
        actions_layout.addWidget(self.students_search_edit)
        
        # 搜索按钮
        self.search_students_button = QPushButton("搜索")
        actions_layout.addWidget(self.search_students_button)
        
        # 添加操作按钮布局到主布局
        students_layout.addLayout(actions_layout)
        
        # 创建学生表格
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(8)
        self.students_table.setHorizontalHeaderLabels(["学生ID", "学号", "姓名", "性别", "年龄", "专业", "班级", "操作"])
        
        # 设置表格样式
        self.students_table.horizontalHeader().setStretchLastSection(True)
        
        # 添加学生表格到布局
        students_layout.addWidget(self.students_table)
    
    def create_teachers_tab(self):
        """创建教师管理标签页"""
        self.teachers_widget = QWidget()
        teachers_layout = QVBoxLayout(self.teachers_widget)
        
        # 创建操作按钮布局
        actions_layout = QHBoxLayout()
        
        # 添加教师按钮
        self.add_teacher_button = QPushButton("添加教师")
        self.add_teacher_button.clicked.connect(self.add_teacher)
        actions_layout.addWidget(self.add_teacher_button)
        
        # 刷新按钮
        self.refresh_teachers_button = QPushButton("刷新")
        actions_layout.addWidget(self.refresh_teachers_button)
        
        # 搜索框
        self.teachers_search_edit = QLineEdit()
        self.teachers_search_edit.setPlaceholderText("搜索教师姓名")
        actions_layout.addWidget(self.teachers_search_edit)
        
        # 搜索按钮
        self.search_teachers_button = QPushButton("搜索")
        actions_layout.addWidget(self.search_teachers_button)
        
        # 添加操作按钮布局到主布局
        teachers_layout.addLayout(actions_layout)
        
        # 创建教师表格
        self.teachers_table = QTableWidget()
        self.teachers_table.setColumnCount(7)
        self.teachers_table.setHorizontalHeaderLabels(["教师ID", "姓名", "性别", "年龄", "部门", "职称", "操作"])
        
        # 设置表格样式
        self.teachers_table.horizontalHeader().setStretchLastSection(True)
        
        # 添加教师表格到布局
        teachers_layout.addWidget(self.teachers_table)
    
    def create_courses_tab(self):
        """创建课程管理标签页"""
        self.courses_widget = QWidget()
        courses_layout = QVBoxLayout(self.courses_widget)
        
        # 创建操作按钮布局
        actions_layout = QHBoxLayout()
        
        # 添加课程按钮
        self.add_course_button = QPushButton("添加课程")
        self.add_course_button.clicked.connect(self.add_course)
        actions_layout.addWidget(self.add_course_button)
        
        # 刷新按钮
        self.refresh_courses_button = QPushButton("刷新")
        actions_layout.addWidget(self.refresh_courses_button)
        
        # 搜索框
        self.courses_search_edit = QLineEdit()
        self.courses_search_edit.setPlaceholderText("搜索课程名称或代码")
        actions_layout.addWidget(self.courses_search_edit)
        
        # 搜索按钮
        self.search_courses_button = QPushButton("搜索")
        actions_layout.addWidget(self.search_courses_button)
        
        # 添加操作按钮布局到主布局
        courses_layout.addLayout(actions_layout)
        
        # 创建课程表格
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(8)
        self.courses_table.setHorizontalHeaderLabels(["课程ID", "课程代码", "课程名称", "学分", "教师", "学期", "上课时间", "操作"])
        
        # 设置表格样式
        self.courses_table.horizontalHeader().setStretchLastSection(True)
        
        # 添加课程表格到布局
        courses_layout.addWidget(self.courses_table)
    
    def create_settings_tab(self):
        """创建系统设置标签页"""
        self.settings_widget = QWidget()
        settings_layout = QVBoxLayout(self.settings_widget)
        
        # 创建系统信息组框
        system_info_group = QGroupBox("系统信息")
        system_info_layout = QFormLayout(system_info_group)
        
        # 系统版本
        version_label = QLabel("系统版本: 1.0.0")
        system_info_layout.addRow(version_label)
        
        # 数据库状态
        db_status_label = QLabel("数据库状态: 已连接")
        system_info_layout.addRow(db_status_label)
        
        # 服务器状态
        server_status_label = QLabel("服务器状态: 运行中")
        system_info_layout.addRow(server_status_label)
        
        # 添加系统信息组框到布局
        settings_layout.addWidget(system_info_group)
        
        # 创建系统维护组框
        maintenance_group = QGroupBox("系统维护")
        maintenance_layout = QVBoxLayout(maintenance_group)
        
        # 备份数据库按钮
        backup_db_button = QPushButton("备份数据库")
        backup_db_button.clicked.connect(self.backup_database)
        maintenance_layout.addWidget(backup_db_button)
        
        # 恢复数据库按钮
        restore_db_button = QPushButton("恢复数据库")
        restore_db_button.clicked.connect(self.restore_database)
        maintenance_layout.addWidget(restore_db_button)
        
        # 清理缓存按钮
        clear_cache_button = QPushButton("清理缓存")
        clear_cache_button.clicked.connect(self.clear_cache)
        maintenance_layout.addWidget(clear_cache_button)
        
        # 添加系统维护组框到布局
        settings_layout.addWidget(maintenance_group)
        
        # 添加拉伸因子
        settings_layout.addStretch()
    
    def load_users(self):
        """加载用户数据"""
        try:
            # 获取所有用户
            response = client.get_all_users()
            
            if response.get('success'):
                users = response.get('users', [])
                
                # 清空表格
                self.users_table.setRowCount(0)
                
                # 填充表格
                for user in users:
                    row_position = self.users_table.rowCount()
                    self.users_table.insertRow(row_position)
                    
                    # 设置表格数据
                    self.users_table.setItem(row_position, 0, QTableWidgetItem(str(user.get('id', ''))))
                    self.users_table.setItem(row_position, 1, QTableWidgetItem(user.get('username', '')))
                    self.users_table.setItem(row_position, 2, QTableWidgetItem(user.get('name', '')))
                    
                    # 角色显示
                    role_text = '管理员' if user.get('role') == 'admin' else '教师' if user.get('role') == 'teacher' else '学生'
                    self.users_table.setItem(row_position, 3, QTableWidgetItem(role_text))
                    
                    self.users_table.setItem(row_position, 4, QTableWidgetItem(user.get('email', '')))
                    
                    # 创建操作按钮
                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(0, 0, 0, 0)
                    
                    # 编辑按钮
                    edit_button = QPushButton("编辑")
                    edit_button.setMaximumWidth(60)
                    edit_button.clicked.connect(lambda checked, user_id=user.get('id'): self.edit_user(user_id))
                    action_layout.addWidget(edit_button)
                    
                    # 删除按钮
                    delete_button = QPushButton("删除")
                    delete_button.setMaximumWidth(60)
                    delete_button.setStyleSheet("color: red;")
                    delete_button.clicked.connect(lambda checked, user_id=user.get('id'): self.delete_user(user_id))
                    action_layout.addWidget(delete_button)
                    
                    self.users_table.setCellWidget(row_position, 5, action_widget)
                
                # 调整表格列宽
                self.users_table.resizeColumnsToContents()
        except Exception as e:
            logger.error(f"加载用户数据失败: {e}")
            QMessageBox.warning(self, "加载失败", f"加载用户数据失败: {str(e)}")
    
    def add_user(self):
        """添加用户"""
        # 创建添加用户对话框
        dialog = AddUserDialog(self)
        if dialog.exec_():
            # 刷新用户列表
            self.load_users()
    
    def edit_user(self, user_id):
        """编辑用户"""
        # 打开编辑用户对话框
        dialog = EditUserDialog(user_id, self)
        if dialog.exec_() == QDialog.Accepted:
            # 如果用户确认编辑，重新加载用户列表
            self.load_users()
    
    def delete_user(self, user_id):
        """删除用户"""
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除ID为 {user_id} 的用户吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 发送删除请求
                response = client.delete_user(user_id)
                
                if response.get('success'):
                    # 删除成功，刷新用户列表
                    logger.info(f"用户ID {user_id} 已删除")
                    self.load_users()
                    QMessageBox.information(self, "删除成功", "用户删除成功")
                else:
                    # 删除失败
                    logger.warning(f"删除用户ID {user_id} 失败")
                    QMessageBox.warning(self, "删除失败", "用户删除失败")
            except Exception as e:
                logger.error(f"删除用户时发生错误: {e}")
                QMessageBox.critical(self, "删除错误", f"删除用户时发生错误: {str(e)}")
    
    def search_users(self):
        """搜索用户"""
        # 这里简化处理，实际可能需要调用特定的API搜索用户
        keyword = self.users_search_edit.text().strip()
        if not keyword:
            self.load_users()
            return
        
        QMessageBox.information(self, "功能提示", f"用户搜索功能待实现，关键词: {keyword}")
    
    def add_student(self):
        """添加学生"""
        QMessageBox.information(self, "功能提示", "添加学生功能待实现")
    
    def add_teacher(self):
        """添加教师"""
        QMessageBox.information(self, "功能提示", "添加教师功能待实现")
    
    def add_course(self):
        """添加课程"""
        QMessageBox.information(self, "功能提示", "添加课程功能待实现")
    
    def backup_database(self):
        """备份数据库"""
        QMessageBox.information(self, "功能提示", "备份数据库功能待实现")
    
    def restore_database(self):
        """恢复数据库"""
        QMessageBox.information(self, "功能提示", "恢复数据库功能待实现")
    
    def clear_cache(self):
        """清理缓存"""
        QMessageBox.information(self, "功能提示", "清理缓存功能待实现")
    
    def switch_page(self, page_name):
        """切换页面"""
        # 根据页面名称切换标签页
        if page_name == 'profile':
            self.tab_widget.setCurrentWidget(self.profile_widget)
        elif page_name == 'users':
            self.tab_widget.setCurrentWidget(self.users_widget)
        elif page_name == 'students':
            self.tab_widget.setCurrentWidget(self.students_widget)
        elif page_name == 'teachers':
            self.tab_widget.setCurrentWidget(self.teachers_widget)
        elif page_name == 'courses':
            self.tab_widget.setCurrentWidget(self.courses_widget)
        elif page_name == 'settings':
            self.tab_widget.setCurrentWidget(self.settings_widget)
    
    def refresh(self):
        """刷新数据"""
        # 重新加载数据
        self.load_users()
        # 如果有其他数据也需要刷新，可以在这里添加


class EditUserDialog(QDialog):
    """编辑用户对话框类"""
    
    def __init__(self, user_id, parent=None):
        """初始化编辑用户对话框"""
        super().__init__(parent)
        self.setWindowTitle("编辑用户")
        self.setGeometry(400, 300, 400, 300)
        self.user_id = user_id
        self.user_info = None
        
        # 初始化UI
        self.init_ui()
        # 加载用户信息
        self.load_user_info()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # 用户名显示（不可编辑）
        self.username_label = QLabel()
        form_layout.addRow("用户名:", self.username_label)
        
        # 新密码输入框
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("留空表示不修改密码")
        form_layout.addRow("新密码:", self.password_edit)
        
        # 确认密码输入框
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText("留空表示不修改密码")
        form_layout.addRow("确认密码:", self.confirm_password_edit)
        
        # 姓名输入框
        self.name_edit = QLineEdit()
        form_layout.addRow("姓名:", self.name_edit)
        
        # 角色选择
        self.role_combo = QComboBox()
        self.role_combo.addItems(["学生", "教师", "管理员"])
        form_layout.addRow("角色:", self.role_combo)
        
        # 邮箱输入框
        self.email_edit = QLineEdit()
        form_layout.addRow("邮箱:", self.email_edit)
        
        # 添加表单布局到主布局
        main_layout.addLayout(form_layout)
        
        # 创建按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 添加按钮到主布局
        main_layout.addWidget(button_box)
    
    def load_user_info(self):
        """加载用户信息"""
        try:
            # 获取用户信息
            response = client.send_request('get_user_by_id', {'user_id': self.user_id})
            
            if response.get('success'):
                self.user_info = response.get('user')
                
                # 填充表单
                if self.user_info:
                    self.username_label.setText(self.user_info.get('username', ''))
                    self.name_edit.setText(self.user_info.get('name', ''))
                    
                    # 设置角色
                    role = self.user_info.get('role', 'student')
                    role_index = 0  # 默认学生
                    if role == 'teacher':
                        role_index = 1
                    elif role == 'admin':
                        role_index = 2
                    self.role_combo.setCurrentIndex(role_index)
                    
                    self.email_edit.setText(self.user_info.get('email', ''))
            else:
                QMessageBox.warning(self, "加载失败", "加载用户信息失败")
        except Exception as e:
            QMessageBox.critical(self, "加载错误", f"加载用户信息时发生错误: {str(e)}")
    
    def accept(self):
        """处理确认事件"""
        # 收集表单数据
        name = self.name_edit.text().strip()
        password = self.password_edit.text().strip()
        confirm_password = self.confirm_password_edit.text().strip()
        role_index = self.role_combo.currentIndex()
        role = ['student', 'teacher', 'admin'][role_index]
        email = self.email_edit.text().strip()
        
        # 验证输入
        if not name:
            QMessageBox.warning(self, "输入错误", "姓名不能为空")
            self.name_edit.setFocus()
            return
        
        if password or confirm_password:
            if password != confirm_password:
                QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")
                self.confirm_password_edit.clear()
                self.confirm_password_edit.setFocus()
                return
            
            if len(password) < 6:
                QMessageBox.warning(self, "输入错误", "密码长度不能少于6位")
                self.password_edit.clear()
                self.confirm_password_edit.clear()
                self.password_edit.setFocus()
                return
        
        if email and '@' not in email:
            QMessageBox.warning(self, "输入错误", "邮箱格式不正确")
            self.email_edit.setFocus()
            return
        
        try:
            # 构建更新参数
            update_params = {
                'name': name,
                'role': role,
                'email': email
            }
            
            # 如果输入了密码，则更新密码
            if password:
                update_params['password'] = password
            
            # 发送更新请求
            response = client.update_user(self.user_id, **update_params)
            
            if response.get('success'):
                # 更新成功
                QMessageBox.information(self, "更新成功", "用户信息更新成功")
                super().accept()
            else:
                # 更新失败
                error_msg = response.get('message', '用户信息更新失败')
                QMessageBox.warning(self, "更新失败", error_msg)
        except Exception as e:
            # 处理异常
            QMessageBox.critical(self, "更新错误", f"更新用户信息时发生错误: {str(e)}")

class AddUserDialog(QDialog):
    """添加用户对话框类"""
    
    def __init__(self, parent=None):
        """初始化添加用户对话框"""
        super().__init__(parent)
        self.setWindowTitle("添加用户")
        self.setGeometry(400, 300, 400, 300)
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # 用户名输入框
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        form_layout.addRow("用户名:", self.username_edit)
        
        # 密码输入框
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("请输入密码")
        form_layout.addRow("密码:", self.password_edit)
        
        # 确认密码输入框
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText("请确认密码")
        form_layout.addRow("确认密码:", self.confirm_password_edit)
        
        # 姓名输入框
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入姓名")
        form_layout.addRow("姓名:", self.name_edit)
        
        # 角色选择
        self.role_combo = QComboBox()
        self.role_combo.addItems(["学生", "教师", "管理员"])
        form_layout.addRow("角色:", self.role_combo)
        
        # 邮箱输入框
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("请输入邮箱")
        form_layout.addRow("邮箱:", self.email_edit)
        
        # 添加表单布局到主布局
        main_layout.addLayout(form_layout)
        
        # 创建按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 添加按钮到主布局
        main_layout.addWidget(button_box)
    
    def accept(self):
        """处理确认事件"""
        # 收集表单数据
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        confirm_password = self.confirm_password_edit.text().strip()
        name = self.name_edit.text().strip()
        role_index = self.role_combo.currentIndex()
        role = ['student', 'teacher', 'admin'][role_index]
        email = self.email_edit.text().strip()
        
        # 验证输入
        if not username:
            QMessageBox.warning(self, "输入错误", "用户名不能为空")
            self.username_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "输入错误", "密码不能为空")
            self.password_edit.setFocus()
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")
            self.confirm_password_edit.clear()
            self.confirm_password_edit.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "输入错误", "密码长度不能少于6位")
            self.password_edit.clear()
            self.confirm_password_edit.clear()
            self.password_edit.setFocus()
            return
        
        if not name:
            QMessageBox.warning(self, "输入错误", "姓名不能为空")
            self.name_edit.setFocus()
            return
        
        if email and '@' not in email:
            QMessageBox.warning(self, "输入错误", "邮箱格式不正确")
            self.email_edit.setFocus()
            return
        
        try:
            # 调用User模型的添加方法
            success = User.register(username, password, name, role, email)
            
            if success:
                # 添加成功
                QMessageBox.information(self, "添加成功", "用户添加成功")
                super().accept()
            else:
                # 添加失败
                QMessageBox.warning(self, "添加失败", "用户添加失败，请重试")
        except Exception as e:
            # 处理异常
            QMessageBox.critical(self, "添加错误", f"添加用户时发生错误: {str(e)}")


# 测试代码
if __name__ == '__main__':
    # 这里只是为了测试
    test_user_info = {
        'id': 3,
        'username': 'admin',
        'role': 'admin',
        'name': '管理员'
    }
    
    app = QApplication(sys.argv)
    dashboard = AdminDashboard(test_user_info)
    dashboard.show()
    sys.exit(app.exec_())