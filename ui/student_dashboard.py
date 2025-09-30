#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""学生仪表盘模块"""

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
    QTableWidgetItem, QTabWidget, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from network.client import client
from models.student import Student
from models.scores import Score
import utils.data_visualization
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QTabWidget, QFrame, QMessageBox,
    QPushButton, QLineEdit, QFormLayout, QDialog, QDialogButtonBox, QComboBox, QDateEdit
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('student_dashboard')


class DataLoadingThread(QThread):
    """数据加载线程，用于在后台加载学生数据，避免阻塞GUI主线程"""
    # 定义信号
    data_loaded = pyqtSignal(dict)
    load_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        """在线程中执行数据加载操作"""
        try:
            result = {
                'student_info': None,
                'scores': None,
                'courses': None
            }
            
            # 获取学生信息
            student_response = client.get_student_info()
            if student_response.get('success'):
                result['student_info'] = student_response.get('student')
            
            # 获取学生成绩
            scores_response = client.get_my_scores()
            if scores_response.get('success'):
                result['scores'] = scores_response.get('scores', [])
                result['gpa'] = scores_response.get('gpa', 0.0)
            
            # 获取学生课程详情
            courses_response = client.get_student_courses()
            if courses_response.get('success'):
                result['courses'] = courses_response.get('courses', [])
            else:
                # 如果获取课程详情失败，则从成绩中提取课程信息
                result['courses'] = result['scores']
            
            # 发送数据加载完成信号
            self.data_loaded.emit(result)
        except Exception as e:
            logger.error(f"数据加载失败: {e}")
            self.load_error.emit(str(e))


