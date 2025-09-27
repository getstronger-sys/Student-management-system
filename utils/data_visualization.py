#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""数据可视化模块"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
from matplotlib.ticker import MaxNLocator

# 配置中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 正确显示负号

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('data_visualization')


class ScoreDistributionChart(FigureCanvas):
    """成绩分布柱状图"""
    
    def __init__(self, width=5, height=4, dpi=100):
        """初始化成绩分布柱状图"""
        # 创建figure对象
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        
        # 调用父类构造函数
        super().__init__(self.fig)
        
        # 创建子图
        self.axes = self.fig.add_subplot(111)
        
        # 初始化图表
        self.init_chart()
    
    def init_chart(self):
        """初始化图表样式"""
        # 设置图表标题
        self.axes.set_title("成绩分布图")
        
        # 设置坐标轴标签
        self.axes.set_xlabel("分数段")
        self.axes.set_ylabel("人数")
        
        # 设置坐标轴刻度
        self.axes.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.axes.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        # 关闭网格线
        self.axes.grid(False)
    
    def update_data(self, scores):
        """更新成绩数据并绘制图表"""
        # 清空图表
        self.axes.clear()
        
        # 重新初始化图表样式
        self.init_chart()
        
        try:
            # 检查输入数据
            if not scores or len(scores) == 0:
                # 没有数据时显示空图表
                self.axes.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=self.axes.transAxes)
                self.draw()
                return
            
            # 计算分数段
            score_ranges = [(0, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
            range_labels = ['0-59', '60-69', '70-79', '80-89', '90-100']
            
            # 统计各分数段的人数
            count = [0] * len(score_ranges)
            
            for score in scores:
                for i, (min_score, max_score) in enumerate(score_ranges):
                    if min_score <= score < max_score:
                        count[i] += 1
                        break
                if score >= 100:
                    count[-1] += 1
            
            # 设置柱状图宽度
            width = 0.6
            
            # 绘制柱状图
            x_pos = np.arange(len(range_labels))
            bars = self.axes.bar(x_pos, count, width, color='skyblue', edgecolor='black')
            
            # 添加数据标签
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    self.axes.text(
                        bar.get_x() + bar.get_width() / 2., height,
                        f'{int(height)}', ha='center', va='bottom'
                    )
            
            # 设置x轴刻度标签
            self.axes.set_xticks(x_pos)
            self.axes.set_xticklabels(range_labels)
            
            # 设置y轴范围
            max_count = max(count) if count else 1
            self.axes.set_ylim(0, max_count * 1.2)
            
            # 计算平均分、最高分、最低分
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            
            # 在图表下方添加统计信息
            stats_text = f'平均分: {avg_score:.2f}   最高分: {max_score}   最低分: {min_score}'
            self.fig.text(0.5, 0.01, stats_text, ha='center', fontsize=10)
            
            # 调整布局
            self.fig.tight_layout(rect=[0, 0.05, 1, 0.95])
            
            # 重新绘制图表
            self.draw()
        except Exception as e:
            logger.error(f"更新成绩分布图时发生错误: {e}")
            # 显示错误信息
            self.axes.text(0.5, 0.5, f'数据可视化错误: {str(e)}', ha='center', va='center', transform=self.axes.transAxes, color='red')
            self.draw()
    
    def clear_chart(self):
        """清空图表"""
        # 清空图表
        self.axes.clear()
        
        # 重新初始化图表样式
        self.init_chart()
        
        # 显示空数据提示
        self.axes.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=self.axes.transAxes)
        
        # 重新绘制图表
        self.draw()


class TermComparisonChart(FigureCanvas):
    """学期对比折线图"""
    
    def __init__(self, width=6, height=4, dpi=100):
        """初始化学期对比折线图"""
        # 创建figure对象
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        
        # 调用父类构造函数
        super().__init__(self.fig)
        
        # 创建子图
        self.axes = self.fig.add_subplot(111)
        
        # 初始化图表
        self.init_chart()
    
    def init_chart(self):
        """初始化图表样式"""
        # 设置图表标题
        self.axes.set_title("学期成绩对比图")
        
        # 设置坐标轴标签
        self.axes.set_xlabel("学期")
        self.axes.set_ylabel("平均分")
        
        # 设置y轴范围
        self.axes.set_ylim(0, 100)
        
        # 添加网格线
        self.axes.grid(True, linestyle='--', alpha=0.7)
        
        # 设置图例
        self.axes.legend()
    
    def update_data(self, term_scores):
        """更新学期数据并绘制图表"""
        # 清空图表
        self.axes.clear()
        
        # 重新初始化图表样式
        self.init_chart()
        
        try:
            # 检查输入数据
            if not term_scores or len(term_scores) == 0:
                # 没有数据时显示空图表
                self.axes.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=self.axes.transAxes)
                self.draw()
                return
            
            # 提取学期名称和平均分
            terms = []
            avg_scores = []
            
            for term, scores in term_scores.items():
                terms.append(term)
                if scores:
                    avg_scores.append(sum(scores) / len(scores))
                else:
                    avg_scores.append(0)
            
            # 绘制折线图
            self.axes.plot(terms, avg_scores, 'o-', color='blue', linewidth=2, markersize=6)
            
            # 添加数据标签
            for i, score in enumerate(avg_scores):
                if score > 0:
                    self.axes.text(
                        i, score, f'{score:.2f}', ha='center', va='bottom'
                    )
            
            # 设置x轴刻度
            self.axes.set_xticks(range(len(terms)))
            self.axes.set_xticklabels(terms, rotation=45, ha='right')
            
            # 调整布局
            self.fig.tight_layout()
            
            # 重新绘制图表
            self.draw()
        except Exception as e:
            logger.error(f"更新学期对比图时发生错误: {e}")
            # 显示错误信息
            self.axes.text(0.5, 0.5, f'数据可视化错误: {str(e)}', ha='center', va='center', transform=self.axes.transAxes, color='red')
            self.draw()
    
    def clear_chart(self):
        """清空图表"""
        # 清空图表
        self.axes.clear()
        
        # 重新初始化图表样式
        self.init_chart()
        
        # 显示空数据提示
        self.axes.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=self.axes.transAxes)
        
        # 重新绘制图表
        self.draw()


