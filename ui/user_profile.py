#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""用户个人信息对话框模块"""

import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGroupBox, QFormLayout, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from network.client import client
from models.user import User
from config.config import USER_ROLES

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('user_profile')


class UserProfileDialog(QDialog):
    """用户个人信息对话框类"""
    
    def __init__(self, user_info, parent=None):
        """初始化用户信息对话框"""
        super().__init__(parent)
        
        # 保存用户信息
        self.user_info = user_info.copy()  # 复制一份，避免直接修改原始数据
        self.user_updated = False
        
        # 设置窗口属性
        self.setWindowTitle("个人信息")
        self.setGeometry(400, 300, 500, 400)
        self.setMinimumSize(500, 400)
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # 添加标题
        title_label = QLabel("个人信息")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建用户信息组框
        user_info_group = QGroupBox("基本信息")
        user_info_layout = QFormLayout(user_info_group)
        user_info_layout.setVerticalSpacing(15)
        
        # 用户名字段
        self.username_edit = QLineEdit(self.user_info.get('username', ''))
        self.username_edit.setReadOnly(True)  # 用户名通常不允许修改
        user_info_layout.addRow("用户名:", self.username_edit)
        
        # 角色字段
        role_text = USER_ROLES.get(self.user_info.get('role', ''), '未知')
        self.role_edit = QLineEdit(role_text)
        self.role_edit.setReadOnly(True)  # 角色通常不允许修改
        user_info_layout.addRow("角色:", self.role_edit)
        
        # 真实名字段
        self.name_edit = QLineEdit(self.user_info.get('name', ''))
        user_info_layout.addRow("姓名:", self.name_edit)
        
        # 邮箱字段
        self.email_edit = QLineEdit(self.user_info.get('email', ''))
        user_info_layout.addRow("邮箱:", self.email_edit)
        
        # 手机号字段
        self.phone_edit = QLineEdit(self.user_info.get('phone', ''))
        user_info_layout.addRow("手机号:", self.phone_edit)
        
        # 添加用户信息组框到主布局
        main_layout.addWidget(user_info_group)
        
        # 创建修改密码组框
        password_group = QGroupBox("修改密码")
        password_layout = QFormLayout(password_group)
        password_layout.setVerticalSpacing(15)
        
        # 原密码字段
        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow("原密码:", self.old_password_edit)
        
        # 新密码字段
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow("新密码:", self.new_password_edit)
        
        # 确认新密码字段
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow("确认新密码:", self.confirm_password_edit)
        
        # 添加修改密码组框到主布局
        main_layout.addWidget(password_group)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.setMinimumHeight(35)
        self.save_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 5px; font-weight: bold; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.save_button.clicked.connect(self.handle_save)
        button_layout.addWidget(self.save_button)
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; border-radius: 5px; font-weight: bold; }"
            "QPushButton:hover { background-color: #da190b; }"
        )
        self.cancel_button.clicked.connect(self.handle_cancel)
        button_layout.addWidget(self.cancel_button)
        
        # 添加按钮布局到主布局
        main_layout.addLayout(button_layout)
    
    def handle_save(self):
        """处理保存事件"""
        # 收集表单数据
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        phone = self.phone_edit.text().strip()
        
        # 验证必填字段
        if not name:
            QMessageBox.warning(self, "输入错误", "姓名不能为空")
            self.name_edit.setFocus()
            return
        
        # 验证邮箱格式（简单验证）
        if email and '@' not in email:
            QMessageBox.warning(self, "输入错误", "邮箱格式不正确")
            self.email_edit.setFocus()
            return
        
        # 检查是否需要修改密码
        old_password = self.old_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # 密码相关验证
        if old_password or new_password or confirm_password:
            # 如果有一个密码字段填写了，其他也必须填写
            if not (old_password and new_password and confirm_password):
                QMessageBox.warning(self, "输入错误", "修改密码时，所有密码字段都必须填写")
                return
            
            # 验证新密码和确认密码是否一致
            if new_password != confirm_password:
                QMessageBox.warning(self, "输入错误", "新密码和确认密码不一致")
                self.confirm_password_edit.clear()
                self.confirm_password_edit.setFocus()
                return
            
            # 验证密码长度
            if len(new_password) < 6:
                QMessageBox.warning(self, "输入错误", "新密码长度不能少于6位")
                self.new_password_edit.clear()
                self.confirm_password_edit.clear()
                self.new_password_edit.setFocus()
                return
        
        try:
            # 更新用户信息
            user_data = {
                'name': name,
                'email': email,
                'phone': phone
            }
            
            # 如果需要修改密码，添加密码字段
            if old_password:
                user_data['old_password'] = old_password
                user_data['new_password'] = new_password
            
            # 调用User模型的更新方法
            success = User.update_user(self.user_info['id'], **user_data)
            
            if success:
                # 更新成功
                logger.info(f"用户 {self.user_info['username']} 的个人信息更新成功")
                
                # 更新本地用户信息
                self.user_info.update(user_data)
                # 如果修改了密码，清除密码字段
                if old_password:
                    self.old_password_edit.clear()
                    self.new_password_edit.clear()
                    self.confirm_password_edit.clear()
                
                # 设置更新标志
                self.user_updated = True
                
                # 显示成功消息
                QMessageBox.information(self, "更新成功", "个人信息更新成功")
                
                # 关闭对话框
                self.accept()
            else:
                # 更新失败
                logger.warning(f"用户 {self.user_info['username']} 的个人信息更新失败")
                QMessageBox.warning(self, "更新失败", "个人信息更新失败，请重试")
        except Exception as e:
            # 处理异常
            logger.error(f"更新个人信息时发生错误: {e}")
            QMessageBox.critical(self, "更新错误", f"更新个人信息时发生错误: {str(e)}")
    
    def handle_cancel(self):
        """处理取消事件"""
        # 关闭对话框
        self.reject()


# 测试代码
if __name__ == '__main__':
    # 这里只是为了测试
    test_user_info = {
        'id': 1,
        'username': 'testuser',
        'role': 'student',
        'name': '测试用户',
        'email': 'test@example.com',
        'phone': '13800138000'
    }
    
    app = QApplication(sys.argv)
    dialog = UserProfileDialog(test_user_info)
    dialog.exec_()
    
    # 输出更新后的用户信息
    if dialog.user_updated:
        print("用户信息已更新:", dialog.user_info)