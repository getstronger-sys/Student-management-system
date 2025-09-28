#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""主窗口模块，根据用户角色显示不同功能界面"""

import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QMessageBox, QMenuBar, QMenu,
    QAction, QSplitter, QListWidget, QListWidgetItem, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from network.client import client
from config.config import MAIN_WINDOW_CONFIG, USER_ROLES
from ui.student_dashboard import StudentDashboard
from ui.teacher_dashboard import TeacherDashboard
from ui.admin_dashboard import AdminDashboard
from ui.user_profile import UserProfileDialog
import utils.data_visualization

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main_window')


class MainWindow(QMainWindow):
    """主窗口类，根据用户角色显示不同功能界面"""
    
    def __init__(self, user_info):
        """初始化主窗口"""
        super().__init__()
        
        # 保存用户信息
        self.user_info = user_info
        self.role = user_info['role']
        self.username = user_info['username']
        
        # 标记是否在执行注销流程，用于关闭事件中绕过二次确认
        self.is_logging_out = False
        
        # 设置窗口属性
        self.setWindowTitle(f"{MAIN_WINDOW_CONFIG['title']} - {USER_ROLES[self.role]}")
        self.setGeometry(
            MAIN_WINDOW_CONFIG['x'],
            MAIN_WINDOW_CONFIG['y'],
            MAIN_WINDOW_CONFIG['width'],
            MAIN_WINDOW_CONFIG['height']
        )
        self.setMinimumSize(
            MAIN_WINDOW_CONFIG['min_width'],
            MAIN_WINDOW_CONFIG['min_height']
        )
        
        # 初始化UI
        self.init_ui()
        
        # 初始化状态栏
        self.init_status_bar()
        
        # 连接信号和槽
        self.connect_signals_slots()
        
        # 更新状态栏信息
        self.update_status_bar()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建左侧导航栏
        self.create_navigation_bar(main_layout)
        
        # 创建右侧内容区域
        self.create_content_area(main_layout)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
    
    def create_navigation_bar(self, main_layout):
        """创建左侧导航栏"""
        self.nav_widget = QListWidget()
        self.nav_widget.setMaximumWidth(200)
        self.nav_widget.setStyleSheet("QListWidget { border-right: 1px solid #ccc; }")
        
        # 根据角色设置导航项
        if self.role == 'student':
            self.add_nav_item("个人信息", "profile")
            self.add_nav_item("我的成绩", "scores")
            self.add_nav_item("我的课程", "courses")
            self.add_nav_item("成绩分析", "analysis")
        elif self.role == 'teacher':
            self.add_nav_item("个人信息", "profile")
            self.add_nav_item("我的课程", "courses")
            self.add_nav_item("成绩管理", "scores")
            self.add_nav_item("学生管理", "students")
            self.add_nav_item("数据分析", "analysis")
        elif self.role == 'admin':
            self.add_nav_item("个人信息", "profile")
            self.add_nav_item("用户管理", "users")
            self.add_nav_item("学生管理", "students")
            self.add_nav_item("教师管理", "teachers")
            self.add_nav_item("课程管理", "courses")
            self.add_nav_item("系统设置", "settings")
        
        main_layout.addWidget(self.nav_widget)
    
    def add_nav_item(self, text, data):
        """添加导航项"""
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, data)
        item.setTextAlignment(Qt.AlignCenter)
        item.setSizeHint(QSize(0, 50))  # 设置项的高度
        self.nav_widget.addItem(item)
    
    def create_content_area(self, main_layout):
        """创建右侧内容区域"""
        # 创建堆叠窗口，用于切换不同功能界面
        self.stacked_widget = QStackedWidget()
        
        # 根据角色创建不同的仪表盘
        if self.role == 'student':
            self.dashboard = StudentDashboard(self.user_info)
        elif self.role == 'teacher':
            self.dashboard = TeacherDashboard(self.user_info)
        elif self.role == 'admin':
            self.dashboard = AdminDashboard(self.user_info)
        
        # 添加仪表盘到堆叠窗口
        self.stacked_widget.addWidget(self.dashboard)
        
        main_layout.addWidget(self.stacked_widget, 1)  # 1表示拉伸因子
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        # 新建
        new_action = QAction('新建', self)
        new_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_action)
        
        # 打开
        open_action = QAction('打开', self)
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)
        
        # 保存
        save_action = QAction('保存', self)
        save_action.setShortcut('Ctrl+S')
        file_menu.addAction(save_action)
        
        # 分隔线
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        
        # 复制
        copy_action = QAction('复制', self)
        copy_action.setShortcut('Ctrl+C')
        edit_menu.addAction(copy_action)
        
        # 粘贴
        paste_action = QAction('粘贴', self)
        paste_action.setShortcut('Ctrl+V')
        edit_menu.addAction(paste_action)
        
        # 查看菜单
        view_menu = menubar.addMenu('查看')
        
        # 刷新
        refresh_action = QAction('刷新', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_content)
        view_menu.addAction(refresh_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        # 关于
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        # 帮助文档
        help_doc_action = QAction('帮助文档', self)
        help_menu.addAction(help_doc_action)
    
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = self.addToolBar('工具栏')
        
        # 刷新按钮
        refresh_action = QAction('刷新', self)
        refresh_action.triggered.connect(self.refresh_content)
        toolbar.addAction(refresh_action)
        
        # 分隔线
        toolbar.addSeparator()
        
        # 用户信息按钮
        profile_action = QAction('个人信息', self)
        profile_action.triggered.connect(self.show_user_profile)
        toolbar.addAction(profile_action)
        
        # 分隔线
        toolbar.addSeparator()
        
        # 退出登录按钮
        logout_action = QAction('退出登录', self)
        logout_action.triggered.connect(self.handle_logout)
        toolbar.addAction(logout_action)
    
    def init_status_bar(self):
        """初始化状态栏"""
        # 创建状态栏
        self.status_bar = self.statusBar()
        
        # 添加状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label, 1)  # 1表示拉伸因子
        
        # 添加用户信息标签
        self.user_label = QLabel(f"用户: {self.username} ({USER_ROLES[self.role]})")
        self.status_bar.addPermanentWidget(self.user_label)
    
    def connect_signals_slots(self):
        """连接信号和槽"""
        # 导航栏选择事件
        self.nav_widget.currentItemChanged.connect(self.on_nav_item_changed)
    
    def on_nav_item_changed(self, current, previous):
        """处理导航项变更事件"""
        if current:
            # 获取选中项的数据
            data = current.data(Qt.UserRole)
            
            # 调用仪表盘的切换页面方法
            if hasattr(self.dashboard, 'switch_page'):
                self.dashboard.switch_page(data)
    
    def update_status_bar(self):
        """更新状态栏信息"""
        # 这里可以添加更多状态信息的更新逻辑
        pass
    
    def refresh_content(self):
        """刷新内容"""
        # 调用仪表盘的刷新方法
        if hasattr(self.dashboard, 'refresh'):
            self.dashboard.refresh()
        
        # 更新状态栏信息
        self.update_status_bar()
        
        # 显示刷新成功提示
        self.status_label.setText("刷新成功")
        QTimer.singleShot(2000, lambda: self.status_label.setText("就绪"))
    
    def show_user_profile(self):
        """显示用户个人信息"""
        # 创建用户信息对话框
        profile_dialog = UserProfileDialog(self.user_info, self)
        profile_dialog.exec_()
        
        # 如果用户信息有更新，更新当前用户信息
        if profile_dialog.user_updated:
            self.user_info = profile_dialog.user_info
            # 刷新仪表盘
            self.refresh_content()
    
    def handle_logout(self):
        """处理退出登录事件"""
        # 确认退出登录
        reply = QMessageBox.question(
            self,
            "确认退出登录",
            "确定要退出登录吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 发送注销请求
            response = client.logout()
            
            # 断开与服务器的连接
            client.disconnect()
            
            # 标记登出流程，避免 closeEvent 再次弹出确认
            self.is_logging_out = True
            
            # 显示登录窗口
            self.show_login_window()
            
            # 关闭主窗口
            self.close()

    def show_login_window(self):
        """显示登录窗口，并在登录成功后打开新的主窗口"""
        from ui.login_window import LoginWindow
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        
        # 保持全局引用，避免因当前窗口关闭导致对象被GC
        app.login_window = LoginWindow()
        
        def on_login_success(user_info):
            app.main_window = MainWindow(user_info)
            app.main_window.show()
            # 登录成功后关闭登录窗口
            app.login_window.close()
            app.login_window = None
        
        app.login_window.login_success.connect(on_login_success)
        app.login_window.show()
    
    def show_about_dialog(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于系统",
            f"{MAIN_WINDOW_CONFIG['title']}\n\n版本: {MAIN_WINDOW_CONFIG['version']}\n\n开发者: {MAIN_WINDOW_CONFIG['developers']}\n\n描述: {MAIN_WINDOW_CONFIG['description']}"
        )
    
    def closeEvent(self, event):
        """重写关闭事件"""
        # 如果是登出流程触发的关闭，直接接受关闭
        if getattr(self, 'is_logging_out', False):
            event.accept()
            return
        
        # 确认退出
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出系统吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 断开与服务器的连接
            client.disconnect()
            
            # 接受关闭事件
            event.accept()
        else:
            # 拒绝关闭事件
            event.ignore()


# 测试代码
if __name__ == '__main__':
    # 这里只是为了测试，实际使用时用户信息应该从登录窗口传递过来
    test_user_info = {
        'id': 1,
        'username': 'testuser',
        'role': 'student',
        'name': '测试用户'
    }
    
    app = QApplication(sys.argv)
    window = MainWindow(test_user_info)
    window.show()
    sys.exit(app.exec_())