class CourseComparisonChart(FigureCanvas):
    """课程对比图"""
    
    def __init__(self, width=6, height=4, dpi=100):
        """初始化课程对比图"""
        # 创建figure对象
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        
        # 调用父类构造函数
        super().__init__(self.fig)
        
        # 创建子图
        self.axes = self.fig.add_subplot(111)
        
        # 初始化图表
        self.init_chart()
    
    def init_chart(self):
        """初始化图表样式"""
        # 设置图表标题
        self.axes.set_title("课程平均分对比")
        
        # 设置坐标轴标签
        self.axes.set_xlabel("课程")
        self.axes.set_ylabel("平均分")
        
        # 设置y轴范围
        self.axes.set_ylim(0, 100)
        
        # 关闭网格线
        self.axes.grid(False)
    
    def update_data(self, course_scores):
        """更新课程数据并绘制图表"""
        # 清空图表
        self.axes.clear()
        
        # 重新初始化图表样式
        self.init_chart()
        
        try:
            # 检查输入数据
            if not course_scores or len(course_scores) == 0:
                # 没有数据时显示空图表
                self.axes.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=self.axes.transAxes)
                self.draw()
                return
            
            # 提取课程名称和平均分
            courses = []
            avg_scores = []
            
            for course_name, scores in course_scores.items():
                courses.append(course_name)
                if scores:
                    avg_scores.append(sum(scores) / len(scores))
                else:
                    avg_scores.append(0)
            
            # 设置柱状图宽度
            width = 0.6
            
            # 绘制柱状图
            x_pos = np.arange(len(courses))
            bars = self.axes.bar(x_pos, avg_scores, width, color='lightgreen', edgecolor='black')
            
            # 添加数据标签
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    self.axes.text(
                        bar.get_x() + bar.get_width() / 2., height,
                        f'{height:.2f}', ha='center', va='bottom'
                    )
            
            # 设置x轴刻度标签
            self.axes.set_xticks(x_pos)
            self.axes.set_xticklabels(courses, rotation=45, ha='right')
            
            # 调整布局
            self.fig.tight_layout()
            
            # 重新绘制图表
            self.draw()
        except Exception as e:
            logger.error(f"更新课程对比图时发生错误: {e}")
            # 显示错误信息
            self.axes.text(0.5, 0.5, f'数据可视化错误: {str(e)}', ha='center', va='center', transform=self.axes.transAxes, color='red')
            self.draw()
    
    def clear_chart(self):
        """清空图表"""
        # 清空图表
        self.axes.clear()
        
        # 重新初始化图表样式
        self.init_chart()
        
        # 显示空数据提示
        self.axes.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=self.axes.transAxes)
        
        # 重新绘制图表
        self.draw()