class StudentDashboard(QWidget):
    """学生仪表盘类"""
    
    def __init__(self, user_info):
        """初始化学生仪表盘"""
        super().__init__()
        
        # 保存用户信息
        self.user_info = user_info
        self.student_id = None
        self.current_student_info = None
        
        # 初始化UI
        self.init_ui()
        
        # 使用线程在后台加载数据，避免阻塞主线程
        self.start_data_loading()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 创建个人信息标签页
        self.create_profile_tab()
        
        # 创建成绩标签页
        self.create_scores_tab()
        
        # 创建课程标签页
        self.create_courses_tab()
        
        # 创建数据分析标签页
        self.create_analysis_tab()
        
        # 添加标签页到标签部件
        self.tab_widget.addTab(self.profile_widget, "个人信息")
        self.tab_widget.addTab(self.scores_widget, "我的成绩")
        self.tab_widget.addTab(self.courses_widget, "我的课程")
        self.tab_widget.addTab(self.analysis_widget, "成绩分析")
        
        # 添加标签部件到主布局
        main_layout.addWidget(self.tab_widget)
    
    def start_data_loading(self):
        """启动数据加载线程"""
        # 创建数据加载线程
        self.loading_thread = DataLoadingThread()
        
        # 连接信号和槽
        self.loading_thread.data_loaded.connect(self.on_data_loaded)
        self.loading_thread.load_error.connect(self.on_data_load_error)
        
        # 启动线程
        self.loading_thread.start()
    
    def on_data_loaded(self, result):
        """处理数据加载完成事件"""
        # 更新UI显示
        if result.get('student_info'):
            self.update_student_info(result['student_info'])
            
        if result.get('scores') is not None:
            self.update_scores(result['scores'], result.get('gpa', 0.0))
            
        if result.get('courses'):
            self.update_courses(result['courses'])
    
    def on_data_load_error(self, error_message):
        """处理数据加载错误事件"""
        logger.error(f"数据加载失败: {error_message}")
        QMessageBox.warning(self, "加载失败", f"数据加载失败: {error_message}")
    
    def update_student_info(self, student):
        """更新学生信息显示"""
        if student:
            self.current_student_info = student
            self.student_id = student.get('student_id')
            
            # 计算年龄（根据 birth 字段）
            age_text = ''
            try:
                birth_val = student.get('birth')
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
            
            # 更新界面显示（按后端实际字段映射）
            self.student_id_label.setText(f"学生ID: {student.get('student_id', '')}")
            self.name_label.setText(f"姓名: {student.get('name', '')}")
            self.gender_label.setText(f"性别: {student.get('gender', '')}")
            self.age_label.setText(f"年龄: {age_text}")
            self.major_label.setText(f"专业: {student.get('major', '')}")
            self.class_label.setText(f"班级: {student.get('class', '')}")
            # 系统未提供入学年份字段，这里留空
            self.admission_year_label.setText(f"入学年份: ")
    
    def update_scores(self, scores, gpa):
        """更新成绩显示"""
        # 更新GPA显示
        self.gpa_value_label.setText(f"{gpa:.2f}")
        
        # 清空表格
        self.scores_table.setRowCount(0)
        
        # 填充表格
        for score_info in scores:
            row_position = self.scores_table.rowCount()
            self.scores_table.insertRow(row_position)
            
            # 设置表格数据
            self.scores_table.setItem(row_position, 0, QTableWidgetItem(score_info.get('course_code', '')))
            self.scores_table.setItem(row_position, 1, QTableWidgetItem(score_info.get('course_name', '')))
            self.scores_table.setItem(row_position, 2, QTableWidgetItem(str(score_info.get('credits', ''))))
            self.scores_table.setItem(row_position, 3, QTableWidgetItem(str(score_info.get('score', ''))))
            self.scores_table.setItem(row_position, 4, QTableWidgetItem(score_info.get('semester', '')))
            self.scores_table.setItem(row_position, 5, QTableWidgetItem(score_info.get('teacher_name', '')))
        
        # 调整表格列宽
        self.scores_table.resizeColumnsToContents()
        
        # 更新图表
        self.update_charts(scores)
    
    def update_courses(self, courses):
        """更新课程显示"""
        # 清空表格
        self.courses_table.setRowCount(0)
        
        # 填充表格（从成绩中提取课程信息）
        for course_info in courses:
            row_position = self.courses_table.rowCount()
            self.courses_table.insertRow(row_position)
            
            # 设置表格数据
            self.courses_table.setItem(row_position, 0, QTableWidgetItem(course_info.get('course_code', '')))
            self.courses_table.setItem(row_position, 1, QTableWidgetItem(course_info.get('course_name', '')))
            self.courses_table.setItem(row_position, 2, QTableWidgetItem(str(course_info.get('credits', ''))))
            self.courses_table.setItem(row_position, 3, QTableWidgetItem(course_info.get('teacher_name', '')))
            # 从课程数据中获取上课时间和地点
            self.courses_table.setItem(row_position, 4, QTableWidgetItem(course_info.get('class_time', '') or "待定"))
            self.courses_table.setItem(row_position, 5, QTableWidgetItem(course_info.get('class_room', '') or "待定"))
            
            # 添加退课按钮
            drop_btn = QPushButton("退课")
            drop_btn.setStyleSheet(
                "QPushButton { background-color: #f44336; color: white; border-radius: 3px; padding: 3px 10px; }"
                "QPushButton:hover { background-color: #da190b; }"
            )
            # 使用lambda捕获course_info
            drop_btn.clicked.connect(lambda checked, c=course_info: self.drop_course(c))
            self.courses_table.setCellWidget(row_position, 6, drop_btn)
        
        # 调整表格列宽
        self.courses_table.resizeColumnsToContents()
        
        # 同时更新课程表
        self.update_schedule(courses)
    
    def create_profile_tab(self):
        """创建个人信息标签页"""
        self.profile_widget = QWidget()
        profile_layout = QVBoxLayout(self.profile_widget)
        
        # 创建个人信息组框
        profile_group = QFrame()
        profile_group.setFrameShape(QFrame.StyledPanel)
        profile_group.setStyleSheet("QFrame { background-color: #f0f0f0; border-radius: 10px; padding: 10px; }")
        profile_form_layout = QVBoxLayout(profile_group)
        
        # 学生ID
        self.student_id_label = QLabel("学生ID: ")
        profile_form_layout.addWidget(self.student_id_label)
        
        # 姓名
        self.name_label = QLabel("姓名: ")
        profile_form_layout.addWidget(self.name_label)
        
        # 性别
        self.gender_label = QLabel("性别: ")
        profile_form_layout.addWidget(self.gender_label)
        
        # 年龄
        self.age_label = QLabel("年龄: ")
        profile_form_layout.addWidget(self.age_label)
        
        # 专业
        self.major_label = QLabel("专业: ")
        profile_form_layout.addWidget(self.major_label)
        
        # 班级
        self.class_label = QLabel("班级: ")
        profile_form_layout.addWidget(self.class_label)
        
        # 入学年份
        self.admission_year_label = QLabel("入学年份: ")
        profile_form_layout.addWidget(self.admission_year_label)
        
        # 操作按钮区：修改信息
        buttons_layout = QHBoxLayout()
        self.edit_info_button = QPushButton("修改信息")
        self.edit_info_button.clicked.connect(self.open_edit_dialog)
        buttons_layout.addWidget(self.edit_info_button)
        
        self.change_pwd_button = QPushButton("修改密码")
        self.change_pwd_button.clicked.connect(self.open_change_password_dialog)
        buttons_layout.addWidget(self.change_pwd_button)
        
        buttons_layout.addStretch()
        profile_form_layout.addLayout(buttons_layout)
        
        # 添加个人信息组框到布局
        profile_layout.addWidget(profile_group)
    
    def create_scores_tab(self):
        """创建成绩标签页"""
        self.scores_widget = QWidget()
        scores_layout = QVBoxLayout(self.scores_widget)
        
        # 创建成绩表格
        self.scores_table = QTableWidget()
        self.scores_table.setColumnCount(6)
        self.scores_table.setHorizontalHeaderLabels(["课程代码", "课程名称", "学分", "成绩", "学期", "教师"])
        
        # 设置表格样式
        self.scores_table.horizontalHeader().setStretchLastSection(True)
        
        # 添加成绩表格到布局
        scores_layout.addWidget(self.scores_table)
        
        # 添加GPA显示
        gpa_layout = QHBoxLayout()
        gpa_label = QLabel("GPA: ")
        self.gpa_value_label = QLabel("0.0")
        gpa_value_font = QFont()
        gpa_value_font.setPointSize(14)
        gpa_value_font.setBold(True)
        self.gpa_value_label.setFont(gpa_value_font)
        self.gpa_value_label.setStyleSheet("color: blue;")
        gpa_layout.addWidget(gpa_label)
        gpa_layout.addWidget(self.gpa_value_label)
        gpa_layout.addStretch()
        scores_layout.addLayout(gpa_layout)
    
    def create_courses_tab(self):
        """创建课程标签页"""
        self.courses_widget = QWidget()
        courses_layout = QVBoxLayout(self.courses_widget)
        
        # 添加标题和操作按钮
        header_layout = QHBoxLayout()
        courses_title = QLabel("我的课程")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        courses_title.setFont(title_font)
        header_layout.addWidget(courses_title)
        header_layout.addStretch()
        
        # 添加选课按钮
        self.select_course_button = QPushButton("选课")
        self.select_course_button.setMinimumHeight(35)
        self.select_course_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 5px; padding: 5px 15px; font-weight: bold; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.select_course_button.clicked.connect(self.open_course_selection_dialog)
        header_layout.addWidget(self.select_course_button)
        
        courses_layout.addLayout(header_layout)
        
        # 创建子标签页（课程列表和课程表）
        self.courses_tab_widget = QTabWidget()
        
        # 课程列表标签页
        course_list_widget = QWidget()
        course_list_layout = QVBoxLayout(course_list_widget)
        
        # 创建课程表格
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(7)
        self.courses_table.setHorizontalHeaderLabels(["课程代码", "课程名称", "学分", "教师", "上课时间", "上课地点", "操作"])
        
        # 设置表格样式
        self.courses_table.horizontalHeader().setStretchLastSection(True)
        
        # 添加课程表格到布局
        course_list_layout.addWidget(self.courses_table)
        
        # 课程表标签页
        self.schedule_widget = QWidget()
        schedule_layout = QVBoxLayout(self.schedule_widget)
        
        # 创建课程表
        self.create_schedule_table()
        schedule_layout.addWidget(self.schedule_table)
        
        # 添加说明文字
        schedule_note = QLabel("💡 提示：课程表显示您已选课程的时间安排")
        schedule_note.setStyleSheet("color: #666; padding: 5px; font-size: 12px;")
        schedule_layout.addWidget(schedule_note)
        
        # 将两个子标签页添加到标签控件
        self.courses_tab_widget.addTab(course_list_widget, "📋 课程列表")
        self.courses_tab_widget.addTab(self.schedule_widget, "📅 课程表")
        
        # 添加标签控件到主布局
        courses_layout.addWidget(self.courses_tab_widget)
    
    def create_schedule_table(self):
        """创建课程表"""
        # 定义时间段和对应的时间
        self.time_slots = [
            ("08:00-09:40", "第1-2节"),
            ("10:00-11:40", "第3-4节"),
            ("14:00-15:40", "第5-6节"),
            ("16:00-17:40", "第7-8节"),
            ("19:00-20:40", "第9-10节")
        ]
        
        # 定义星期
        self.weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        # 创建课程表表格
        self.schedule_table = QTableWidget()
        self.schedule_table.setRowCount(len(self.time_slots))
        self.schedule_table.setColumnCount(len(self.weekdays) + 1)  # +1 for time column
        
        # 设置表头
        headers = ["时间"] + self.weekdays
        self.schedule_table.setHorizontalHeaderLabels(headers)
        
        # 设置时间列
        for i, (time_range, period) in enumerate(self.time_slots):
            time_item = QTableWidgetItem(f"{period}\n{time_range}")
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setFont(QFont("Arial", 9))
            time_item.setBackground(Qt.lightGray)
            self.schedule_table.setItem(i, 0, time_item)
        
        # 设置表格属性
        self.schedule_table.horizontalHeader().setStretchLastSection(True)
        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 连接单元格点击事件
        self.schedule_table.itemClicked.connect(self.on_schedule_cell_clicked)
        
        # 设置行高和列宽
        for i in range(len(self.time_slots)):
            self.schedule_table.setRowHeight(i, 80)
        
        self.schedule_table.setColumnWidth(0, 120)  # 时间列宽度
        for i in range(1, len(self.weekdays) + 1):
            self.schedule_table.setColumnWidth(i, 150)
        
        # 设置表格样式
        self.schedule_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                border: 1px solid #c0c0c0;
            }
            QTableWidget::item {
                padding: 5px;
                border: 1px solid #e0e0e0;
            }
            QTableWidget::item:hover {
                border: 2px solid #2196F3;
                cursor: pointer;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
    
    def update_schedule(self, courses):
        """更新课程表显示"""
        # 清空所有课程单元格
        for row in range(len(self.time_slots)):
            for col in range(1, len(self.weekdays) + 1):
                self.schedule_table.setItem(row, col, QTableWidgetItem(""))
        
        # 定义颜色列表（用于不同课程）
        colors = [
            "#FFE5E5", "#E5F5FF", "#E5FFE5", "#FFF5E5", "#F5E5FF",
            "#FFE5F5", "#E5FFFF", "#FFFFE5", "#FFE5CC", "#E5E5FF"
        ]
        
        # 解析并填充课程信息
        for idx, course in enumerate(courses):
            class_time = course.get('class_time', '')
            if not class_time:
                continue
            
            # 解析时间信息（格式：周X HH:MM-HH:MM）
            parsed = self.parse_course_time(class_time)
            if not parsed:
                continue
            
            weekday, time_range = parsed
            
            # 找到对应的列
            try:
                col_index = self.weekdays.index(weekday) + 1
            except ValueError:
                continue
            
            # 找到对应的行
            row_index = self.find_time_slot(time_range)
            if row_index == -1:
                continue
            
            # 创建课程单元格内容
            course_name = course.get('course_name', '')
            teacher_name = course.get('teacher_name', '')
            class_location = course.get('class_room', '') or course.get('class_location', '')
            
            # 组合显示内容
            display_text = f"{course_name}\n"
            if teacher_name:
                display_text += f"{teacher_name}\n"
            if class_location:
                display_text += f"{class_location}"
            
            # 创建单元格项
            cell_item = QTableWidgetItem(display_text)
            cell_item.setTextAlignment(Qt.AlignCenter)
            
            # 设置背景颜色
            color_index = idx % len(colors)
            from PyQt5.QtGui import QColor
            cell_item.setBackground(QColor(colors[color_index]))
            
            # 设置字体
            font = QFont()
            font.setBold(True)
            font.setPointSize(9)
            cell_item.setFont(font)
            
            # 存储完整的课程信息到单元格（使用 UserRole）
            cell_item.setData(Qt.UserRole, course)
            
            # 设置提示文本
            cell_item.setToolTip(f"点击查看《{course_name}》的详细信息")
            
            # 设置鼠标悬停样式（通过单元格样式）
            cell_item.setFlags(cell_item.flags() | Qt.ItemIsEnabled)
            
            # 设置到表格
            self.schedule_table.setItem(row_index, col_index, cell_item)
    
    def parse_course_time(self, time_str):
        """
        解析课程时间字符串
        输入格式: "周一 10:00-11:40"
        返回: (weekday, time_range) 或 None
        """
        try:
            if not time_str:
                return None
            
            parts = time_str.strip().split()
            if len(parts) < 2:
                return None
            
            weekday = parts[0]  # 周几
            time_range = parts[1]  # 时间段
            
            return (weekday, time_range)
        except:
            return None
    
    def find_time_slot(self, time_range):
        """
        根据时间段找到对应的行索引
        输入格式: "10:00-11:40"
        返回: 行索引 或 -1
        """
        for i, (slot_time, _) in enumerate(self.time_slots):
            if time_range == slot_time:
                return i
        
        # 如果没有完全匹配，尝试模糊匹配（检查开始时间）
        try:
            input_start = time_range.split('-')[0]
            for i, (slot_time, _) in enumerate(self.time_slots):
                slot_start = slot_time.split('-')[0]
                if input_start == slot_start:
                    return i
        except:
            pass
        
        return -1
    
    def on_schedule_cell_clicked(self, item):
        """处理课程表单元格点击事件"""
        # 获取存储在单元格中的课程数据
        course_data = item.data(Qt.UserRole)
        
        # 如果没有课程数据（空单元格或时间列），不做处理
        if not course_data:
            return
        
        # 显示课程详情对话框
        dialog = CourseDetailDialog(course_data, self)
        dialog.exec_()
    
    def create_analysis_tab(self):
        """创建数据分析标签页"""
        self.analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(self.analysis_widget)
        
        # 创建图表
        self.create_charts()
        
        # 创建图表布局
        charts_layout = QHBoxLayout()
        charts_layout.addWidget(self.score_distribution_widget)
        charts_layout.addWidget(self.semester_comparison_widget)
        
        # 添加图表布局到主布局
        analysis_layout.addLayout(charts_layout)
    
    def create_charts(self):
        """创建数据可视化图表"""
        # 成绩分布图表
        self.score_distribution_widget = QWidget()
        score_distribution_layout = QVBoxLayout(self.score_distribution_widget)
        
        # 创建成绩分布标题
        score_distribution_title = QLabel("成绩分布")
        score_distribution_title.setAlignment(Qt.AlignCenter)
        score_distribution_title.setStyleSheet("font-weight: bold;")
        score_distribution_layout.addWidget(score_distribution_title)
        
        # 创建成绩分布图表
        self.score_distribution_canvas = ScoreDistributionCanvas(self)
        score_distribution_layout.addWidget(self.score_distribution_canvas)
        
        # 学期成绩对比图表
        self.semester_comparison_widget = QWidget()
        semester_comparison_layout = QVBoxLayout(self.semester_comparison_widget)
        
        # 创建学期成绩对比标题
        semester_comparison_title = QLabel("学期成绩对比")
        semester_comparison_title.setAlignment(Qt.AlignCenter)
        semester_comparison_title.setStyleSheet("font-weight: bold;")
        semester_comparison_layout.addWidget(semester_comparison_title)
        
        # 创建学期成绩对比图表
        self.semester_comparison_canvas = SemesterComparisonCanvas(self)
        semester_comparison_layout.addWidget(self.semester_comparison_canvas)
    
    def update_charts(self, scores):
        """更新数据可视化图表"""
        # 更新成绩分布图表
        if hasattr(self, 'score_distribution_canvas'):
            self.score_distribution_canvas.update_chart(scores)
        
        # 更新学期成绩对比图表
        if hasattr(self, 'semester_comparison_canvas'):
            self.semester_comparison_canvas.update_chart(scores)
    
    def switch_page(self, page_name):
        """切换页面"""
        # 根据页面名称切换标签页
        if page_name == 'profile':
            self.tab_widget.setCurrentWidget(self.profile_widget)
        elif page_name == 'scores':
            self.tab_widget.setCurrentWidget(self.scores_widget)
        elif page_name == 'courses':
            self.tab_widget.setCurrentWidget(self.courses_widget)
        elif page_name == 'analysis':
            self.tab_widget.setCurrentWidget(self.analysis_widget)
    
    def refresh(self):
        """刷新数据"""
        # 重新加载数据
        self.start_data_loading()

    def open_edit_dialog(self):
        """打开修改个人信息对话框"""
        if not self.current_student_info:
            QMessageBox.warning(self, "提示", "未获取到个人信息，稍后再试")
            return
        dialog = EditSelfStudentDialog(self.current_student_info, self)
        if dialog.exec_() == QDialog.Accepted:
            # 更新成功后刷新数据显示
            self.start_data_loading()
    
    def open_change_password_dialog(self):
        dialog = ChangePasswordDialog(self)
        dialog.exec_()
    
    def open_course_selection_dialog(self):
        """打开选课对话框"""
        # 获取当前学期（这里可以根据实际情况获取，暂时使用固定学期）
        # 从现有课程中提取学期信息，或使用默认值
        current_semester = "2025-2026-1"  # 默认学期
        
        dialog = CourseSelectionDialog(current_semester, self)
        if dialog.exec_() == QDialog.Accepted:
            # 刷新课程列表
            self.start_data_loading()
    
    def drop_course(self, course_info):
        """退课"""
        course_name = course_info.get('course_name', '未知课程')
        course_id = course_info.get('id')
        semester = course_info.get('semester')
        
        if not course_id or not semester:
            QMessageBox.warning(self, "退课失败", "课程信息不完整")
            return
        
        # 确认退课
        reply = QMessageBox.question(
            self, 
            "确认退课", 
            f"确定要退选《{course_name}》吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                response = client.unenroll_course(course_id, semester)
                if response.get('success'):
                    QMessageBox.information(self, "成功", "退课成功！")
                    # 刷新课程列表
                    self.start_data_loading()
                else:
                    QMessageBox.warning(self, "失败", response.get('message', '退课失败'))
            except Exception as e:
                QMessageBox.critical(self, "错误", f"退课失败: {str(e)}")


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
        self.axes.set_ylabel('课程数量')
        
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
        
        # 计算各分数段的课程数量
        hist, _ = np.histogram(score_values, bins=bins)
        
        # 绘制柱状图
        self.axes.bar(labels, hist, color='skyblue')
        
        # 设置图表属性
        self.axes.set_title('成绩分布图')
        self.axes.set_xlabel('分数段')
        self.axes.set_ylabel('课程数量')
        self.axes.grid(True, linestyle='--', alpha=0.7)
        
        # 调整布局
        self.fig.tight_layout()
        
        # 刷新画布
        self.draw()


class SemesterComparisonCanvas(FigureCanvas):
    """学期成绩对比图表画布"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """初始化学期成绩对比图表"""
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # 初始化图表
        self.axes = self.fig.add_subplot(111)
        self.axes.set_title('学期成绩对比')
        self.axes.set_xlabel('学期')
        self.axes.set_ylabel('平均成绩')
        
        # 初始绘制
        self.update_chart([])
    
    def update_chart(self, scores):
        """更新学期成绩对比图表"""
        # 清空图表
        self.axes.clear()
        
        # 按学期分组计算平均成绩
        semester_scores = {}
        for score in scores:
            semester = score.get('semester', '未知')
            score_value = score.get('score', 0)
            
            if semester not in semester_scores:
                semester_scores[semester] = []
            semester_scores[semester].append(score_value)
        
        # 计算每个学期的平均成绩
        semester_avg_scores = {}
        for semester, score_list in semester_scores.items():
            semester_avg_scores[semester] = sum(score_list) / len(score_list)
        
        # 排序学期
        sorted_semesters = sorted(semester_avg_scores.keys())
        sorted_avg_scores = [semester_avg_scores[semester] for semester in sorted_semesters]
        
        # 绘制折线图
        self.axes.plot(sorted_semesters, sorted_avg_scores, marker='o', color='blue')
        
        # 设置图表属性
        self.axes.set_title('学期成绩对比')
        self.axes.set_xlabel('学期')
        self.axes.set_ylabel('平均成绩')
        self.axes.set_ylim(0, 100)
        self.axes.grid(True, linestyle='--', alpha=0.7)
        
        # 调整布局
        self.fig.tight_layout()
        
        # 刷新画布
        self.draw()


class EditSelfStudentDialog(QDialog):
    """学生自助修改个人信息对话框"""
    def __init__(self, student_info: dict, parent=None):
        super().__init__(parent)
        self.student_info = student_info or {}
        self.setWindowTitle("修改个人信息")
        self.setMinimumWidth(420)
        self.init_ui()
        self.fill_form()
    
    def init_ui(self):
        self.form = QFormLayout(self)
        # 学号只读
        self.student_id_label = QLabel()
        self.form.addRow("学号:", self.student_id_label)
        # 姓名
        self.name_edit = QLineEdit()
        self.form.addRow("姓名:", self.name_edit)
        # 性别
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["", "男", "女"])
        self.form.addRow("性别:", self.gender_combo)
        # 出生日期
        self.birth_edit = QDateEdit()
        self.birth_edit.setCalendarPopup(True)
        self.form.addRow("出生日期:", self.birth_edit)
        # 班级
        self.class_edit = QLineEdit()
        self.form.addRow("班级:", self.class_edit)
        # 专业
        self.major_edit = QLineEdit()
        self.form.addRow("专业:", self.major_edit)
        # 按钮
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.on_submit)
        btns.rejected.connect(self.reject)
        self.form.addRow(btns)
    
    def fill_form(self):
        from PyQt5.QtCore import QDate
        self.student_id_label.setText(self.student_info.get('student_id', ''))
        self.name_edit.setText(self.student_info.get('name', ''))
        self.gender_combo.setCurrentText(self.student_info.get('gender', ''))
        birth = self.student_info.get('birth')
        if birth:
            try:
                parts = str(birth).split('-')
                if len(parts) == 3:
                    self.birth_edit.setDate(QDate(int(parts[0]), int(parts[1]), int(parts[2])))
            except Exception:
                pass
        self.class_edit.setText(self.student_info.get('class', ''))
        self.major_edit.setText(self.student_info.get('major', ''))
    
    def on_submit(self):
        name = self.name_edit.text().strip()
        gender = self.gender_combo.currentText()
        class_name = self.class_edit.text().strip()
        major = self.major_edit.text().strip()
        birth_str = self.birth_edit.date().toString('yyyy-MM-dd') if self.birth_edit.date().isValid() else None
        if not name:
            QMessageBox.warning(self, "输入错误", "姓名不能为空")
            return
        try:
            payload = {
                'name': name,
                'gender': gender,
                'birth': birth_str,
                'class': class_name,
                'major': major
            }
            resp = client.update_student_info(**payload)
            if resp.get('success'):
                QMessageBox.information(self, "更新成功", "个人信息已更新")
                self.accept()
            else:
                QMessageBox.warning(self, "更新失败", resp.get('message', '更新失败'))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新失败: {str(e)}")


class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改密码")
        self.setMinimumWidth(380)
        self.init_ui()
    
    def init_ui(self):
        self.form = QFormLayout(self)
        self.pwd_edit = QLineEdit()
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        self.form.addRow("新密码:", self.pwd_edit)
        self.pwd_confirm_edit = QLineEdit()
        self.pwd_confirm_edit.setEchoMode(QLineEdit.Password)
        self.form.addRow("确认密码:", self.pwd_confirm_edit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.on_submit)
        btns.rejected.connect(self.reject)
        self.form.addRow(btns)
    
    def on_submit(self):
        pwd = self.pwd_edit.text().strip()
        confirm = self.pwd_confirm_edit.text().strip()
        if len(pwd) < 6:
            QMessageBox.warning(self, "输入错误", "密码长度不得小于6位")
            return
        if pwd != confirm:
            QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")
            return
        try:
            resp = client.change_password(pwd)
            if resp.get('success'):
                QMessageBox.information(self, "修改成功", "密码已更新，请牢记新密码")
                self.accept()
            else:
                QMessageBox.warning(self, "修改失败", resp.get('message', '修改失败'))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改失败: {str(e)}")


class CourseDetailDialog(QDialog):
    """课程详情对话框"""
    def __init__(self, course_data, parent=None):
        super().__init__(parent)
        self.course_data = course_data
        self.setWindowTitle("课程详细信息")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建标题
        title_layout = QHBoxLayout()
        title_icon = QLabel("📚")
        title_icon.setFont(QFont("Arial", 24))
        title_layout.addWidget(title_icon)
        
        title_label = QLabel(self.course_data.get('course_name', '未知课程'))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 创建信息显示区域
        info_widget = QWidget()
        info_widget.setStyleSheet("background-color: #f9f9f9; border-radius: 5px; padding: 15px;")
        info_layout = QVBoxLayout(info_widget)
        
        # 课程代码
        course_code = self.course_data.get('course_code', '无')
        code_label = QLabel(f"<b>课程代码：</b>{course_code}")
        code_label.setFont(QFont("Arial", 11))
        info_layout.addWidget(code_label)
        
        # 学分
        credits = self.course_data.get('credits', '无')
        credits_label = QLabel(f"<b>学分：</b>{credits}")
        credits_label.setFont(QFont("Arial", 11))
        info_layout.addWidget(credits_label)
        
        # 教师
        teacher_name = self.course_data.get('teacher_name', '未指定')
        teacher_label = QLabel(f"<b>授课教师：</b>{teacher_name}")
        teacher_label.setFont(QFont("Arial", 11))
        info_layout.addWidget(teacher_label)
        
        # 上课时间
        class_time = self.course_data.get('class_time', '待定')
        time_label = QLabel(f"<b>上课时间：</b>{class_time}")
        time_label.setFont(QFont("Arial", 11))
        info_layout.addWidget(time_label)
        
        # 上课地点
        class_location = self.course_data.get('class_room', '') or self.course_data.get('class_location', '待定')
        location_label = QLabel(f"<b>上课地点：</b>{class_location}")
        location_label.setFont(QFont("Arial", 11))
        info_layout.addWidget(location_label)
        
        # 学期
        semester = self.course_data.get('semester', '未知')
        semester_label = QLabel(f"<b>学期：</b>{semester}")
        semester_label.setFont(QFont("Arial", 11))
        info_layout.addWidget(semester_label)
        
        layout.addWidget(info_widget)
        
        # 添加关闭按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("关闭")
        close_button.setMinimumHeight(35)
        close_button.setMinimumWidth(100)
        close_button.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; border-radius: 5px; padding: 5px 15px; font-weight: bold; }"
            "QPushButton:hover { background-color: #1976D2; }"
        )
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)


class CourseSelectionDialog(QDialog):
    """选课对话框"""
    def __init__(self, semester, parent=None):
        super().__init__(parent)
        self.semester = semester
        self.setWindowTitle(f"选课 - {semester}")
        self.setMinimumSize(900, 600)
        self.available_courses = []
        self.init_ui()
        self.load_courses()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 顶部说明
        info_label = QLabel(f"当前学期：{self.semester}\n请从下方列表中选择课程（系统会自动检测时间冲突）")
        info_label.setStyleSheet("color: #666; padding: 10px; background-color: #f9f9f9; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # 创建课程表格
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(7)
        self.courses_table.setHorizontalHeaderLabels(["课程代码", "课程名称", "学分", "教师", "上课时间", "上课地点", "操作"])
        self.courses_table.horizontalHeader().setStretchLastSection(False)
        self.courses_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.courses_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.courses_table)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.load_courses)
        button_layout.addWidget(self.refresh_button)
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def load_courses(self):
        """加载可选课程"""
        try:
            response = client.get_available_courses(self.semester)
            if response.get('success'):
                self.available_courses = response.get('courses', [])
                self.display_courses()
            else:
                QMessageBox.warning(self, "加载失败", response.get('message', '无法加载课程列表'))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载课程失败: {str(e)}")
    
    def display_courses(self):
        """显示课程列表"""
        self.courses_table.setRowCount(0)
        
        if not self.available_courses:
            QMessageBox.information(self, "提示", "当前学期没有可选课程")
            return
        
        for course in self.available_courses:
            row_position = self.courses_table.rowCount()
            self.courses_table.insertRow(row_position)
            
            # 设置表格数据
            self.courses_table.setItem(row_position, 0, QTableWidgetItem(course.get('course_code', '')))
            self.courses_table.setItem(row_position, 1, QTableWidgetItem(course.get('course_name', '')))
            self.courses_table.setItem(row_position, 2, QTableWidgetItem(str(course.get('credits', ''))))
            self.courses_table.setItem(row_position, 3, QTableWidgetItem(course.get('teacher_name', '')))
            self.courses_table.setItem(row_position, 4, QTableWidgetItem(course.get('class_time', '') or "待定"))
            self.courses_table.setItem(row_position, 5, QTableWidgetItem(course.get('class_room', '') or "待定"))
            
            # 添加选课按钮
            enroll_btn = QPushButton("选课")
            enroll_btn.setStyleSheet(
                "QPushButton { background-color: #4CAF50; color: white; border-radius: 3px; padding: 5px 15px; }"
                "QPushButton:hover { background-color: #45a049; }"
            )
            enroll_btn.clicked.connect(lambda checked, c=course: self.enroll_course(c))
            self.courses_table.setCellWidget(row_position, 6, enroll_btn)
        
        # 调整列宽
        self.courses_table.resizeColumnsToContents()
        self.courses_table.horizontalHeader().setStretchLastSection(True)
    
    def enroll_course(self, course):
        """选课"""
        course_name = course.get('course_name', '未知课程')
        course_id = course.get('id')
        
        if not course_id:
            QMessageBox.warning(self, "选课失败", "课程信息不完整")
            return
        
        # 确认选课
        reply = QMessageBox.question(
            self, 
            "确认选课", 
            f"确定要选择《{course_name}》吗？\n\n上课时间：{course.get('class_time', '待定')}\n上课地点：{course.get('class_room', '待定')}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                response = client.enroll_course(course_id, self.semester)
                if response.get('success'):
                    QMessageBox.information(self, "成功", "选课成功！")
                    # 重新加载课程列表
                    self.load_courses()
                    # 通知父窗口刷新
                    self.accept()
                else:
                    # 如果是时间冲突，显示详细信息
                    message = response.get('message', '选课失败')
                    QMessageBox.warning(self, "选课失败", message)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"选课失败: {str(e)}")


# 测试代码
if __name__ == '__main__':
    # 这里只是为了测试
    test_user_info = {
        'id': 1,
        'username': 'student1',
        'role': 'student',
        'name': '张三'
    }
    
    app = QApplication(sys.argv)
    dashboard = StudentDashboard(test_user_info)
    dashboard.show()
    sys.exit(app.exec_())