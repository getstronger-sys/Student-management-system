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
from models.enrollment import Enrollment

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
                    from datetime import datetime, date
                    if isinstance(obj, datetime):
                        return obj.strftime('%Y-%m-%d %H:%M:%S')
                    if isinstance(obj, date):
                        return obj.strftime('%Y-%m-%d')
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
        
        # 处理注册请求（未登录也可执行）
        elif action == 'register':
            username = params.get('username')
            password = params.get('password')
            role = params.get('role')
            name = params.get('name') or username
            
            # 服务端基础校验：密码长度
            if password is None or len(password) < 6:
                return {'success': False, 'message': '密码长度不得小于6位'}
            
            success = User.register(username, password, role, name)
            return {'success': success, 'message': '注册成功' if success else '注册失败或用户名已存在'}
        
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
        
        # 新增：搜索用户（管理员权限）
        elif action == 'search_users' and current_user['role'] == 'admin':
            keyword = params.get('keyword', '')
            users = User.search_users(keyword)
            return {'success': True, 'users': users}
        
        # 新增：个人密码修改（登录用户）
        elif action == 'change_password':
            new_password = params.get('password')
            if new_password is None or len(new_password) < 6:
                return {'success': False, 'message': '密码长度不得小于6位'}
            success = User.update_user(current_user['id'], password=new_password)
            return {'success': success, 'message': '修改成功' if success else '修改失败'}
        
        # 新增：学生管理（管理员权限）
        elif action == 'get_all_students' and current_user['role'] == 'admin':
            students = Student.get_all_students()
            return {'success': True, 'students': students}
        
        elif action == 'search_students' and current_user['role'] == 'admin':
            keyword = params.get('keyword', '')
            students = Student.search_students(keyword)
            return {'success': True, 'students': students}
        
        elif action == 'get_student_by_id' and current_user['role'] == 'admin':
            student_id = params.get('student_id')
            student = Student.get_student_by_id(student_id)
            if student:
                return {'success': True, 'student': student}
            return {'success': False, 'message': '未找到学生'}
        
        elif action == 'add_student' and current_user['role'] == 'admin':
            student_id = params.get('student_id')
            name = params.get('name')
            gender = params.get('gender')
            birth = params.get('birth')
            class_name = params.get('class') or params.get('class_name')
            major = params.get('major')
            # 管理员添加可不绑定用户
            success = Student.add_student(student_id, name, gender, birth, class_name, major, None)
            return {'success': success, 'message': '添加成功' if success else '添加失败'}
        
        elif action == 'update_student' and current_user['role'] == 'admin':
            student_id = params.get('student_id')
            name = params.get('name')
            gender = params.get('gender')
            birth = params.get('birth')
            class_name = params.get('class') or params.get('class_name')
            major = params.get('major')
            success = Student.update_student(student_id, name=name, gender=gender, birth=birth, class_name=class_name, major=major)
            return {'success': success, 'message': '更新成功' if success else '更新失败'}
        
        elif action == 'delete_student' and current_user['role'] == 'admin':
            student_id = params.get('student_id')
            # 若学生绑定了用户，则删除用户以级联清理学生信息
            try:
                student = Student.get_student_by_id(student_id)
                if student and student.get('user_id'):
                    user_id = student.get('user_id')
                    success = User.delete_user(user_id)
                else:
                    success = Student.delete_student(student_id)
            except Exception:
                success = False
            return {'success': success, 'message': '删除成功' if success else '删除失败'}
        
        # 新增：教师管理（管理员权限）
        elif action == 'get_all_teachers' and current_user['role'] == 'admin':
            teachers = Teacher.get_all_teachers()
            return {'success': True, 'teachers': teachers}
        
        elif action == 'search_teachers' and current_user['role'] == 'admin':
            keyword = params.get('keyword', '')
            teachers = Teacher.search_teachers(keyword)
            return {'success': True, 'teachers': teachers}
        
        elif action == 'get_teacher_by_id' and current_user['role'] == 'admin':
            teacher_id = params.get('teacher_id')
            teacher = Teacher.get_teacher_by_id(teacher_id)
            if teacher:
                return {'success': True, 'teacher': teacher}
            return {'success': False, 'message': '未找到教师'}
        
        elif action == 'add_teacher' and current_user['role'] == 'admin':
            teacher_id = params.get('teacher_id')
            name = params.get('name')
            gender = params.get('gender')
            title = params.get('title')
            department = params.get('department')
            success = Teacher.add_teacher(teacher_id, name, gender, title, department, None)
            return {'success': success, 'message': '添加成功' if success else '添加失败'}
        
        elif action == 'update_teacher' and current_user['role'] == 'admin':
            teacher_id = params.get('teacher_id')
            name = params.get('name')
            gender = params.get('gender')
            title = params.get('title')
            department = params.get('department')
            success = Teacher.update_teacher(teacher_id, name=name, gender=gender, title=title, department=department)
            return {'success': success, 'message': '更新成功' if success else '更新失败'}
        
        elif action == 'delete_teacher' and current_user['role'] == 'admin':
            teacher_id = params.get('teacher_id')
            success = Teacher.delete_teacher(teacher_id)
            return {'success': success, 'message': '删除成功' if success else '删除失败'}
        
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
        
        elif action == 'get_course_students' and current_user['role'] == 'teacher':
            course_id = params.get('course_id')
            # 确保该课程属于当前教师
            course = Course.get_course_by_id(course_id)
            if not course:
                return {'success': False, 'message': '课程不存在'}
            teacher = Teacher.get_teacher_by_user_id(current_user['id'])
            if not teacher or course.get('teacher_id') != teacher['id']:
                return {'success': False, 'message': '权限不足，您不是该课程的教师'}
            # 基于选课关系获取该课程的学生列表（不依赖是否已有成绩）
            students = Enrollment.get_students_by_course(course_id)
            return {'success': True, 'students': students or []}
        
        elif action == 'get_course_scores' and current_user['role'] == 'teacher':
            course_id = params.get('course_id')
            semester = params.get('semester')
            scores = Score.get_scores_by_course_and_semester(course_id, semester)
            stats = Score.get_score_statistics(course_id, semester)
            return {'success': True, 'scores': scores, 'statistics': stats}
            
        # 新增：课程管理（管理员权限）
        elif action == 'get_all_courses' and current_user['role'] == 'admin':
            courses = Course.get_all_courses()
            return {'success': True, 'courses': courses}
        
        elif action == 'search_courses' and current_user['role'] == 'admin':
            keyword = params.get('keyword', '')
            courses = Course.search_courses(keyword)
            return {'success': True, 'courses': courses}
        
        elif action == 'add_course' and current_user['role'] == 'admin':
            code = params.get('code')
            name = params.get('name')
            credit = params.get('credit')
            teacher_id = params.get('teacher_id')
            semester = params.get('semester')
            time = params.get('time')
            success = Course.add_course(code, name, credit, teacher_id, semester, time)
            return {'success': success, 'message': '添加成功' if success else '添加失败'}
            
        elif action == 'update_course' and current_user['role'] == 'admin':
            course_id = params.get('course_id')
            code = params.get('code')
            name = params.get('name')
            credit = params.get('credit')
            teacher_id = params.get('teacher_id')
            semester = params.get('semester')
            time = params.get('time')
            success = Course.update_course(course_id, code, name, credit, teacher_id, semester, time)
            return {'success': success, 'message': '更新成功' if success else '更新失败'}
            
        elif action == 'delete_course' and current_user['role'] == 'admin':
            course_id = params.get('course_id')
            success = Course.delete_course(course_id)
            return {'success': success, 'message': '删除成功' if success else '删除失败'}
        
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