class OverallStatisticsChart(FigureCanvas):
    """系统整体统计图表"""
    
    def __init__(self, width=6, height=4, dpi=100):
        """初始化系统整体统计图表"""
        # 创建figure对象
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        
        # 调用父类构造函数
        super().__init__(self.fig)
        
        # 创建子图
        self.axes = self.fig.add_subplot(111)
        
        # 初始化图表
        self.init_chart()
    
    def init_chart(self):
        """初始化图表样式"""
        # 设置图表标题
        self.axes.set_title("系统用户统计")
        
        # 关闭坐标轴
        self.axes.axis('off')
    
    def update_data(self, statistics_data):
        """更新统计数据"""
        # 清空图表
        self.axes.clear()
        
        # 重新初始化图表样式
        self.init_chart()
        
        try:
            # 检查输入数据
            if not statistics_data or len(statistics_data) == 0:
                # 没有数据时显示空图表
                self.axes.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=self.axes.transAxes)
                self.draw()
                return
            
            # 计算网格大小
            rows = len(statistics_data) // 2
            if len(statistics_data) % 2 != 0:
                rows += 1
            
            # 创建网格布局
            stats_grid = []
            for i, (key, value) in enumerate(statistics_data.items()):
                stats_grid.append(f"{key}: {value}")
            
            # 将网格数据转换为2D列表
            stats_2d = []
            for i in range(0, len(stats_grid), 2):
                row = stats_grid[i:i+2]
                if len(row) < 2:
                    row.append('')  # 补齐最后一行
                stats_2d.append(row)
            
            # 绘制表格
            table = self.axes.table(
                cellText=stats_2d,
                cellLoc='center',
                loc='center'
            )
            
            # 设置表格样式
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.5, 2)
            
            # 调整布局
            self.fig.tight_layout()
            
            # 重新绘制图表
            self.draw()
        except Exception as e:
            logger.error(f"更新系统统计图表时发生错误: {e}")
            # 显示错误信息
            self.axes.text(0.5, 0.5, f'数据可视化错误: {str(e)}', ha='center', va='center', transform=self.axes.transAxes, color='red')
            self.draw()
    
    def clear_chart(self):
        """清空图表"""
        # 清空图表
        self.axes.clear()
        
        # 重新初始化图表样式
        self.init_chart()
        
        # 显示空数据提示
        self.axes.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=self.axes.transAxes)
        
        # 重新绘制图表
        self.draw()


# 测试代码
if __name__ == '__main__':
    # 这里只是为了测试
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("数据可视化测试")
    window.resize(800, 600)
    
    # 创建中心部件
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # 创建布局
    layout = QVBoxLayout(central_widget)
    
    # 测试成绩分布图表
    score_chart = ScoreDistributionChart()
    scores = [65, 72, 85, 92, 78, 68, 95, 88, 76, 60, 55, 90, 82, 71, 87]
    score_chart.update_data(scores)
    layout.addWidget(score_chart)
    
    # 测试学期对比图表
    term_chart = TermComparisonChart()
    term_scores = {
        '2022-秋季': [75, 82, 68, 90, 78],
        '2023-春季': [80, 76, 88, 92, 72],
        '2023-秋季': [85, 90, 78, 82, 95]
    }
    term_chart.update_data(term_scores)
    layout.addWidget(term_chart)
    
    # 显示窗口
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())