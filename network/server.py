#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""网络服务端模块，处理客户端连接和请求"""

import socket
import threading
import json
import logging
from config.config import NETWORK_CONFIG
from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.courses import Course
from models.scores import Score

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('server')


class Server:
    """网络服务端类，处理客户端连接和请求"""
    
    def __init__(self):
        """初始化服务器"""
        self.host = NETWORK_CONFIG['host']
        self.port = NETWORK_CONFIG['port']
        self.server_socket = None
        self.clients = []
        self.running = False
        
    def start(self):
        """启动服务器"""
        try:
            # 创建套接字
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 绑定地址和端口
            self.server_socket.bind((self.host, self.port))
            
            # 开始监听
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"服务器已启动，监听地址: {self.host}:{self.port}")
            
            # 不断接受新的客户端连接
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    logger.info(f"新客户端连接: {client_address}")
                    
                    # 为每个客户端创建一个线程处理请求
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                    client_thread.daemon = True
                    client_thread.start()
                    
                    # 添加到客户端列表
                    self.clients.append((client_socket, client_address))
                except socket.error as e:
                    if not self.running:
                        break
                    logger.error(f"接受客户端连接失败: {e}")
        except Exception as e:
            logger.error(f"服务器启动失败: {e}")
    
    def stop(self):
        """停止服务器"""
        self.running = False
        
        # 关闭所有客户端连接
        for client_socket, _ in self.clients:
            try:
                client_socket.close()
            except:
                pass
        
        # 关闭服务器套接字
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("服务器已停止")
    
    def handle_client(self, client_socket, client_address):
        """处理客户端请求"""
        current_user = None
        
        try:
            while self.running:
                # 接收客户端消息
                data = self.receive_data(client_socket)
                if not data:
                    break
                
                # 解析请求
                request = json.loads(data)
                action = request.get('action')
                params = request.get('params', {})
                
                # 根据操作类型处理请求
                response = self.process_request(action, params, current_user)
                
                # 如果是登录操作，更新当前用户
                if action == 'login' and response.get('success'):
                    current_user = response.get('user')
                # 如果是注销操作，清除当前用户
                elif action == 'logout' and response.get('success'):
                    current_user = None
                
                # 发送响应
                self.send_data(client_socket, response)
        except Exception as e:
            logger.error(f"处理客户端请求失败 ({client_address}): {e}")
        finally:
            # 关闭客户端连接
            try:
                client_socket.close()
                self.clients.remove((client_socket, client_address))
                logger.info(f"客户端断开连接: {client_address}")
            except:
                pass
    
    def receive_data(self, client_socket):
        """接收客户端数据"""
        try:
            # 首先接收数据长度
            length_data = client_socket.recv(4)
            if not length_data:
                return None
            
            # 解析数据长度
            data_length = int.from_bytes(length_data, byteorder='big')
            
            # 接收实际数据
            data = b''
            while len(data) < data_length:
                packet = client_socket.recv(data_length - len(data))
                if not packet:
                    return None
                data += packet
            
            # 解码数据
            return data.decode('utf-8')
        except Exception as e:
            logger.error(f"接收数据失败: {e}")
            return None
    
    def send_data(self, client_socket, data):
        """发送数据到客户端"""
        try:
            # 自定义JSON编码器处理datetime对象
            class DateTimeEncoder(json.JSONEncoder):
                def default(self, obj):
                    from datetime import datetime
                    if isinstance(obj, datetime):
                        return obj.strftime('%Y-%m-%d %H:%M:%S')
                    return super(DateTimeEncoder, self).default(obj)
            
            # 序列化数据，使用自定义编码器
            json_data = json.dumps(data, cls=DateTimeEncoder)
            
            # 发送数据长度
            data_length = len(json_data.encode('utf-8'))
            client_socket.sendall(data_length.to_bytes(4, byteorder='big'))
            
            # 发送实际数据
            client_socket.sendall(json_data.encode('utf-8'))
        except Exception as e:
            logger.error(f"发送数据失败: {e}")
    
    def process_request(self, action, params, current_user):
        """处理请求并返回响应"""
        # 处理登录请求
        if action == 'login':
            username = params.get('username')
            password = params.get('password')
            
            user = User.login(username, password)
            if user:
                return {'success': True, 'user': user}
            else:
                return {'success': False, 'message': '用户名或密码错误'}
        
        # 处理注销请求
        elif action == 'logout':
            return {'success': True, 'message': '注销成功'}
        
        # 以下操作需要用户登录
        if not current_user:
            return {'success': False, 'message': '请先登录'}
        
        # 用户管理操作 (管理员权限)
        if action == 'get_all_users' and current_user['role'] == 'admin':
            users = User.get_all_users()
            return {'success': True, 'users': users}
        
        elif action == 'get_user_by_id' and current_user['role'] == 'admin':
            user_id = params.get('user_id')
            user = User.get_user_by_id(user_id)
            if user:
                return {'success': True, 'user': user}
            else:
                return {'success': False, 'message': '未找到用户'}
        
        elif action == 'delete_user' and current_user['role'] == 'admin':
            user_id = params.get('user_id')
            success = User.delete_user(user_id)
            return {'success': success, 'message': '删除成功' if success else '删除失败'}
        
        # 更新用户信息操作 (管理员权限)
        elif action == 'update_user' and current_user['role'] == 'admin':
            user_id = params.get('user_id')
            # 从params中提取需要更新的字段
            name = params.get('name')
            password = params.get('password')
            role = params.get('role')
            email = params.get('email')
            
            # 调用User模型的update_user方法
            success = User.update_user(user_id, name=name, password=password, role=role, email=email)
            return {'success': success, 'message': '更新成功' if success else '更新失败'}
        
        # 学生管理操作
        elif action == 'get_student_info' and current_user['role'] in ['admin', 'student']:
            if current_user['role'] == 'student':
                student = Student.get_student_by_user_id(current_user['id'])
            else:
                student_id = params.get('student_id')
                student = Student.get_student_by_id(student_id)
            return {'success': True, 'student': student}
        
        elif action == 'update_student_info' and current_user['role'] in ['admin', 'student']:
            if current_user['role'] == 'student':
                student = Student.get_student_by_user_id(current_user['id'])
                if student:
                    success = Student.update_student(student['student_id'], **params)
            else:
                student_id = params.get('student_id')
                success = Student.update_student(student_id, **params)
            return {'success': success, 'message': '更新成功' if success else '更新失败'}
        
        # 成绩查询操作
        elif action == 'get_my_scores' and current_user['role'] == 'student':
            student = Student.get_student_by_user_id(current_user['id'])
            if student:
                scores = Score.get_scores_by_student_id(student['id'])
                gpa = Score.calculate_gpa(student['id'])
                return {'success': True, 'scores': scores, 'gpa': gpa}
            return {'success': False, 'message': '获取成绩失败'}
        
        # 教师相关操作
        elif action == 'get_my_courses' and current_user['role'] == 'teacher':
            teacher = Teacher.get_teacher_by_user_id(current_user['id'])
            if teacher:
                courses = Course.get_courses_by_teacher_id(teacher['id'])
                return {'success': True, 'courses': courses}
            return {'success': False, 'message': '获取课程失败'}
        
        elif action == 'get_course_scores' and current_user['role'] == 'teacher':
            course_id = params.get('course_id')
            semester = params.get('semester')
            scores = Score.get_scores_by_course_and_semester(course_id, semester)
            stats = Score.get_score_statistics(course_id, semester)
            return {'success': True, 'scores': scores, 'stats': stats}
        
        # 其他操作...
        return {'success': False, 'message': '未知操作或权限不足'}


# 全局服务器实例
server = Server()


def start_server():
    """启动服务器的函数"""
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("服务器被用户中断")
    finally:
        server.stop()


def stop_server():
    """停止服务器的函数"""
    server.stop()