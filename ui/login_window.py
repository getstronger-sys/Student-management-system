#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""登录窗口模块"""

import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon
from network.client import client
from config.config import LOGIN_WINDOW_CONFIG
from ui.register_dialog import RegisterDialog

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('login_window')


class LoginWindow(QMainWindow):
    """登录窗口类"""
    # 定义登录成功的信号
    login_success = pyqtSignal(dict)
    
    def __init__(self):
        """初始化登录窗口"""
        super().__init__()
        self.setWindowTitle(LOGIN_WINDOW_CONFIG['title'])
        self.setGeometry(
            LOGIN_WINDOW_CONFIG['x'],
            LOGIN_WINDOW_CONFIG['y'],
            LOGIN_WINDOW_CONFIG['width'],
            LOGIN_WINDOW_CONFIG['height']
        )
        self.setMinimumSize(
            LOGIN_WINDOW_CONFIG['min_width'],
            LOGIN_WINDOW_CONFIG['min_height']
        )
        
        # 连接状态
        self.connected = False
        
        # 登录成功标志
        self.login_success_triggered = False
        
        # 初始化UI
        self.init_ui()
        
        # 尝试连接服务器
        self.connect_to_server()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)
        
        # 添加标题
        title_label = QLabel(LOGIN_WINDOW_CONFIG['title'])
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建表单框架
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setStyleSheet("QFrame { background-color: #f0f0f0; border-radius: 10px; }")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(30, 30, 30, 30)
        
        # 用户名输入框
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        username_label.setFixedWidth(80)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        self.username_edit.setMinimumHeight(35)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        form_layout.addLayout(username_layout)
        
        # 密码输入框
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        password_label.setFixedWidth(80)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(35)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        form_layout.addLayout(password_layout)
        
        # 服务器状态标签
        self.status_label = QLabel("正在连接服务器...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: blue;")
        form_layout.addWidget(self.status_label)
        
        # 登录按钮
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("登录")
        self.login_button.setMinimumHeight(40)
        self.login_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 5px; font-weight: bold; }"
            "QPushButton:hover { background-color: #45a049; }"
            "QPushButton:disabled { background-color: #cccccc; color: #666666; }"
        )
        self.login_button.setEnabled(False)
        self.login_button.clicked.connect(self.handle_login)
        button_layout.addWidget(self.login_button)
        
        # 新增：注册按钮
        self.register_button = QPushButton("注册")
        self.register_button.setMinimumHeight(40)
        self.register_button.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; border-radius: 5px; font-weight: bold; }"
            "QPushButton:hover { background-color: #1976D2; }"
            "QPushButton:disabled { background-color: #cccccc; color: #666666; }"
        )
        self.register_button.clicked.connect(self.open_register_dialog)
        # 只有连接成功时允许注册，以便调用后端
        self.register_button.setEnabled(False)
        button_layout.addWidget(self.register_button)
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; border-radius: 5px; font-weight: bold; }"
            "QPushButton:hover { background-color: #da190b; }"
        )
        self.cancel_button.clicked.connect(self.handle_cancel)
        button_layout.addWidget(self.cancel_button)
        
        form_layout.addLayout(button_layout)
        main_layout.addWidget(form_frame)
        
        # 添加键盘事件
        self.username_edit.returnPressed.connect(self.password_edit.setFocus)
        self.password_edit.returnPressed.connect(self.handle_login)
    
    def connect_to_server(self):
        """连接到服务器"""
        try:
            # 尝试连接服务器
            self.connected = client.connect()
            
            if self.connected:
                self.status_label.setText("服务器连接成功")
                self.status_label.setStyleSheet("color: green;")
                self.login_button.setEnabled(True)
                self.register_button.setEnabled(True)
                self.username_edit.setFocus()
                logger.info("服务器连接成功")
            else:
                self.status_label.setText("服务器连接失败")
                self.status_label.setStyleSheet("color: red;")
                self.login_button.setEnabled(False)
                logger.error("服务器连接失败")
                
                # 显示错误消息
                QMessageBox.critical(
                    self,
                    "连接失败",
                    "无法连接到服务器，请检查网络设置或稍后再试。",
                    QMessageBox.Ok
                )
        except Exception as e:
            self.status_label.setText(f"连接错误: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
            self.login_button.setEnabled(False)
            logger.error(f"服务器连接异常: {e}")
    
    # 定义登录线程类，用于在后台处理登录请求，避免阻塞GUI主线程
    class LoginThread(QThread):
        # 定义信号，用于将登录结果传递回主线程
        login_result = pyqtSignal(dict)
        
        def __init__(self, username, password):
            super().__init__()
            self.username = username
            self.password = password
        
        def run(self):
            try:
                # 在单独的线程中发送登录请求
                response = client.login(self.username, self.password)
                self.login_result.emit(response)
            except Exception as e:
                # 处理异常
                self.login_result.emit({'success': False, 'message': f'登录过程中发生错误: {str(e)}'})
    
    def handle_login(self):
        """处理登录事件"""
        # 获取用户名和密码
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        # 验证输入
        if not username:
            QMessageBox.warning(self, "输入错误", "请输入用户名")
            self.username_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "输入错误", "请输入密码")
            self.password_edit.setFocus()
            return
        
        # 检查连接状态
        if not self.connected:
            QMessageBox.warning(self, "连接失败", "未连接到服务器")
            self.connect_to_server()
            return
        
        # 禁用登录按钮，防止重复点击
        self.login_button.setEnabled(False)
        self.status_label.setText("正在登录...")
        
        logger.info(f"用户 {username} 尝试登录")
        
        # 创建并启动登录线程
        self.login_thread = self.LoginThread(username, password)
        self.login_thread.login_result.connect(self.on_login_result)
        self.login_thread.start()
    
    def on_login_result(self, response):
        """处理登录结果"""
        try:
            if response.get('success'):
                # 登录成功
                username = self.username_edit.text().strip()
                user_info = response.get('user')
                logger.info(f"用户 {username} 登录成功")
                
                # 设置登录成功标志
                self.login_success_triggered = True
                
                # 发送登录成功信号
                self.login_success.emit(user_info)
                
                # 关闭登录窗口
                self.close()
            else:
                # 登录失败
                username = self.username_edit.text().strip()
                error_message = response.get('message', '登录失败')
                logger.warning(f"用户 {username} 登录失败: {error_message}")
                QMessageBox.warning(self, "登录失败", error_message)
                
                # 清空密码输入框
                self.password_edit.clear()
                self.password_edit.setFocus()
        except Exception as e:
            # 处理异常
            logger.error(f"处理登录结果时发生错误: {e}")
            QMessageBox.critical(self, "登录错误", f"处理登录结果时发生错误: {str(e)}")
        finally:
            # 恢复登录按钮状态
            self.login_button.setEnabled(True)
            self.status_label.setText("服务器连接成功")
            self.status_label.setStyleSheet("color: green;")
            self.register_button.setEnabled(self.connected)
        
    def open_register_dialog(self):
        """打开注册对话框"""
        dialog = RegisterDialog(self)
        dialog.exec_()
        if getattr(dialog, 'register_success', False):
            # 回填用户名，便于用户直接登录
            self.username_edit.setText(dialog.registered_username or '')
            self.password_edit.setFocus()
    
    def handle_cancel(self):
        """处理取消事件"""
        # 断开与服务器的连接 - 只有在没有触发登录成功信号时才断开连接
        if not self.login_success_triggered:
            client.disconnect()
        
        # 关闭窗口
        self.close()
    
    def closeEvent(self, event):
        """重写关闭事件"""
        # 断开与服务器的连接 - 只有在没有触发登录成功信号时才断开连接
        # 登录成功后，主窗口会接管与服务器的连接
        if hasattr(self, 'login_success_triggered') and not self.login_success_triggered:
            if self.connected:
                client.disconnect()
        
        # 接受关闭事件
        event.accept()


# 测试代码
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())