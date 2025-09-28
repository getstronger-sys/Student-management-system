#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""用户注册对话框"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from network.client import client

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('register_dialog')


class RegisterDialog(QDialog):
    """注册对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("注册新用户")
        self.setMinimumWidth(400)
        self.register_success = False
        self.registered_username = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        username_label.setFixedWidth(80)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        
        # 姓名
        name_layout = QHBoxLayout()
        name_label = QLabel("姓名:")
        name_label.setFixedWidth(80)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入姓名(可与用户名相同)")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 密码
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        password_label.setFixedWidth(80)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("请输入密码")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)
        
        # 确认密码
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel("确认密码:")
        confirm_label.setFixedWidth(80)
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit.setPlaceholderText("请再次输入密码")
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_edit)
        layout.addLayout(confirm_layout)
        
        # 角色
        role_layout = QHBoxLayout()
        role_label = QLabel("角色:")
        role_label.setFixedWidth(80)
        self.role_combo = QComboBox()
        self.role_combo.addItem("学生", "student")
        self.role_combo.addItem("教师", "teacher")
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_combo)
        layout.addLayout(role_layout)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        self.submit_button = QPushButton("注册")
        self.submit_button.clicked.connect(self.handle_submit)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.submit_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)
    
    def handle_submit(self):
        username = self.username_edit.text().strip()
        name = self.name_edit.text().strip() or username
        password = self.password_edit.text().strip()
        confirm = self.confirm_edit.text().strip()
        role = self.role_combo.currentData()
        
        # 校验
        if not username:
            QMessageBox.warning(self, "输入错误", "请输入用户名")
            return
        if not password:
            QMessageBox.warning(self, "输入错误", "请输入密码")
            return
        if password != confirm:
            QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")
            return
        if role not in ['student', 'teacher']:
            QMessageBox.warning(self, "输入错误", "角色无效")
            return
        
        # 确保已连接服务器
        # 如果未连接，这里尝试连接一次
        if not getattr(client, 'connected', False):
            if not client.connect():
                QMessageBox.critical(self, "连接失败", "无法连接到服务器，请稍后再试")
                return
        
        # 调用后端注册
        try:
            response = client.register(username, password, role, name)
            if response.get('success'):
                QMessageBox.information(self, "注册成功", "注册成功，请使用新账号登录")
                self.register_success = True
                self.registered_username = username
                self.accept()
            else:
                QMessageBox.warning(self, "注册失败", response.get('message', '注册失败'))
        except Exception as e:
            logger.error(f"注册请求失败: {e}")
            QMessageBox.critical(self, "错误", f"注册失败: {str(e)}") 