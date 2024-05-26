import numpy as np
import matplotlib.pyplot as plt
# from sin_line_process.dengjianjvchabu.dengjianjv_suanfa import adaptive_equal_spacing_interpolation, base_radius

# # 参数设定
# tool_radius = 40
# t_start = 0
# t_end = 2 * np.pi
# initial_segments = 10
# max_distance = 0.1

# 根据刀具半径和方向偏移曲线，并检测过切
from PyQt6.QtWidgets import QMessageBox


def offset_curve(x_values, y_values, tool_radius, base_radius, direction='left'):
    offsets = []

    if tool_radius >= base_radius and direction == "left":
        msg_box = QMessageBox()
        msg_box.setWindowTitle("过切警告")
        msg_box.setText("刀具半径过大造成过切，请减小刀具半径")
        msg_box.exec()
        return zip((0,0))
    else:
        for i in range(len(x_values) - 1):
            dx = x_values[i + 1] - x_values[i]
            dy = y_values[i + 1] - y_values[i]
            dist = np.sqrt(dx ** 2 + dy ** 2)

            if dist == 0:  # 防止除以零
                continue

            norm_dx = dx / dist
            norm_dy = dy / dist

            if direction == 'left':
                offset_x = x_values[i] - tool_radius * norm_dy
                offset_y = y_values[i] + tool_radius * norm_dx
            elif direction == 'right':
                offset_x = x_values[i] + tool_radius * norm_dy
                offset_y = y_values[i] - tool_radius * norm_dx
            else:
                raise ValueError("Direction must be 'left' or 'right'.")

            offsets.append((offset_x, offset_y))
        return zip(*offsets)  # 返回X和Y的偏移坐标


# # 绘制心脏线和刀具中心轨迹
# def plot_heart_curve_with_tool_path(x_values, y_values, tool_radius, direction):
#     offset_x, offset_y = offset_curve(x_values, y_values, tool_radius, direction)
#
#     plt.figure(figsize=(10, 10))
#     plt.plot(x_values, y_values, label='Heart Curve', color='blue')
#     plt.plot(list(offset_x), list(offset_y), label=f'Tool Path ({direction} offset)', color='red')
#     plt.xlabel('X')
#     plt.ylabel('Y')
#     plt.title('Heart Curve with Tool Path')
#     plt.legend()
#     plt.grid(True)
#     plt.show()
#
#
# t_values, x_values, y_values, segments = adaptive_equal_spacing_interpolation(t_start, t_end, initial_segments,
#                                                                               max_distance)
# plot_heart_curve_with_tool_path(x_values, y_values, tool_radius, 'left')  # 左刀补
# # plot_heart_curve_with_tool_path(x_values, y_values, tool_radius, 'right')  # 右刀补
