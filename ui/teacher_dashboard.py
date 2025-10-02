#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""教师仪表盘模块"""

import sys
import logging
import os
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib
matplotlib.use('Qt5Agg')  # 使用Qt5后端
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QTabWidget, QFrame, QMessageBox, QComboBox,
    QPushButton, QLineEdit, QFormLayout, QGroupBox, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from network.client import client
from models.teacher import Teacher
from models.courses import Course
from models.scores import Score
from models.enrollment import Enrollment
from models.student import Student
import utils.data_visualization

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('teacher_dashboard')


class TeacherDashboard(QWidget):
    """教师仪表盘类"""
    
    def __init__(self, user_info):
        """初始化教师仪表盘"""
        super().__init__()
        
        # 保存用户信息
        self.user_info = user_info
        self.teacher_id = None
        
        # 初始化UI
        self.init_ui()
        
        # 加载数据
        self.load_teacher_info()
        self.load_courses()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 创建个人信息标签页
        self.create_profile_tab()
        
        # 创建我的课程标签页
        self.create_courses_tab()
        
        # 创建成绩管理标签页
        self.create_scores_tab()
        
        # 创建学生管理标签页
        self.create_students_tab()
        
        # 创建数据分析标签页
        self.create_analysis_tab()
        
        # 添加标签页到标签部件
        self.tab_widget.addTab(self.profile_widget, "个人信息")
        self.tab_widget.addTab(self.courses_widget, "我的课程")
        self.tab_widget.addTab(self.scores_widget, "成绩管理")
        self.tab_widget.addTab(self.students_widget, "学生管理")
        self.tab_widget.addTab(self.analysis_widget, "数据分析")
        
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
        
        # 教师ID
        self.teacher_id_label = QLabel("教师ID: ")
        profile_form_layout.addWidget(self.teacher_id_label)
        
        # 姓名
        self.name_label = QLabel("姓名: ")
        profile_form_layout.addWidget(self.name_label)
        
        # 性别
        self.gender_label = QLabel("性别: ")
        profile_form_layout.addWidget(self.gender_label)
        
        # 年龄
        self.age_label = QLabel("年龄: ")
        profile_form_layout.addWidget(self.age_label)
        
        # 部门
        self.department_label = QLabel("部门: ")
        profile_form_layout.addWidget(self.department_label)
        
        # 职称
        self.title_label = QLabel("职称: ")
        profile_form_layout.addWidget(self.title_label)
        
        # 添加个人信息组框到布局
        profile_layout.addWidget(profile_group)
    
    def create_courses_tab(self):
        """创建我的课程标签页"""
        self.courses_widget = QWidget()
        courses_layout = QVBoxLayout(self.courses_widget)
        
        # 创建课程表格
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(7)
        self.courses_table.setHorizontalHeaderLabels(["课程代码", "课程名称", "学分", "学期", "上课时间", "上课地点", "学生人数"])
        
        # 设置表格样式
        self.courses_table.horizontalHeader().setStretchLastSection(True)
        
        # 添加课程表格到布局
        courses_layout.addWidget(self.courses_table)
    
    def create_scores_tab(self):
        """创建成绩管理标签页"""
        self.scores_widget = QWidget()
        scores_layout = QVBoxLayout(self.scores_widget)
        
        # 创建搜索和筛选布局
        search_layout = QHBoxLayout()
        
        # 课程选择
        self.course_combo = QComboBox()
        search_layout.addWidget(QLabel("选择课程:"))
        search_layout.addWidget(self.course_combo)
        search_layout.addSpacing(20)
        
        # 学期选择（将由课程加载时动态填充）
        self.semester_combo = QComboBox()
        search_layout.addWidget(QLabel("选择学期:"))
        search_layout.addWidget(self.semester_combo)
        search_layout.addSpacing(20)
        
        # 查询按钮
        self.query_button = QPushButton("查询")
        self.query_button.clicked.connect(self.query_scores)
        search_layout.addWidget(self.query_button)
        
        # 批量导入导出按钮
        self.import_scores_button = QPushButton("批量导入")
        self.import_scores_button.clicked.connect(self.import_scores)
        search_layout.addWidget(self.import_scores_button)
        
        self.export_scores_button = QPushButton("批量导出")
        self.export_scores_button.clicked.connect(self.export_scores)
        search_layout.addWidget(self.export_scores_button)
        
        search_layout.addStretch()
        
        # 添加搜索布局到主布局
        scores_layout.addLayout(search_layout)
        
        # 创建成绩表格
        self.scores_table = QTableWidget()
        self.scores_table.setColumnCount(5)
        self.scores_table.setHorizontalHeaderLabels(["学生ID", "学生姓名", "成绩", "学分", "操作"])
        
        # 设置表格样式
        self.scores_table.horizontalHeader().setStretchLastSection(True)
        
        # 添加成绩表格到布局
        scores_layout.addWidget(self.scores_table)
        
        # 添加成绩统计信息
        stats_layout = QHBoxLayout()
        stats_label = QLabel("成绩统计: ")
        self.stats_value_label = QLabel("平均分: 0, 最高分: 0, 最低分: 0, 及格率: 0%")
        stats_layout.addWidget(stats_label)
        stats_layout.addWidget(self.stats_value_label)
        stats_layout.addStretch()
        scores_layout.addLayout(stats_layout)
    
    def create_students_tab(self):
        """创建学生管理标签页"""
        self.students_widget = QWidget()
        students_layout = QVBoxLayout(self.students_widget)

        # 顶部课程选择与操作区
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("选择课程:"))
        self.students_course_combo = QComboBox()
        top_layout.addWidget(self.students_course_combo)
        load_btn = QPushButton("加载学生")
        load_btn.clicked.connect(self.load_students)
        top_layout.addWidget(load_btn)
        top_layout.addStretch()
        students_layout.addLayout(top_layout)
        
        # 创建搜索框
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("请输入学生姓名或学号")
        search_layout.addWidget(self.search_edit)
        
        # 搜索按钮
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_students)
        search_layout.addWidget(self.search_button)
        
        # 添加搜索布局到主布局
        students_layout.addLayout(search_layout)
        
        # 创建学生表格
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(7)
        self.students_table.setHorizontalHeaderLabels(["学生ID", "姓名", "性别", "年龄", "专业", "班级", "操作"])
        
        # 设置表格样式
        self.students_table.horizontalHeader().setStretchLastSection(True)
        
        # 添加学生表格到布局
        students_layout.addWidget(self.students_table)
    
    def create_analysis_tab(self):
        """创建数据分析标签页"""
        self.analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(self.analysis_widget)
        
        # 添加课程选择和刷新按钮
        analysis_top_layout = QHBoxLayout()
        analysis_top_layout.addWidget(QLabel("选择课程:"))
        self.analysis_course_combo = QComboBox()
        analysis_top_layout.addWidget(self.analysis_course_combo)
        
        refresh_btn = QPushButton("刷新图表")
        refresh_btn.clicked.connect(self.load_analysis_data)
        analysis_top_layout.addWidget(refresh_btn)
        analysis_top_layout.addStretch()
        
        analysis_layout.addLayout(analysis_top_layout)
        
        # 创建图表
        self.create_charts()
        
        # 创建图表布局
        charts_layout = QHBoxLayout()
        charts_layout.addWidget(self.score_distribution_widget)
        charts_layout.addWidget(self.course_comparison_widget)
        
        # 添加图表布局到主布局
        analysis_layout.addLayout(charts_layout)
    
    def load_analysis_courses(self):
        """加载数据分析标签页的课程列表"""
        try:
            # 获取教师课程（优先服务器，失败则本地回退）
            response = client.get_my_courses()
            courses = response.get('courses', []) if response.get('success') else []
            if not courses:
                try:
                    teacher = Teacher.get_teacher_by_user_id(self.user_info.get('id'))
                    if teacher:
                        courses = Course.get_courses_by_teacher_id(teacher.get('id')) or []
                        # 确保本地获取的课程数据格式正确
                        if courses:
                            logger.info(f"本地回退获取到{len(courses)}门课程")
                except Exception as e:
                    logger.error(f"本地回退获取课程失败: {e}")
                    courses = []
            else:
                logger.info(f"从服务器获取到{len(courses)}门课程")
            
            # 清空课程下拉框
            self.analysis_course_combo.clear()
            
            # 添加课程到下拉框
            for course in courses:
                self.analysis_course_combo.addItem(course.get('course_name', ''), course.get('id'))
                logger.debug(f"添加课程到下拉框: {course.get('course_name', '')}")
            
            # 如果有课程，默认加载第一个课程的数据分析
            if courses:
                # 存储课程列表，供后续获取学期信息使用
                self.analysis_courses = courses
                self.load_analysis_data()
            else:
                logger.warning("未获取到任何课程数据")
        except Exception as e:
            logger.error(f"加载分析课程失败: {e}")
    
    def load_analysis_data(self):
        """加载并显示选定课程的数据分析数据"""
        try:
            # 获取选中的课程ID
            idx = self.analysis_course_combo.currentIndex()
            if idx < 0:
                QMessageBox.information(self, "提示", "请先选择课程")
                return
            
            course_id = self.analysis_course_combo.itemData(idx)
            course_name = self.analysis_course_combo.currentText()
            
            # 获取课程对应的学期
            semester = ""
            if hasattr(self, 'analysis_courses'):
                for course in self.analysis_courses:
                    if course.get('id') == course_id:
                        semester = course.get('semester', '')
                        break
            
            # 如果没有获取到学期，使用默认值
            if not semester:
                semester = "2025-2026-1"
            
            logger.info(f"加载课程 '{course_name}' (ID: {course_id}, 学期: {semester}) 的分析数据")
            
            # 获取该课程的成绩数据（优先服务器），现在传入正确的两个参数
            response = client.get_course_scores(course_id, semester)
            if response.get('success'):
                scores = response.get('scores', [])
                logger.info(f"从服务器获取到{len(scores)}条成绩数据")
            else:
                # 本地回退
                logger.info(f"服务器获取失败，尝试本地回退")
                from models.scores import Score
                scores = Score.get_scores_by_course(course_id) or []
                logger.info(f"本地回退获取到{len(scores)}条成绩数据")
                # 为了兼容，为每个分数添加课程名称
                for score in scores:
                    if 'course_name' not in score:
                        score['course_name'] = course_name
            
            # 更新图表
            self.update_charts(scores)
        except Exception as e:
            logger.error(f"加载分析数据失败: {e}")
            QMessageBox.warning(self, "加载失败", f"加载分析数据失败: {str(e)}")
    
    def create_charts(self):
        """创建数据可视化图表"""
        # 成绩分布图表
        self.score_distribution_widget = QWidget()
        score_distribution_layout = QVBoxLayout(self.score_distribution_widget)
        
        # 创建成绩分布标题
        score_distribution_title = QLabel("课程成绩分布")
        score_distribution_title.setAlignment(Qt.AlignCenter)
        score_distribution_title.setStyleSheet("font-weight: bold;")
        score_distribution_layout.addWidget(score_distribution_title)
        
        # 创建成绩分布图表
        self.score_distribution_canvas = ScoreDistributionCanvas(self)
        score_distribution_layout.addWidget(self.score_distribution_canvas)
        
        # 课程对比图表
        self.course_comparison_widget = QWidget()
        course_comparison_layout = QVBoxLayout(self.course_comparison_widget)
        
        # 创建课程对比标题
        course_comparison_title = QLabel("各课程成绩对比")
        course_comparison_title.setAlignment(Qt.AlignCenter)
        course_comparison_title.setStyleSheet("font-weight: bold;")
        course_comparison_layout.addWidget(course_comparison_title)
        
        # 创建课程对比图表
        self.course_comparison_canvas = CourseComparisonCanvas(self)
        course_comparison_layout.addWidget(self.course_comparison_canvas)
    
    def load_teacher_info(self):
        """加载教师信息"""
        try:
            # 这里简化处理，实际可能需要调用特定的API获取教师信息
            # 假设教师信息存储在用户信息中
            self.teacher_id = self.user_info.get('id')
            
            # 更新界面显示
            self.teacher_id_label.setText(f"教师ID: {self.teacher_id}")
            self.name_label.setText(f"姓名: {self.user_info.get('name', '')}")
            self.gender_label.setText(f"性别: {self.user_info.get('gender', '')}")
            self.age_label.setText(f"年龄: {self.user_info.get('age', '')}")
            self.department_label.setText(f"部门: {self.user_info.get('department', '')}")
            self.title_label.setText(f"职称: {self.user_info.get('title', '')}")
        except Exception as e:
            logger.error(f"加载教师信息失败: {e}")
            QMessageBox.warning(self, "加载失败", f"加载教师信息失败: {str(e)}")
    
    def load_courses(self):
        """加载教师课程"""
        try:
            # 获取教师课程（优先服务器，失败则本地回退）
            response = client.get_my_courses()
            courses = response.get('courses', []) if response.get('success') else []
            if not courses:
                try:
                    teacher = Teacher.get_teacher_by_user_id(self.user_info.get('id'))
                    if teacher:
                        courses = Course.get_courses_by_teacher_id(teacher.get('id')) or []
                        # 兼容字段：将class_location转为class_room
                        for c in courses:
                            if 'class_location' in c and 'class_room' not in c:
                                c['class_room'] = c.get('class_location')
                except Exception:
                    courses = []

            # 清空表格和下拉框
            self.courses_table.setRowCount(0)
            self.course_combo.clear()

            # 添加课程到下拉框和表格（同步填充学生页课程下拉框）
            for course in courses:
                # 添加到下拉框
                self.course_combo.addItem(course.get('course_name', ''), course.get('id'))
                if hasattr(self, 'students_course_combo'):
                    self.students_course_combo.addItem(course.get('course_name', ''), course.get('id'))
                # 添加到表格
                row_position = self.courses_table.rowCount()
                self.courses_table.insertRow(row_position)
                # 设置表格数据
                self.courses_table.setItem(row_position, 0, QTableWidgetItem(course.get('course_code', '')))
                self.courses_table.setItem(row_position, 1, QTableWidgetItem(course.get('course_name', '')))
                self.courses_table.setItem(row_position, 2, QTableWidgetItem(str(course.get('credits', ''))))
                self.courses_table.setItem(row_position, 3, QTableWidgetItem(course.get('semester', '')))
                self.courses_table.setItem(row_position, 4, QTableWidgetItem(course.get('class_time', '')))
                self.courses_table.setItem(row_position, 5, QTableWidgetItem(course.get('class_room', '')))
                self.courses_table.setItem(row_position, 6, QTableWidgetItem(str(course.get('student_count', 0))))

            # 调整表格列宽
            self.courses_table.resizeColumnsToContents()

            # 根据课程动态填充学期下拉框
            semesters = []
            for c in courses:
                sem = c.get('semester')
                if sem and sem not in semesters:
                    semesters.append(sem)
            self.semester_combo.clear()
            if semesters:
                self.semester_combo.addItems(semesters)
            else:
                # 无课程时提供默认学期，避免空
                self.semester_combo.addItems(["2025-2026-1", "2025-2026-2"])            
        except Exception as e:
            logger.error(f"加载教师课程失败: {e}")
            QMessageBox.warning(self, "加载失败", f"加载教师课程失败: {str(e)}")
    
    def query_scores(self):
        """查询成绩"""
        try:
            # 获取选择的课程和学期
            course_index = self.course_combo.currentIndex()
            if course_index < 0:
                QMessageBox.warning(self, "选择错误", "请先选择课程")
                return
            
            course_id = self.course_combo.itemData(course_index)
            semester = self.semester_combo.currentText()
            
            # 查询成绩
            response = client.get_course_scores(course_id, semester)
            
            if response.get('success'):
                scores = response.get('scores', [])
                stats = response.get('statistics', {})
                
                # 清空表格
                self.scores_table.setRowCount(0)
                
                # 获取学生信息映射表
                from models.student import Student
                student_ids = list(set([score_info.get('student_id') for score_info in scores if score_info.get('student_id') is not None]))
                students_map = {}
                for student_id in student_ids:
                    # 使用新方法根据内部ID查询学生信息
                    student_info = Student.get_student_by_internal_id(student_id)
                    if student_info:
                        students_map[student_id] = student_info
                
                # 填充表格
                for score_info in scores:
                    row_position = self.scores_table.rowCount()
                    self.scores_table.insertRow(row_position)
                    
                    # 设置表格数据 - 确保所有字段都正确处理
                    # 学生ID - 获取真实学号
                    student_id = score_info.get('student_id', '')
                    student_info = students_map.get(student_id, {})
                    # 使用学生表中的真实学号(student_id字段)
                    actual_student_id = student_info.get('student_id', str(student_id))  # 如未找到则使用原始ID作为 fallback
                    self.scores_table.setItem(row_position, 0, QTableWidgetItem(str(actual_student_id)))
                    
                    # 学生姓名 - 优先使用学生表中的姓名
                    student_name = student_info.get('name', '')
                    if not student_name:
                        student_name = score_info.get('student_name', '')
                        if not student_name:
                            student_name = score_info.get('name', '')
                    self.scores_table.setItem(row_position, 1, QTableWidgetItem(str(student_name)))
                    
                    # 创建成绩编辑框
                    score_value = score_info.get('score', '')
                    score_item = QTableWidgetItem(str(score_value) if score_value is not None else '')
                    self.scores_table.setItem(row_position, 2, score_item)
                    
                    # 学分 - 确保转换为字符串
                    credits = score_info.get('credits', '')
                    self.scores_table.setItem(row_position, 3, QTableWidgetItem(str(credits) if credits is not None else ''))
                    
                    # 添加编辑按钮
                    score_id = score_info.get('id')
                    if score_id is not None:
                        edit_button = QPushButton("编辑")
                        edit_button.clicked.connect(lambda checked, row=row_position, score_id=score_id: self.edit_score(row, score_id))
                        self.scores_table.setCellWidget(row_position, 4, edit_button)
                    else:
                        # 如果没有score_id，显示一个不可点击的标签
                        self.scores_table.setItem(row_position, 4, QTableWidgetItem("无法编辑"))
                
                # 调整表格列宽
                self.scores_table.resizeColumnsToContents()
                
                # 更新统计信息
                avg_score = stats.get('avg_score', 0)
                max_score = stats.get('max_score', 0)
                min_score = stats.get('min_score', 0)
                pass_rate = stats.get('pass_rate', 0)
                
                self.stats_value_label.setText(f"平均分: {avg_score:.2f}, 最高分: {max_score}, 最低分: {min_score}, 及格率: {pass_rate:.2f}%")
                
                # 更新图表
                self.update_charts(scores)
        except Exception as e:
            logger.error(f"查询成绩失败: {e}")
            QMessageBox.warning(self, "查询失败", f"查询成绩失败: {str(e)}")
    
    def load_students(self):
        """加载学生数据"""
        try:
            # 优先使用学生页选择的课程
            course_id = None
            if hasattr(self, 'students_course_combo') and self.students_course_combo.count() > 0:
                idx = self.students_course_combo.currentIndex()
                if idx >= 0:
                    course_id = self.students_course_combo.itemData(idx)
            # 若未选择，按教师课程列表回退选取第一个
            if course_id is None:
                courses_response = client.get_my_courses()
                courses = courses_response.get('courses', []) if courses_response.get('success') else []
                if not courses:
                    try:
                        teacher = Teacher.get_teacher_by_user_id(self.user_info.get('id'))
                        if teacher:
                            courses = Course.get_courses_by_teacher_id(teacher.get('id')) or []
                    except Exception:
                        courses = []
                if courses:
                    course_id = courses[0].get('id')
                else:
                    QMessageBox.information(self, "提示", "没有可用课程")
                    return
            # 获取该课程的学生列表（优先服务端）
            response = client.get_course_students(course_id)
            if response.get('success'):
                students = response.get('students', [])
            else:
                students = Enrollment.get_students_by_course(course_id) or []
            # 清空表格
            self.students_table.setRowCount(0)
            # 添加学生数据到表格
            for s in students:
                row = self.students_table.rowCount()
                self.students_table.insertRow(row)
                # 学生ID - 确保格式正确
                student_id = s.get('student_id', '')
                # 确保学生ID是字符串类型
                formatted_id = str(student_id)
                self.students_table.setItem(row, 0, QTableWidgetItem(formatted_id))
                # 姓名
                self.students_table.setItem(row, 1, QTableWidgetItem(s.get('name', '')))
                # 性别
                self.students_table.setItem(row, 2, QTableWidgetItem(s.get('gender', '')))
                # 年龄（根据出生日期计算）
                age_text = ''
                try:
                    birth_val = s.get('birth')
                    if birth_val:
                        from datetime import datetime, date
                        if isinstance(birth_val, str):
                            birth_date = datetime.strptime(birth_val, '%Y-%m-%d').date()
                        elif isinstance(birth_val, date):
                            birth_date = birth_val
                        else:
                            birth_date = None
                        if birth_date:
                            today = date.today()
                            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                            age_text = str(age)
                except Exception:
                    age_text = ''
                self.students_table.setItem(row, 3, QTableWidgetItem(age_text))
                # 专业
                self.students_table.setItem(row, 4, QTableWidgetItem(s.get('major', '')))
                # 班级
                self.students_table.setItem(row, 5, QTableWidgetItem(s.get('class', '')))
                # 操作列（删除按钮）
                delete_button = QPushButton("删除")
                delete_button.clicked.connect(lambda checked, student_id=s.get('id'), student_name=s.get('name', ''): self.delete_student(student_id, student_name))
                self.students_table.setCellWidget(row, 6, delete_button)
            # 调整列宽
            self.students_table.resizeColumnsToContents()
        except Exception as e:
            logger.error(f"加载学生数据失败: {e}")
            QMessageBox.warning(self, "加载失败", f"加载学生数据失败: {str(e)}")

    def search_students(self):
        """搜索学生"""
        keyword = self.search_edit.text().strip()
        if not keyword:
            self.load_students()
            return
        try:
            # 使用学生页下拉选择的课程
            course_id = None
            if hasattr(self, 'students_course_combo') and self.students_course_combo.count() > 0:
                idx = self.students_course_combo.currentIndex()
                if idx >= 0:
                    course_id = self.students_course_combo.itemData(idx)
            if course_id is None:
                courses_response = client.get_my_courses()
                if courses_response.get('success') and courses_response.get('courses'):
                    first_course = courses_response.get('courses')[0]
                    course_id = first_course.get('id')
                else:
                    teacher = Teacher.get_teacher_by_user_id(self.user_info.get('id'))
                    if teacher:
                        local_courses = Course.get_courses_by_teacher_id(teacher.get('id')) or []
                        if local_courses:
                            course_id = local_courses[0].get('id')
            if course_id is None:
                QMessageBox.information(self, "提示", "没有可用课程")
                return
            # 获取该课程的学生列表
            response = client.get_course_students(course_id)
            if response.get('success'):
                students = response.get('students', [])
            else:
                students = Enrollment.get_students_by_course(course_id) or []
            # 筛选包含关键词的学生
            filtered_students = []
            kw = keyword.lower()
            for s in students:
                student_id = str(s.get('student_id', '')).lower()
                student_name = str(s.get('name', '')).lower()
                if kw in student_id or kw in student_name:
                    filtered_students.append(s)
            # 清空表格并填充
            self.students_table.setRowCount(0)
            for s in filtered_students:
                row = self.students_table.rowCount()
                self.students_table.insertRow(row)
                # 学生ID - 确保格式正确
                student_id = s.get('student_id', '')
                # 确保学生ID是字符串类型
                formatted_id = str(student_id)
                self.students_table.setItem(row, 0, QTableWidgetItem(formatted_id))
                self.students_table.setItem(row, 1, QTableWidgetItem(s.get('name', '')))
                self.students_table.setItem(row, 2, QTableWidgetItem(s.get('gender', '')))
                age_text = ''
                try:
                    birth_val = s.get('birth')
                    if birth_val:
                        from datetime import datetime, date
                        if isinstance(birth_val, str):
                            birth_date = datetime.strptime(birth_val, '%Y-%m-%d').date()
                        elif isinstance(birth_val, date):
                            birth_date = birth_val
                        else:
                            birth_date = None
                        if birth_date:
                            today = date.today()
                            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                            age_text = str(age)
                except Exception:
                    age_text = ''
                self.students_table.setItem(row, 3, QTableWidgetItem(age_text))
                self.students_table.setItem(row, 4, QTableWidgetItem(s.get('major', '')))
                self.students_table.setItem(row, 5, QTableWidgetItem(s.get('class', '')))
                # 操作列（删除按钮）
                delete_button = QPushButton("删除")
                delete_button.clicked.connect(lambda checked, student_id=s.get('id'), student_name=s.get('name', ''): self.delete_student(student_id, student_name))
                self.students_table.setCellWidget(row, 6, delete_button)
                self.students_table.resizeColumnsToContents()
        except Exception as e:
            logger.error(f"搜索学生失败: {e}")
            QMessageBox.critical(self, "错误", f"搜索学生失败: {str(e)}")
    
    def edit_score(self, row, score_id):
        """编辑成绩"""
        try:
            # 验证score_id是否有效
            if score_id is None:
                QMessageBox.warning(self, "编辑失败", "无法获取成绩ID，无法编辑")
                return
                
            # 从表格中获取当前分数
            score_item = self.scores_table.item(row, 2)
            if not score_item:
                QMessageBox.warning(self, "提示", "未找到该行的成绩数据")
                return
            text = score_item.text().strip()
            # 基础校验
            try:
                new_score = float(text)
            except ValueError:
                QMessageBox.warning(self, "输入错误", "成绩必须是数字")
                return
            if new_score < 0 or new_score > 100:
                QMessageBox.warning(self, "输入错误", "成绩范围应在0到100之间")
                return

            # 发送更新请求
            logger.info(f"尝试更新成绩: score_id={score_id}, new_score={new_score}")
            # 添加额外的调试信息
            logger.debug(f"当前行: {row}, 当前用户: {self.user_info.get('username')}")
            
            # 直接调用模型层进行本地更新，避免网络问题
            try:
                # 首先导入必要的模型
                from models.scores import Score
                
                # 确保score_id是整数类型
                try:
                    score_id_int = int(score_id)
                except ValueError:
                    logger.error(f"成绩ID格式错误: {score_id}")
                    QMessageBox.warning(self, "编辑失败", "成绩ID格式错误")
                    return
                
                # 直接更新成绩
                success = Score.update_score_by_id(score_id_int, score=new_score)
                
                if success:
                    QMessageBox.information(self, "成功", "成绩已更新")
                    # 刷新当前列表和统计
                    self.query_scores()
                else:
                    # 如果本地更新失败，尝试通过网络客户端更新
                    logger.warning("本地更新失败，尝试通过网络客户端更新...")
                    # 使用相同的整数类型score_id
                    resp = client.update_score(score_id_int, score=new_score)
                    logger.info(f"客户端更新响应: {resp}")
                    
                    if resp and resp.get('success'):
                        QMessageBox.information(self, "成功", "成绩已更新")
                        self.query_scores()
                    else:
                        error_message = resp.get('message', '更新失败') if resp else '未知错误'
                        logger.error(f"客户端更新失败: {error_message}")
                        QMessageBox.warning(self, "失败", f"{error_message}\n\n请检查网络连接或联系管理员")
            except Exception as e:
                logger.error(f"直接更新成绩时出错: {e}")
                # 回退到原来的客户端更新方式
                # 确保使用整数类型的score_id
                try:
                    score_id_int = int(score_id)
                except ValueError:
                    logger.error(f"成绩ID格式错误: {score_id}")
                    QMessageBox.warning(self, "编辑失败", "成绩ID格式错误")
                    return
                resp = client.update_score(score_id_int, score=new_score)
                if resp and resp.get('success'):
                    QMessageBox.information(self, "成功", "成绩已更新")
                    self.query_scores()
                else:
                    error_message = resp.get('message', '更新失败') if resp else '未知错误'
                    QMessageBox.warning(self, "失败", f"{error_message}\n\n{str(e)}")
        except Exception as e:
            logger.error(f"编辑成绩失败: {e}")
            QMessageBox.critical(self, "错误", f"编辑成绩失败: {str(e)}")
    
    def delete_student(self, student_id, student_name):
        """删除学生"""
        try:
            # 显示确认对话框
            reply = QMessageBox.question(
                self, '确认删除', f'确定要删除学生 {student_name} 吗？',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 获取当前选择的课程ID和学期
                course_id = None
                semester = None
                
                if hasattr(self, 'students_course_combo') and self.students_course_combo.count() > 0:
                    idx = self.students_course_combo.currentIndex()
                    if idx >= 0:
                        course_id = self.students_course_combo.itemData(idx)
                
                # 获取当前学期（从课程信息中获取）
                if course_id:
                    # 获取当前课程信息
                    try:
                        response = client.get_course_details(course_id)
                        if response.get('success'):
                            course_details = response.get('courses', [{}])[0]
                            semester = course_details.get('semester', '')
                    except:
                        # 如果无法从服务器获取，尝试从本地数据库获取
                        course = Course.get_course_by_id(course_id)
                        if course:
                            semester = course.get('semester', '')
                
                if not semester:
                    # 如果还是没有学期信息，使用当前年份的学期
                    from datetime import datetime
                    current_year = datetime.now().year
                    current_month = datetime.now().month
                    if current_month <= 6:
                        semester = f'{current_year-1}-{current_year} 第二学期'
                    else:
                        semester = f'{current_year}-{current_year+1} 第一学期'
                
                if course_id:
                    # 使用学生退课功能来实现删除学生
                    response = client.unenroll_course(course_id, semester)
                    
                    if response.get('success'):
                        QMessageBox.information(self, '成功', f'学生 {student_name} 已从课程中删除')
                        self.load_students()  # 重新加载学生列表
                    else:
                        # 本地回退：使用Enrollment.unenroll方法删除选课记录
                        try:
                            from models.enrollment import Enrollment
                            # 注意：unenroll方法需要的是学生内部ID，而不是传入的student_id
                            # 这里假设传入的student_id已经是内部ID
                            success = Enrollment.unenroll(student_id, course_id, semester)
                            if success:
                                QMessageBox.information(self, '成功', f'学生 {student_name} 已从课程中删除')
                                self.load_students()  # 重新加载学生列表
                            else:
                                QMessageBox.warning(self, '失败', f'删除学生失败: {response.get("message", "未知错误")}')
                        except Exception as e:
                            logger.error(f"本地删除学生失败: {e}")
                            QMessageBox.warning(self, '失败', f'删除学生失败: {str(e)}')
                else:
                    QMessageBox.warning(self, '失败', '无法获取当前课程信息')
        except Exception as e:
            logger.error(f"删除学生时发生错误: {e}")
            QMessageBox.critical(self, '错误', f'删除学生时发生错误: {str(e)}')

    def update_charts(self, scores):
        """更新数据可视化图表"""
        # 更新成绩分布图表
        if hasattr(self, 'score_distribution_canvas'):
            self.score_distribution_canvas.update_chart(scores)
        
        # 更新课程对比图表（这里简化处理，实际可能需要更多数据）
        if hasattr(self, 'course_comparison_canvas'):
            self.course_comparison_canvas.update_chart(scores)
    
    def switch_page(self, page_name):
        """切换页面"""
        if page_name == 'profile':
            self.tab_widget.setCurrentWidget(self.profile_widget)
            self.load_teacher_info()  # 切换到个人信息标签页时加载教师信息
        elif page_name == 'courses':
            self.tab_widget.setCurrentWidget(self.courses_widget)
            self.load_courses()  # 切换到我的课程标签页时加载课程信息
        elif page_name == 'scores':
            self.tab_widget.setCurrentWidget(self.scores_widget)
            self.load_courses()  # 切换到成绩管理标签页时加载课程信息
        elif page_name == 'students':
            self.tab_widget.setCurrentWidget(self.students_widget)
            self.load_students()  # 切换到学生管理标签页时加载学生数据
        elif page_name == 'analysis':
            self.tab_widget.setCurrentWidget(self.analysis_widget)
            self.load_analysis_courses()  # 切换到数据分析标签页时加载课程列表
    
    def refresh(self):
        """刷新数据"""
        # 重新加载数据
        self.load_teacher_info()
        self.load_courses()
        # 如果当前在成绩管理标签页，重新查询成绩
        if self.tab_widget.currentWidget() == self.scores_widget:
            self.query_scores()
    
    def import_scores(self):
        """批量导入成绩"""
        # 获取当前选择的课程和学期
        current_course_index = self.course_combo.currentIndex()
        current_semester_index = self.semester_combo.currentIndex()
        
        if current_course_index < 0 or current_semester_index < 0:
            QMessageBox.warning(self, "警告", "请先选择课程和学期")
            return
        
        # 获取课程ID和学期
        course_id = self.course_combo.itemData(current_course_index)
        semester = self.semester_combo.currentText()
        
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 验证数据格式
            required_columns = ['学生ID', '学生姓名', '成绩']
            for col in required_columns:
                if col not in df.columns:
                    QMessageBox.critical(self, "错误", f"Excel文件缺少必要的列: {col}")
                    return
            
            # 导入成绩
            success_count = 0
            fail_count = 0
            fail_students = []
            
            for _, row in df.iterrows():
                student_no = row['学生ID']  # 这里是学号，不是内部ID
                score = row['成绩']
                
                # 验证成绩是否为数字且在0-100之间
                try:
                    score = float(score)
                    if not 0 <= score <= 100:
                        fail_count += 1
                        fail_students.append(f"{student_no}: 成绩必须在0-100之间")
                        continue
                except:
                    fail_count += 1
                    fail_students.append(f"{student_no}: 成绩格式无效")
                    continue
                
                # 根据学号获取学生内部ID
                student_info = Student.get_student_by_id(student_no)
                if not student_info:
                    fail_count += 1
                    fail_students.append(f"{student_no}: 学号不存在")
                    continue
                
                student_id = student_info.get('id')  # 获取内部ID
                
                # 调用client方法更新成绩
                result = client.update_score_by_student_course(student_id=student_id, course_id=course_id, semester=semester, score=score)
                
                if result.get('success'):
                    success_count += 1
                else:
                    fail_count += 1
                    fail_students.append(f"{student_no}: {result.get('message', '更新失败')}")
            
            # 显示导入结果
            message = f"导入完成！成功: {success_count}, 失败: {fail_count}\n"
            if fail_count > 0:
                message += "失败列表:\n" + "\n".join(fail_students[:10])
                if fail_count > 10:
                    message += f"\n... 还有{fail_count - 10}条失败记录"
            
            QMessageBox.information(self, "导入结果", message)
            
            # 重新查询成绩
            self.query_scores()
            
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"导入成绩时发生错误: {str(e)}")
    
    def export_scores(self):
        """批量导出成绩"""
        # 获取当前选择的课程和学期
        current_course_index = self.course_combo.currentIndex()
        current_semester_index = self.semester_combo.currentIndex()
        
        if current_course_index < 0 or current_semester_index < 0:
            QMessageBox.warning(self, "警告", "请先选择课程和学期")
            return
        
        # 获取课程ID和学期
        course_id = self.course_combo.itemData(current_course_index)
        course_name = self.course_combo.currentText()
        semester = self.semester_combo.currentText()
        
        # 调用client方法获取成绩数据
        response = client.get_course_scores(course_id=course_id, semester=semester)
        
        if not response.get('success'):
            QMessageBox.critical(self, "错误", f"获取成绩数据失败: {response.get('message', '')}")
            return
        
        scores = response.get('scores', [])
        
        if not scores:
            QMessageBox.information(self, "提示", "当前选择的课程和学期没有成绩数据")
            return
        
        # 创建保存文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存Excel文件", f"{course_name}_{semester}_成绩.xlsx", "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # 准备数据
            data = []
            students_map = {}
            
            for score in scores:
                student_internal_id = score.get('student_id')
                
                # 缓存学生信息，避免重复查询
                if student_internal_id not in students_map:
                    student_info = Student.get_student_by_internal_id(student_internal_id)
                    if student_info:
                        students_map[student_internal_id] = student_info
                
                student_info = students_map.get(student_internal_id, {})
                student_no = student_info.get('student_id', '')  # 获取学号
                
                data.append({
                    '学生ID': student_no,  # 显示学号而不是内部ID
                    '学生姓名': score.get('student_name', ''),
                    '成绩': score.get('score', ''),
                    '学分': score.get('credits', '')
                })
            
            # 创建DataFrame并导出到Excel
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            
            QMessageBox.information(self, "导出成功", f"成绩数据已成功导出到:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出成绩时发生错误: {str(e)}")


