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
            
            # 课程信息暂时从成绩中提取
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
            # 这里简化处理，实际可能需要从其他地方获取
            self.courses_table.setItem(row_position, 4, QTableWidgetItem("待定"))
            self.courses_table.setItem(row_position, 5, QTableWidgetItem("待定"))
        
        # 调整表格列宽
        self.courses_table.resizeColumnsToContents()
    
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
        
        # 创建课程表格
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(6)
        self.courses_table.setHorizontalHeaderLabels(["课程代码", "课程名称", "学分", "教师", "上课时间", "上课地点"])
        
        # 设置表格样式
        self.courses_table.horizontalHeader().setStretchLastSection(True)
        
        # 添加课程表格到布局
        courses_layout.addWidget(self.courses_table)
    
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
                'class_name': class_name,
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