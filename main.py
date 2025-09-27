#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""学生成绩管理系统主入口"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from network.server import start_server

def main():
    """主函数，根据命令行参数启动服务器或客户端"""
    # 检查命令行参数，判断是否只启动服务器
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        # 只启动服务器模式
        print("启动服务器模式...")
        start_server()
    else:
        # 正常启动客户端模式（包含内嵌服务器）
        from ui.login_window import LoginWindow
        from ui.main_window import MainWindow
        from PyQt5.QtWidgets import QApplication
        import threading
        
        # 启动服务器线程
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # 创建Qt应用
        app = QApplication(sys.argv)
        
        # 创建主应用变量
        main_window = None
        
        # 定义登录成功处理函数
        def on_login_success(user_info):
            nonlocal main_window
            # 创建并显示主窗口
            main_window = MainWindow(user_info)
            main_window.show()
            
        # 显示登录窗口
        login_window = LoginWindow()
        login_window.login_success.connect(on_login_success)
        login_window.show()
        
        # 运行应用
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()