#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""教师仪表盘模块"""

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
    QTableWidgetItem, QTabWidget, QFrame, QMessageBox, QComboBox,
    QPushButton, QLineEdit, QFormLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from network.client import client
from models.teacher import Teacher
from models.courses import Course
from models.scores import Score
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
        
        # 学期选择
        self.semester_combo = QComboBox()
        # 添加一些常用学期选项
        self.semester_combo.addItems(["2023-2024-1", "2023-2024-2", "2022-2023-1", "2022-2023-2"])
        search_layout.addWidget(QLabel("选择学期:"))
        search_layout.addWidget(self.semester_combo)
        search_layout.addSpacing(20)
        
        # 查询按钮
        self.query_button = QPushButton("查询")
        self.query_button.clicked.connect(self.query_scores)
        search_layout.addWidget(self.query_button)
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
        
        # 创建图表
        self.create_charts()
        
        # 创建图表布局
        charts_layout = QHBoxLayout()
        charts_layout.addWidget(self.score_distribution_widget)
        charts_layout.addWidget(self.course_comparison_widget)
        
        # 添加图表布局到主布局
        analysis_layout.addLayout(charts_layout)
    
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
            # 获取教师课程
            response = client.get_my_courses()
            
            if response.get('success'):
                courses = response.get('courses', [])
                
                # 清空表格
                self.courses_table.setRowCount(0)
                
                # 清空课程下拉框
                self.course_combo.clear()
                
                # 添加课程到下拉框和表格
                for course in courses:
                    # 添加到下拉框
                    self.course_combo.addItem(course.get('course_name', ''), course.get('course_id'))
                    
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
                stats = response.get('stats', {})
                
                # 清空表格
                self.scores_table.setRowCount(0)
                
                # 填充表格
                for score_info in scores:
                    row_position = self.scores_table.rowCount()
                    self.scores_table.insertRow(row_position)
                    
                    # 设置表格数据
                    self.scores_table.setItem(row_position, 0, QTableWidgetItem(str(score_info.get('student_id', ''))))
                    self.scores_table.setItem(row_position, 1, QTableWidgetItem(score_info.get('student_name', '')))
                    
                    # 创建成绩编辑框（这里简化处理，实际可能需要更复杂的编辑功能）
                    score_item = QTableWidgetItem(str(score_info.get('score', '')))
                    self.scores_table.setItem(row_position, 2, score_item)
                    
                    self.scores_table.setItem(row_position, 3, QTableWidgetItem(str(score_info.get('credits', ''))))
                    
                    # 添加编辑按钮
                    edit_button = QPushButton("编辑")
                    edit_button.clicked.connect(lambda checked, row=row_position, score_id=score_info.get('id'): self.edit_score(row, score_id))
                    self.scores_table.setCellWidget(row_position, 4, edit_button)
                
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
    
    def search_students(self):
        """搜索学生"""
        # 这里简化处理，实际可能需要调用特定的API搜索学生
        QMessageBox.information(self, "功能提示", "学生搜索功能待实现")
    
    def edit_score(self, row, score_id):
        """编辑成绩"""
        # 这里简化处理，实际可能需要弹出对话框进行成绩编辑
        QMessageBox.information(self, "功能提示", f"编辑成绩功能待实现，成绩ID: {score_id}")
    
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
        # 根据页面名称切换标签页
        if page_name == 'profile':
            self.tab_widget.setCurrentWidget(self.profile_widget)
        elif page_name == 'courses':
            self.tab_widget.setCurrentWidget(self.courses_widget)
        elif page_name == 'scores':
            self.tab_widget.setCurrentWidget(self.scores_widget)
        elif page_name == 'students':
            self.tab_widget.setCurrentWidget(self.students_widget)
        elif page_name == 'analysis':
            self.tab_widget.setCurrentWidget(self.analysis_widget)
    
    def refresh(self):
        """刷新数据"""
        # 重新加载数据
        self.load_teacher_info()
        self.load_courses()
        # 如果当前在成绩管理标签页，重新查询成绩
        if self.tab_widget.currentWidget() == self.scores_widget:
            self.query_scores()


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