class ScoreDistributionCanvas(FigureCanvas):
    """成绩分布图表画布"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """初始化成绩分布图表"""
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # 初始化图表
        self.axes = self.fig.add_subplot(111)
        self.axes.set_title('成绩分布图')
        self.axes.set_xlabel('分数段')
        self.axes.set_ylabel('学生数量')
        
        # 初始绘制
        self.update_chart([])
    
    def update_chart(self, scores):
        """更新成绩分布图表"""
        # 清空图表
        self.axes.clear()
        
        # 提取分数
        score_values = [score.get('score', 0) for score in scores]
        
        # 定义分数段
        bins = [0, 60, 70, 80, 90, 101]
        labels = ['0-59', '60-69', '70-79', '80-89', '90-100']
        
        # 计算各分数段的学生数量
        hist, _ = np.histogram(score_values, bins=bins)
        
        # 绘制柱状图
        self.axes.bar(labels, hist, color='lightgreen')
        
        # 设置图表属性
        self.axes.set_title('成绩分布图')
        self.axes.set_xlabel('分数段')
        self.axes.set_ylabel('学生数量')
        self.axes.grid(True, linestyle='--', alpha=0.7)
        
        # 调整布局
        self.fig.tight_layout()
        
        # 刷新画布
        self.draw()


class CourseComparisonCanvas(FigureCanvas):
    """课程对比图表画布"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """初始化课程对比图表"""
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # 初始化图表
        self.axes = self.fig.add_subplot(111)
        self.axes.set_title('各课程成绩对比')
        self.axes.set_xlabel('课程')
        self.axes.set_ylabel('平均分')
        
        # 初始绘制
        self.update_chart([])
    
    def update_chart(self, scores):
        """更新课程对比图表"""
        # 清空图表
        self.axes.clear()
        
        # 这里简化处理，实际可能需要从其他地方获取更多课程的数据
        # 为了演示，我们只使用当前查询的课程数据
        if scores:
            # 提取当前课程信息
            course_name = scores[0].get('course_name', '当前课程')
            # 计算平均分
            avg_score = sum([score.get('score', 0) for score in scores]) / len(scores)
            
            # 绘制柱状图（这里简化处理，只显示当前课程的平均分）
            self.axes.bar(course_name, avg_score, color='lightblue')
        
        # 设置图表属性
        self.axes.set_title('各课程成绩对比')
        self.axes.set_xlabel('课程')
        self.axes.set_ylabel('平均分')
        self.axes.set_ylim(0, 100)
        self.axes.grid(True, linestyle='--', alpha=0.7)
        
        # 调整布局
        self.fig.tight_layout()
        
        # 刷新画布
        self.draw()


# 测试代码
if __name__ == '__main__':
    # 这里只是为了测试
    test_user_info = {
        'id': 2,
        'username': 'teacher1',
        'role': 'teacher',
        'name': '李老师'
    }
    
    app = QApplication(sys.argv)
    dashboard = TeacherDashboard(test_user_info)
    dashboard.show()
    sys.exit(app.exec_())