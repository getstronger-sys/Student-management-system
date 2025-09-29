#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""网络客户端模块，与服务器进行通信"""

import socket
import json
import logging
from config.config import NETWORK_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('client')


class Client:
    """网络客户端类，与服务器进行通信"""
    
    def __init__(self):
        """初始化客户端"""
        # 修改为服务器的IP地址，组内其他同学运行时需要将此地址改为服务器同学的IP
        #self.host = '10.29.108.168'  # 客户端连接地址（校园网IP）
        self.host = '127.0.0.1'
        self.port = NETWORK_CONFIG['port']
        self.client_socket = None
        self.connected = False
        self.current_user = None
    
    def connect(self):
        """连接到服务器"""
        try:
            # 创建套接字
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # 连接到服务器
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            
            logger.info(f"已连接到服务器: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"连接服务器失败: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """断开与服务器的连接"""
        try:
            if self.client_socket:
                self.client_socket.close()
            self.connected = False
            self.current_user = None
            logger.info("已断开与服务器的连接")
        except Exception as e:
            logger.error(f"断开连接失败: {e}")
    
    def send_request(self, action, params=None):
        """发送请求到服务器并返回响应"""
        if not self.connected:
            logger.error("未连接到服务器")
            return {'success': False, 'message': '未连接到服务器'}
        
        try:
            # 构建请求数据
            request = {'action': action, 'params': params or {}}
            
            # 发送数据
            self._send_data(request)
            
            # 接收响应
            response = self._receive_data()
            
            # 如果是登录成功，保存当前用户信息
            if action == 'login' and response.get('success'):
                self.current_user = response.get('user')
            # 如果是注销成功，清除当前用户信息
            elif action == 'logout' and response.get('success'):
                self.current_user = None
            
            return response
        except Exception as e:
            logger.error(f"发送请求失败: {e}")
            # 发生错误时断开连接
            self.disconnect()
            return {'success': False, 'message': f'发送请求失败: {str(e)}'}
    
    def _send_data(self, data):
        """发送数据到服务器"""
        # 序列化数据
        json_data = json.dumps(data)
        
        # 发送数据长度
        data_length = len(json_data.encode('utf-8'))
        self.client_socket.sendall(data_length.to_bytes(4, byteorder='big'))
        
        # 发送实际数据
        self.client_socket.sendall(json_data.encode('utf-8'))
    
    def _receive_data(self):
        """接收服务器返回的数据"""
        # 接收数据长度
        length_data = self.client_socket.recv(4)
        if not length_data:
            raise Exception("服务器已断开连接")
        
        # 解析数据长度
        data_length = int.from_bytes(length_data, byteorder='big')
        
        # 接收实际数据
        data = b''
        while len(data) < data_length:
            packet = self.client_socket.recv(data_length - len(data))
            if not packet:
                raise Exception("服务器已断开连接")
            data += packet
        
        # 解码数据并解析JSON
        return json.loads(data.decode('utf-8'))
    
    # 快捷方法：登录
    def login(self, username, password):
        """登录到系统"""
        return self.send_request('login', {'username': username, 'password': password})
    
    # 新增：快捷方法：注册
    def register(self, username, password, role, name):
        """注册新用户"""
        return self.send_request('register', {
            'username': username,
            'password': password,
            'role': role,
            'name': name
        })
    
    # 快捷方法：注销
    def logout(self):
        """退出登录"""
        return self.send_request('logout')
    
    # 快捷方法：获取学生信息
    def get_student_info(self, student_id=None):
        """获取学生信息"""
        params = {} if student_id is None else {'student_id': student_id}
        return self.send_request('get_student_info', params)
    
    # 快捷方法：更新学生信息
    def update_student_info(self, student_id=None, **kwargs):
        """更新学生信息"""
        params = kwargs
        if student_id is not None:
            params['student_id'] = student_id
        return self.send_request('update_student_info', params)
    
    # 快捷方法：获取我的成绩
    def get_my_scores(self):
        """获取当前学生的成绩"""
        return self.send_request('get_my_scores')
    
    # 快捷方法：获取我的课程（教师）
    def get_my_courses(self):
        """获取当前教师的课程"""
        return self.send_request('get_my_courses')
    
    # 快捷方法：获取课程成绩（教师）
    def get_course_scores(self, course_id, semester):
        """获取指定课程和学期的成绩"""
        return self.send_request('get_course_scores', {'course_id': course_id, 'semester': semester})
    
    # 快捷方法：获取所有用户（管理员）
    def get_all_users(self):
        """获取所有用户信息（管理员）"""
        return self.send_request('get_all_users')
    
    # 新增：快捷方法：搜索用户（管理员）
    def search_users(self, keyword: str):
        """根据关键词搜索用户（管理员）"""
        return self.send_request('search_users', {'keyword': keyword})
    
    # 学生管理（管理员）
    def get_all_students_admin(self):
        return self.send_request('get_all_students')
    
    def search_students_admin(self, keyword: str):
        return self.send_request('search_students', {'keyword': keyword})
    
    def add_student_admin(self, student):
        return self.send_request('add_student', student)
    
    def update_student_admin(self, student):
        return self.send_request('update_student', student)
    
    def delete_student_admin(self, student_id):
        return self.send_request('delete_student', {'student_id': student_id})
    
    # 教师管理（管理员）
    def get_all_teachers_admin(self):
        return self.send_request('get_all_teachers')
    
    def search_teachers_admin(self, keyword: str):
        return self.send_request('search_teachers', {'keyword': keyword})
    
    def add_teacher_admin(self, teacher):
        return self.send_request('add_teacher', teacher)
    
    def update_teacher_admin(self, teacher):
        return self.send_request('update_teacher', teacher)
    
    def delete_teacher_admin(self, teacher_id):
        return self.send_request('delete_teacher', {'teacher_id': teacher_id})
    
    # 课程管理（管理员）
    def add_course_admin(self, code, name, credit, teacher_id, semester, time):
        """添加课程（管理员）"""
        return self.send_request('add_course', {
            'code': code,
            'name': name,
            'credit': credit,
            'teacher_id': teacher_id,
            'semester': semester,
            'time': time
        })
    
    def update_course_admin(self, course_id, code, name, credit, teacher_id, semester, time):
        """更新课程（管理员）"""
        return self.send_request('update_course', {
            'course_id': course_id,
            'code': code,
            'name': name,
            'credit': credit,
            'teacher_id': teacher_id,
            'semester': semester,
            'time': time
        })
    
    def delete_course_admin(self, course_id):
        """删除课程（管理员）"""
        return self.send_request('delete_course', {'course_id': course_id})
    
    def get_all_courses_admin(self):
        """获取所有课程（管理员）"""
        return self.send_request('get_all_courses', {})
    
    def search_courses_admin(self, keyword):
        """搜索课程（管理员）"""
        return self.send_request('search_courses', {'keyword': keyword})
    
    # 个人密码修改（登录用户）
    def change_password(self, new_password: str):
        return self.send_request('change_password', {'password': new_password})
    
    # 快捷方法：删除用户（管理员）
    def delete_user(self, user_id):
        """删除用户（管理员）"""
        return self.send_request('delete_user', {'user_id': user_id})
    
    # 快捷方法：更新用户信息（管理员）
    def update_user(self, user_id, **kwargs):
        """更新用户信息（管理员）"""
        params = kwargs
        params['user_id'] = user_id
        return self.send_request('update_user', params)


# 全局客户端实例
client = Client()


# 一些测试函数
if __name__ == '__main__':
    # 创建客户端实例
    test_client = Client()
    
    # 连接到服务器
    if test_client.connect():
        # 测试登录
        login_response = test_client.login('admin', 'admin123')
        print(f"登录结果: {login_response}")
        
        # 如果登录成功，测试其他功能
        if login_response.get('success'):
            # 测试获取所有用户
            users_response = test_client.get_all_users()
            print(f"所有用户: {users_response}")
            
            # 测试注销
            logout_response = test_client.logout()
            print(f"注销结果: {logout_response}")
        
        # 断开连接
        test_client.disconnect()