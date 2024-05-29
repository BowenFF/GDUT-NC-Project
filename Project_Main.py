import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget,
    QWidget, QVBoxLayout, QLabel
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QTimer

from Project import Ui_NC_Project
import sys
import warnings
import math
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import rcParams

from daobu_chabu_dengjianjv import plot_heart_curve_with_tool_path
from daobu_chabu_dengjianjv_sin import offset_curve
from generate_nccode_v4 import generate_nc_code

warnings.filterwarnings("ignore",category=DeprecationWarning)

# 在创建图形之前设置字体
rcParams['font.family'] = 'SimHei'  # 例如，使用SimHei字体支持中文
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

class My_NC_Project(Ui_NC_Project, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('LOGO.JPG'))
        self.radioButton_xinzang.toggled.connect(self.xinzang)
        self.radioButton_tulun.toggled.connect(self.tulun)
        self.radioButton_clockwise.toggled.connect(self.clockwise)
        self.radioButton_anticlockwise.toggled.connect(self.anticlockwise)
        self.radioButton_zuodaobu.toggled.connect(self.zuodaobu)
        self.radioButton_youdaobu.toggled.connect(self.youdaobu)
        self.pushButton_start.clicked.connect(self.start)
        self.pushButton_close.clicked.connect(self.close)
        self.pushButton_about.clicked.connect(self.about)
        self.pushButton_fangzhen.clicked.connect(self.fangzhen)
        self.pushButton_back.clicked.connect(self.back)
        self.pushButton_NC_code.clicked.connect(self.display_NC_code)
        self.pushButton_back2.clicked.connect(self.back2)
        self.pushButton_jiagongdonghua.clicked.connect(self.jiagongdonghua)
        self.customGraphicsView = CustomGraphicsView(self.centralwidget)
        self.customGraphicsView.setGeometry(self.graphicsView.geometry())
        self.comboBox_chabu.currentIndexChanged.connect(self.start)
        self.scene = self.customGraphicsView.scene
        self.graphicsView.deleteLater()
        self.anquan.textChanged.connect(self.anquan_Z)
        #初始化
        self.radioButton_xinzang.setChecked(True)
        self.tabWidget.setCurrentIndex(0)
        self.NC_code.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.layout = QVBoxLayout(self.scroll_content)
        self.NC_code.setWidget(self.scroll_content)
        self.show()
    def __sub__(self, other):
        if isinstance(other, My_NC_Project):
            return My_NC_Project(self.value - other.value)
        else:
            return My_NC_Project(self.value - other)
    # 计算两点之间的距离
    def distance(self, p1, p2):
        return np.linalg.norm(p1 - p2)

    def xinzang(self):
        if self.radioButton_xinzang.isChecked():
            self.groupBox_xinzang.setVisible(True)
            self.groupBox_tulun.setVisible(False)
        else:
            return

        pixmap = QPixmap("formula1.jpg")  # 将 "path/to/your/image.png" 替换为你的图片路径
        scaled_pixmap = pixmap.scaled(pixmap.width() //2.6 , pixmap.height() //1.5 )
        self.Function_Equation.setPixmap(scaled_pixmap)
        self.Function_Equation.resize(scaled_pixmap.width(), scaled_pixmap.height())# 调整 QLabel 的大小以适应图片
        if not self.Parameter_Function.text():
            self.Parameter_Function.setText("0.9")
        if not self.lineEdit_wucha.text():
            self.lineEdit_wucha.setText("0.1")
        self.a = float(self.Parameter_Function.text())  # 获取参数值
        error = float(self.lineEdit_wucha.text())
        scale = 10
        if self.comboBox_chabu.currentIndex() == 0:
            # 设定参数范围和初始插补点数、最大距离阈值
            t_start, t_end = 0, 2 * np.pi
            initial_segments = 5  # 初始插补点数，不固定
            max_distance = error  # 最大距离阈值，根据实际需求设定
            # 进行等间距插补
            self.t_values, self.x_values, self.y_values, self.num_segments = self.adaptive_equal_spacing_interpolation\
                                                        (t_start, t_end,initial_segments,max_distance)
            self.plot_figure(self.x_values, self.y_values, scale)
            self.lineEdit_duanshu.setText(f"{self.num_segments}")
        if self.comboBox_chabu.currentIndex() == 1:
            # 设定参数范围和误差阈值
            t_start, t_end = 0, 2 * np.pi
            error_threshold = float(self.lineEdit_wucha.text())  # 误差阈值，根据实际需求设定
            # 进行等误差插补
            self.t_values, self.x_values, self.y_values, self.num_segments = self.equal_error_interpolation(t_start, t_end, error_threshold)
            self.plot_figure(self.x_values, self.y_values, scale)
            self.lineEdit_duanshu.setText(f"{self.num_segments}")


    def tulun(self):
        if self.radioButton_tulun.isChecked():
            self.groupBox_xinzang.setVisible(False)
            self.groupBox_tulun.setVisible(True)
        else:
            return
        if not self.lineEdit_base_radius.text():
            self.lineEdit_base_radius.setText("8")
            self.lineEdit_hight.setText("4")
            self.lineEdit_far_angle.setText("60")
            self.lineEdit_near_angle.setText("90")
        if not self.lineEdit_wucha.text():
            self.lineEdit_wucha.setText("0.1")

        #####起刀点设置
        self.label_X.setText("0")
        self.label_Y.setText("80")

        self.base_radius = float(self.lineEdit_base_radius.text())  # 获取参数值
        self.hight = float(self.lineEdit_hight.text())
        self.far_angle = float(self.lineEdit_far_angle.text())
        self.near_angle = float(self.lineEdit_near_angle.text())
        self.far_angle = self.far_angle * math.pi / 180.0
        self.near_angle = self.near_angle * math.pi / 180.0
        self.to_angle = (math.pi * 2 - self.near_angle - self.far_angle) / 2
        self.return_angle = self.to_angle

        error = float(self.lineEdit_wucha.text())
        scale = 10
        if self.comboBox_chabu.currentIndex() == 0:
            # 设定参数范围和初始插补点数、最大距离阈值
            t_start, t_end = 0, 2 * np.pi
            initial_segments = 10  # 初始插补点数，不固定
            max_distance = error  # 最大距离阈值，根据实际需求设定
            # 进行等间距插补
            self.t_values, self.x_values, self.y_values, self.num_segments = self.adaptive_equal_spacing_interpolation \
                (t_start, t_end, initial_segments, max_distance)
            self.plot_figure(self.x_values, self.y_values, scale)
            self.lineEdit_duanshu.setText(f"{self.num_segments}")
        if self.comboBox_chabu.currentIndex() == 1:
            # 设定参数范围和误差阈值
            t_start, t_end = 0, 2 * np.pi
            error_threshold = float(self.lineEdit_wucha.text())  # 误差阈值，根据实际需求设定
            # 进行等误差插补
            self.t_values, self.x_values, self.y_values, self.num_segments = self.equal_error_interpolation(t_start, t_end, error_threshold)
            self.plot_figure(self.x_values, self.y_values, scale)
            self.lineEdit_duanshu.setText(f"{self.num_segments}")
    def sinline_function(self,angle):
        if angle < self.to_angle:
            return self.hight * ((angle / self.to_angle) -
                            math.sin(2.0 * math.pi * angle / self.to_angle) / 2.0 / math.pi) + self.base_radius
        if self.to_angle <= angle < self.to_angle + self.far_angle:
            return self.base_radius + self.hight
        if self.to_angle + self.far_angle <= angle < self.to_angle + self.far_angle + self.return_angle:
            angle = angle - self.to_angle - self.far_angle
            return self.hight * (1 - (angle / self.return_angle) + math.sin(
                2.0 * math.pi * angle / self.to_angle) / 2.0 / math.pi) + self.base_radius
        else:
            return self.base_radius

    def sinline(self,angle):
        x = self.sinline_function(angle) * math.cos(angle)
        y = self.sinline_function(angle) * math.sin(angle)
        return x, y

    def fangzhen(self):
        self.tabWidget.setCurrentIndex(1)
        if not self.radioButton_clockwise.isChecked():
            self.radioButton_clockwise.setChecked(True)
            self.radioButton_zuodaobu.setChecked(True)
        if not self.radioButton_juedui.isChecked():
            self.daoju.setText("1")
            self.jingei.setText("1000")
            self.zhuzhou.setText("500")
            self.anquan.setText("50")
            self.shendu.setText("5")
            #####起刀点设置
            self.label_X.setText("0")
            self.label_Y.setText("0")
            self.radioButton_juedui.setChecked(True)
        self.jiagongdonghua()

    def back(self):
        self.tabWidget.setCurrentIndex(0)

    def back2(self):
        self.tabWidget.setCurrentIndex(1)

    def start(self):
        if self.radioButton_xinzang.isChecked():
            self.a = float(self.Parameter_Function.text())  # 获取参数值
            scale = 10
            if self.comboBox_chabu.currentIndex() == 0:
                # 设定参数范围和初始插补点数、最大距离阈值
                t_start, t_end = 0, 2 * np.pi
                initial_segments = 10  # 初始插补点数，不固定
                error = float(self.lineEdit_wucha.text())
                max_distance = error  # 最大距离阈值，根据实际需求设定
                # 进行等间距插补
                self.t_values, self.x_values, self.y_values, self.num_segments = self.adaptive_equal_spacing_interpolation \
                    (t_start, t_end, initial_segments, max_distance)
                self.plot_figure(self.x_values, self.y_values, scale)
                self.lineEdit_duanshu.setText(f"{self.num_segments}")
            else:
                # 设定参数范围和误差阈值
                t_start, t_end = 0, 2 * np.pi
                error_threshold = float(self.lineEdit_wucha.text())  # 误差阈值，根据实际需求设定

                # 进行等误差插补
                self.t_values, self.x_values, self.y_values, self.num_segments = self.equal_error_interpolation(t_start, t_end, error_threshold)
                self.plot_figure(self.x_values, self.y_values, scale)
                self.lineEdit_duanshu.setText(f"{self.num_segments}")
        else:
            self.base_radius = float(self.lineEdit_base_radius.text())  # 获取参数值
            self.hight = float(self.lineEdit_hight.text())
            self.far_angle = float(self.lineEdit_far_angle.text())
            self.near_angle = float(self.lineEdit_near_angle.text())
            self.far_angle = self.far_angle * math.pi / 180.0
            self.near_angle = self.near_angle * math.pi / 180.0
            self.to_angle = (math.pi * 2 - self.near_angle - self.far_angle) / 2
            self.return_angle = self.to_angle

            error = float(self.lineEdit_wucha.text())
            scale = 10

            if self.comboBox_chabu.currentIndex() == 0:
                # 设定参数范围和初始插补点数、最大距离阈值
                t_start, t_end = 0, 2 * np.pi
                initial_segments = 10  # 初始插补点数，不固定
                max_distance = error  # 最大距离阈值，根据实际需求设定
                # 进行等间距插补
                self.t_values, self.x_values, self.y_values, self.num_segments = self.adaptive_equal_spacing_interpolation \
                    (t_start, t_end, initial_segments, max_distance)
                self.plot_figure(self.x_values, self.y_values, scale)
                self.lineEdit_duanshu.setText(f"{self.num_segments}")
            if self.comboBox_chabu.currentIndex() == 1:
                # 设定参数范围和误差阈值
                t_start, t_end = 0, 2 * np.pi
                error_threshold = float(self.lineEdit_wucha.text())  # 误差阈值，根据实际需求设定
                # 进行等误差插补
                self.t_values, self.x_values, self.y_values, self.num_segments = self.equal_error_interpolation(t_start, t_end, error_threshold)
                self.plot_figure(self.x_values, self.y_values, scale)
                self.lineEdit_duanshu.setText(f"{self.num_segments}")


    def about(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("小组信息")
        msg_box.setText("小组成员：\n王淳锋 3121000016\n黄兴文 3121000006\n余文基 3121000019\n指导老师：姜永军")
        msg_box.exec()

    def close(self):
        QApplication.quit()  # 退出应用程序

    def display_NC_code(self):
        self.tabWidget.setCurrentIndex(2)
        self.generate_NC_code()

    def generate_NC_code(self):
        if self.layout is not None:
            while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
        tool_radius = float(self.daoju.text())
        feed_rate = float(self.jingei.text())
        spindle_speed = float(self.zhuzhou.text())
        safety_height = float(self.anquan.text())
        shendu = float(self.shendu.text())
        start_point = (float(self.label_X.text()),float(self.label_Y.text()))
        if self.radioButton_zuodaobu.isChecked():
            compensation_direction = 'left'
        else:
            compensation_direction = 'right'
        if self.radioButton_juedui.isChecked():
            use_relative_coordinates = False
        else:
            use_relative_coordinates = True
        nc_code = generate_nc_code(self.t_values, self.x_values, self.y_values, tool_radius=tool_radius, feed_rate=feed_rate, spindle_speed=spindle_speed,
                     safety_height=safety_height, cut_depth=shendu, start_point=start_point, compensation_direction=compensation_direction,
                     use_relative_coordinates=use_relative_coordinates)
        # 将数控代码添加到内容部件
        for line in nc_code:
            label = QLabel(line)
            self.layout.addWidget(label)

    def plot_figure(self,x_vals, y_vals,scale):
        # 清空场景
        self.customGraphicsView.scene.clear()
        # 创建图形
        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        if self.comboBox_chabu.currentIndex() == 0:
            ax.plot(x_vals, y_vals, color='red')
        else:
            ax.plot(x_vals, y_vals, color='blue')
        ax.axis('equal')
        # 将原点设置在中心，绘制十字形坐标轴
        ax.spines['left'].set_position('center')
        ax.spines['bottom'].set_position('center')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        # 手动设置 x 轴和 y 轴的刻度
        x_ticks = list(range(-15, 16, 5))  # 设置 x 轴刻度
        y_ticks = list(range(-15, 16, 5))  # 设置 y 轴刻度
        ax.set_xticks(x_ticks)
        ax.set_yticks(y_ticks)
        # 设置每个刻度都有标签
        ax.set_xticklabels([str(tick) for tick in x_ticks])
        ax.set_yticklabels([str(tick) for tick in y_ticks])
        # 设置x轴和y轴的范围
        ax.set_xlim(-scale * 1.8, scale * 1.8)
        ax.set_ylim(-scale * 1.8, scale * 1.8)
        # 隐藏 Y 轴上的 "0" 标签
        yticks = ax.get_yticks()
        ytick_labels = ['' if y == 0 else str(y) for y in yticks]
        ax.set_yticks(yticks)
        ax.set_yticklabels(ytick_labels)
        # 隐藏 X 轴上的 "0" 标签
        xticks = ax.get_xticks()
        xtick_labels = ['' if x == 0 else str(x) for x in xticks]
        ax.set_xticks(xticks)
        ax.set_xticklabels(xtick_labels)
        # 设置x轴上的0与坐标轴错开
        ax.annotate('0', xy=(0, 0), xytext=(-1, -1.5))
        # 添加箭头
        ax.annotate('', xy=(18, 0), xytext=(17.9, 0),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color='black'))
        ax.annotate('', xy=(0, 17.8), xytext=(0, 17.7),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color='black'))
        # 添加坐标轴标签
        ax.text(0.9, 0.40, 'X轴', transform=ax.transAxes)
        ax.text(0.52, 0.94, 'Y轴', transform=ax.transAxes)
        # 将图形添加到QGraphicsView中
        canvas = FigureCanvas(fig)
        proxy_widget = QGraphicsProxyWidget()
        proxy_widget.setWidget(canvas)
        self.customGraphicsView.scene.addItem(proxy_widget)

    def plot_xinzang(self, t):
        x = self.a * (16 * math.sin(t) ** 3)
        y = self.a * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        return x,y

    # 等间距插补法
    def adaptive_equal_spacing_interpolation(self,t_start, t_end, initial_segments, max_distance,):
        segments = initial_segments
        while True:
            # 在参数t上进行等间距插补
            t_values = np.linspace(t_start, t_end, segments)
            if self.radioButton_xinzang.isChecked():
                x_values, y_values = zip(*[self.plot_xinzang(t) for t in t_values])
            else:
                x_values, y_values = zip(*[self.sinline(t) for t in t_values])
            # 计算相邻点之间的距离
            distances = np.sqrt(np.diff(x_values) ** 2 + np.diff(y_values) ** 2)
            # 检查最大距离是否满足条件
            if np.max(distances) <= max_distance or segments >= 3000:  # 假设最大插补点数为1000
                break
                # 如果不满足条件，则增加插补点的数量
            segments *= 2
            # 添加起始点到插补点
        t_values = np.concatenate(([t_start], t_values))
        if self.radioButton_xinzang.isChecked():
            x_values = np.concatenate(([self.plot_xinzang(t_start)[0]], x_values))
            y_values = np.concatenate(([self.plot_xinzang(t_start)[1]], y_values))
        else:
            x_values = np.concatenate(([self.sinline(t_start)[0]], x_values))
            y_values = np.concatenate(([self.sinline(t_start)[1]], y_values))
        return t_values, x_values, y_values, segments - 1  # 返回线段数（即插补点数量减一）




    # 等误差插补法
    def equal_error_interpolation(self, t_start, t_end, error_threshold):

        t = t_start  # 初始参数
        nodes = []  # 存储节点坐标
        dt = error_threshold  # 参数增量，可根据需要调整以提高精度

        if self.radioButton_xinzang.isChecked():
            current_point = self.plot_xinzang(t)
        else:
            # points = [(t_start, self.sinline(t))]
            current_point = self.sinline(t)
        nodes.append(current_point)
        while t < t_end:
            t += dt
            if self.radioButton_xinzang.isChecked():
                next_point = self.plot_xinzang(t)
            else:
                next_point = self.sinline(t)
            if self.distance(np.array(current_point), np.array(next_point)) > error_threshold:
                nodes.append(next_point)
                current_point = next_point
        if self.distance(np.array(nodes[0]), np.array(nodes[-1])) > error_threshold:
            nodes.append(nodes[0])
        # for i, node in enumerate(nodes):
        #     # print(f"节点 {i + 1}: ({node[0]}, {node[1]})")
        #     x_values = np.array(node[0])
        #     y_values = np.array(node[1])
        # x_values = [node[0] for node in nodes]
        # y_values = [node[1] for node in nodes]
        t_values = [p[0] for p in nodes]
        x_values, y_values = zip(*nodes)
        x_values = list(x_values)
        y_values = list(y_values)
        # print(f"节点 {i + 1}: ({x_values}, {x_values})")
        return t_values, x_values, y_values, len(nodes) - 1


    # 计算两点之间的弦长
    def chord_length(self, t1, t2, n=100):
        t_values = np.linspace(t1, t2, n)
        if self.radioButton_xinzang.isChecked():
            x_values, y_values = zip(*[self.plot_xinzang(t=t) for t in t_values])
        else:
            x_values, y_values = zip(*[self.sinline(t) for t in t_values])
        dx = np.diff(x_values)
        dy = np.diff(y_values)
        return np.sum(np.sqrt(dx ** 2 + dy ** 2))

    def plot_animation(self):
        # 清空场景
        self.customGraphicsView.scene.clear()

        # 创建 pyqtgraph 的 GraphicsLayoutWidget
        self.plot_widget = pg.GraphicsLayoutWidget()

        # 创建一个 plot
        self.plot = self.plot_widget.addPlot(title="仿真加工")
        self.plot.setXRange(-20,20)
        self.plot.setYRange(-20, 20)
        self.plot.showGrid(x=True, y=True)

        # 设置坐标轴标签
        self.plot.setLabel('left', 'Y-Axis')
        self.plot.setLabel('bottom', 'X-Axis')

        # 设置坐标轴标签和刻度
        self.plot.getAxis('left').setStyle(showValues=True)
        self.plot.getAxis('bottom').setStyle(showValues=True)
        self.plot.setLabel('left', 'Y-Axis')
        self.plot.setLabel('bottom', 'X-Axis')

        # 将 GraphicsLayoutWidget 包装成 QGraphicsProxyWidget 并添加到场景
        self.proxy = QGraphicsProxyWidget()
        self.proxy.setWidget(self.plot_widget)
        self.customGraphicsView.scene.addItem(self.proxy)

        # 设置背景颜色为白色
        self.plot.getViewBox().setBackgroundColor('w')

        # 调整 plot_widget 的大小和位置，使其与 QGraphicsView 的场景匹配
        self.proxy.resize(self.customGraphicsView.width(), self.customGraphicsView.height())

        # 将 self.proxy 的位置设定为 self.customGraphicsView 的中心位置
        view_center = self.customGraphicsView.viewport().rect().center()
        self.proxy.setPos(view_center.x() - self.proxy.boundingRect().width() / 2,
                          view_center.y() - self.proxy.boundingRect().height() / 2)

        ## 初始化数据
        # 初始化动态数据线（已存在）
        self.data_line_moving = self.plot.plot([], [], pen=pg.mkPen(color='b', width=3, style=Qt.PenStyle.DashLine))
        self.data_line_cycle = self.plot.plot([], [], pen=pg.mkPen(color='b', width=3))
        # 新增初始化静态数据线
        self.data_line_static = self.plot.plot([], [], pen=pg.mkPen(color='r', width=3))  # 红色代表静态曲线
        self.current_index = 0
        self.continue_updates = True

        # 创建一个定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        if self.jingei.text() == '':
            time = 1000
        else:
            time = float(self.jingei.text())    # 进给速度
            self.timer.start(1000/time)  # 每xx毫秒更新一次
        # 心脏线过切报警
        if self.radioButton_xinzang.isChecked():
            if not (self.daoju.text() == ''):
                self.guoqieyujing()

    def update_plot(self):
        if self.current_index >= len(self.x_values):
            self.timer.stop()
        else:
            tool_radius = float(self.daoju.text())
            angle = np.linspace(0, 2 * np.pi, 100)
            if self.radioButton_clockwise.isChecked():
                if self.radioButton_xinzang.isChecked():
                    x_data = self.offset_x_array[:self.current_index + 1]
                    y_data = self.offset_y_array[:self.current_index + 1]
                else:
                    x_data = self.offset_x_array[-(self.current_index + 1):][::-1]
                    y_data = self.offset_y_array[-(self.current_index + 1):][::-1]
            else:
                if self.radioButton_xinzang.isChecked():
                    x_data = self.offset_x_array[-(self.current_index + 1):][::-1]
                    y_data = self.offset_y_array[-(self.current_index + 1):][::-1]
                else:
                    x_data = self.offset_x_array[:self.current_index + 1]
                    y_data = self.offset_y_array[:self.current_index + 1]
            self.data_line_static.setData(self.x_values, self.y_values)
            self.data_line_moving.setData(x_data, y_data)
            #刀具圆
            if self.current_index < len(self.offset_x_array) and self.current_index < len(self.offset_y_array):
                tool_radius = float(self.daoju.text())
                angle = np.linspace(0, 2 * np.pi, 100)
                if self.radioButton_clockwise.isChecked():
                    if self.radioButton_xinzang.isChecked():
                        x_circle = self.offset_x_array[self.current_index] + tool_radius * np.cos(angle)
                        y_circle = self.offset_y_array[self.current_index] + tool_radius * np.sin(angle)
                    else:
                        x_circle = self.offset_x_array[-(self.current_index)] + tool_radius * np.cos(angle)
                        y_circle = self.offset_y_array[-(self.current_index)] + tool_radius * np.sin(angle)
                else:
                    if self.radioButton_xinzang.isChecked():
                        x_circle = self.offset_x_array[-(self.current_index)] + tool_radius * np.cos(angle)
                        y_circle = self.offset_y_array[-(self.current_index)] + tool_radius * np.sin(angle)
                    else:
                        x_circle = self.offset_x_array[self.current_index] + tool_radius * np.cos(angle)
                        y_circle = self.offset_y_array[self.current_index] + tool_radius * np.sin(angle)
                self.data_line_cycle.setData(x_circle, y_circle)
            self.current_index += 1

    def clockwise(self):
        if not self.radioButton_clockwise.isChecked():
            return
        if (self.daoju.text()==''):
            return
        else:
            if self.daoju.text() == '':
                tool_radius = 1
            else:
                tool_radius = float(self.daoju.text())
            if self.radioButton_xinzang.isChecked():
                if self.radioButton_zuodaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'left')
                else:
                    self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'right')
            else:
                base_radius = float(self.lineEdit_base_radius.text())
                if self.radioButton_zuodaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius, 'right')
                    if (self.offset_x_array ==  self.offset_y_array) :
                        return
                else:
                    self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius, 'left')
                    if (self.offset_x_array ==  self.offset_y_array) :
                        return
            self.plot_animation()

    def anticlockwise(self):
        if not self.radioButton_anticlockwise.isChecked():
            return
        else:
            if self.daoju.text() == '':
                tool_radius = 1
            else:
                tool_radius = float(self.daoju.text())
            if self.radioButton_xinzang.isChecked():
                if self.radioButton_zuodaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'right')
                else:
                    self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'left')
            else:
                base_radius = float(self.lineEdit_base_radius.text())
                if self.radioButton_zuodaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius, 'left')
                    if (self.offset_x_array ==  self.offset_y_array) :
                        return
                else:
                    self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius, 'right')
                    if (self.offset_x_array ==  self.offset_y_array) :
                        return
            self.plot_animation()

    def anquan_Z(self):
        Z = self.anquan.text()
        self.label_Z.setText(f"{Z}")

    def zuodaobu(self):
        if not self.radioButton_zuodaobu.isChecked():
            return
        if (self.daoju.text()==''):
            return
        if self.daoju.text() == '':
            tool_radius = 1
        else:
            tool_radius = float(self.daoju.text())
        if self.radioButton_xinzang.isChecked():
            if self.radioButton_clockwise.isChecked():
                self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'left')
            else:
                self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'right')
        else:
            base_radius = float(self.lineEdit_base_radius.text())
            if self.radioButton_clockwise.isChecked():
                self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius,'right')
                if (self.offset_x_array ==  self.offset_y_array) :
                    return
            else:
                self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius,'left')
                if (self.offset_x_array ==  self.offset_y_array) :
                    return
        self.plot_animation()

    def youdaobu(self):
        if not self.radioButton_youdaobu.isChecked():
            return
        if self.daoju.text() == '':
            tool_radius = 0.5
        else:
            tool_radius = float(self.daoju.text())
        if self.radioButton_xinzang.isChecked():
            if self.radioButton_clockwise.isChecked():
                self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'right')
            else:
                self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'left')
            self.plot_animation()
        else:
            base_radius = float(self.lineEdit_base_radius.text())
            if self.radioButton_clockwise.isChecked():
                self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius, 'left')
                if (self.offset_x_array ==  self.offset_y_array) :
                    return
                else:
                    self.plot_animation()
            else:
                self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius, 'right')
                if (self.offset_x_array ==  self.offset_y_array) :
                    return
                else:
                    self.plot_animation()

    def jiagongdonghua(self):
        tool_radius = float(self.daoju.text())
        if self.radioButton_xinzang.isChecked():
            if self.radioButton_clockwise.isChecked():
                if self.radioButton_youdaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'right')
                if self.radioButton_zuodaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'left')
            else:
                if self.radioButton_youdaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'left')
                if self.radioButton_zuodaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = plot_heart_curve_with_tool_path(self.x_values, self.y_values, tool_radius, 'right')
        else:
            base_radius = float(self.lineEdit_base_radius.text())
            if self.radioButton_clockwise.isChecked():
                if self.radioButton_youdaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius, 'left')
                    if (self.offset_x_array ==  self.offset_y_array) :
                        return
                if self.radioButton_zuodaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius, 'right')
                    if (self.offset_x_array ==  self.offset_y_array) :
                        return
            else:
                if self.radioButton_youdaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius, 'right')
                    if (self.offset_x_array ==  self.offset_y_array) :
                        return
                if self.radioButton_zuodaobu.isChecked():
                    self.offset_x_array, self.offset_y_array = offset_curve(self.x_values, self.y_values, tool_radius, base_radius, 'left')
                    if (self.offset_x_array ==  self.offset_y_array) :
                        return
        self.plot_animation()

    def guoqieyujing(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("过切警告")
        msg_box.setText("心脏线加工会有过切问题，已做近似处理")
        msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_NC_Project = My_NC_Project()
    sys.exit(app.exec())