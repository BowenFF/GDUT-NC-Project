import math

import numpy as np
import matplotlib.pyplot as plt
import cv2
from PyQt6.QtWidgets import QMessageBox
np.seterr(divide='ignore',invalid='ignore')

# 根据刀具半径和方向偏移曲线
# def offset_curve(x_values, y_values, tool_radius, direction='left'):
#     offsets = []
#     overcut_detected = False
#
#     for i in range(len(x_values) - 1):
#         dx = x_values[i + 1] - x_values[i]
#         dy = y_values[i + 1] - y_values[i]
#         dist = np.sqrt(dx ** 2 + dy ** 2)
#
#         if dist == 0:  # 防止除以零
#             continue
#
#         norm_dx = dx / dist
#         norm_dy = dy / dist
#
#         if direction == 'left':
#             offset_x = x_values[i] - tool_radius * norm_dy
#             offset_y = y_values[i] + tool_radius * norm_dx
#         elif direction == 'right':
#             offset_x = x_values[i] + tool_radius * norm_dy
#             offset_y = y_values[i] - tool_radius * norm_dx
#         else:
#             raise ValueError("Direction must be 'left' or 'right'.")
#
#         offsets.append((offset_x, offset_y))
#
#     # if overcut_detected:
#     #     print("Warning: Overcut detected. Please reduce the tool radius.")
#
#     return zip(*offsets)  # 返回X和Y的偏移坐标

def offset_curve(x_values, y_values, tool_radius, direction):
    guoqie = False
    offsets = []
    if direction == 'right':
        tool_radius = -tool_radius
    first_point_x = x_values[0]
    second_point_x = x_values[1]
    third_point_x = x_values[2]
    first_point_y = y_values[0]
    second_point_y = y_values[1]
    third_point_y = y_values[2]

    x = 0
    y = 0
    for i in range(3, len(x_values)):
        dist1 = float(math.sqrt(
            math.pow(second_point_x - first_point_x, 2) + math.pow(second_point_y - first_point_y, 2)))
        dist2 = float(math.sqrt(
            math.pow(third_point_x - second_point_x, 2) + math.pow(third_point_y - second_point_y, 2)))
        x_l1 = float((second_point_x - first_point_x) / dist1)
        y_l1 = float((second_point_y - first_point_y) / dist1)
        x_l2 = float((third_point_x - second_point_x) / dist2)
        y_l2 = float((third_point_y - second_point_y) / dist2)
        if tool_radius * (y_l2 * x_l1 - y_l1 * x_l2) >= 0:
            if i == len(x_values):
                x = second_point_x - tool_radius * y_l1
                y = second_point_y + tool_radius * x_l1
            else:
                x = tool_radius * (x_l2 - x_l1) / (x_l1 * y_l2 - x_l2 * y_l1) + second_point_x
                y = tool_radius * (y_l2 - y_l1) / (x_l1 * y_l2 - x_l2 * y_l1) + second_point_y
            offsets.append((x, y))
            if len(offsets) >= 2:
                if (x - offsets[i - 4][0]) * (second_point_x - first_point_x) < 0:
                    guoqie = True
                    # break
        elif tool_radius * (y_l2 * x_l1 - y_l1 * x_l2) < 0 <= y_l1 * y_l2 + x_l1 * x_l2:
            if i == len(x_values):
                x1 = tool_radius * (x_l2 - x_l1) / (x_l1 * y_l2 - x_l2 * y_l1) + second_point_x
                y1 = tool_radius * (y_l2 - y_l1) / (x_l1 * y_l2 - x_l2 * y_l1) + second_point_y
                x2 = second_point_x - tool_radius * y_l2
                y2 = second_point_y + tool_radius * x_l2
                offsets.append((x1, y1))
                offsets.append((x2, y2))
            else:
                x = tool_radius * (x_l2 - x_l1) / (x_l1 * y_l2 - x_l2 * y_l1) + second_point_x
                y = tool_radius * (y_l2 - y_l1) / (x_l1 * y_l2 - x_l2 * y_l1) + second_point_y
                offsets.append((x, y))
        elif tool_radius * (y_l2 * x_l1 - y_l1 * x_l2) < 0 < y_l1 * y_l2 + x_l1 * x_l2:
            x1 = second_point_x - tool_radius * y_l1
            y1 = second_point_y + tool_radius * x_l1
            x2 = math.fabs(tool_radius) * x_l1 + x1
            y2 = math.fabs(tool_radius) * y_l1 + y1
            x3 = second_point_x - tool_radius * y_l2 - math.fabs(tool_radius) * x_l2
            y3 = second_point_y + tool_radius * x_l2 - math.fabs(tool_radius) * y_l2
            offsets.append((x1, y1))
            offsets.append((x2, y2))
            offsets.append((x3, y3))

        first_point_x = second_point_x
        first_point_y = second_point_y
        second_point_x = third_point_x
        second_point_y = third_point_y
        third_point_x = x_values[i]
        third_point_y = y_values[i]

    offsets.append((offsets[0]))
    if guoqie and direction == 'left':
        left = int(len(offsets) * 3 / 8)
        right = int(len(offsets) * 5 / 8)
        while offsets[left][1] >= offsets[left + 1][1]:
            left += 1
        while offsets[right - 1][1] <= offsets[right][1]:
            right -= 1
        while left + 1 != right:
            del offsets[left + 1]
            right -= 1
        offsets.insert(left + 1, (offsets[left][0], offsets[left][1] - tool_radius))
        offsets.insert(left + 2, (offsets[left + 2][0], offsets[left + 2][1] - tool_radius))
    return zip(*offsets)

# 绘制心脏线和刀具中心轨迹
def plot_heart_curve_with_tool_path(x_values, y_values, tool_radius, direction):
    offset_x, offset_y = offset_curve(x_values, y_values, tool_radius, direction)
    offset_x = list(offset_x)
    offset_y = list(offset_y)
    if direction == 'left':
        while offset_x[0] < 0:
            del offset_x[0]
            del offset_y[0]
        while True:
            num = len(offset_x) - 1
            if offset_x[num] > 0 or offset_y[num] < offset_y[0]:
                del offset_x[num]
                del offset_y[num]
            else:
                break
        return offset_x, offset_y

    elif direction == 'right':
        left = int(len(offset_x) / 4)
        right = int(len(offset_x) * 3 / 4)
        while left != right:
            if offset_x[left] > 0:
                left += 1
            else:
                break
        while left != right:
            if offset_x[right] < 0:
                right -= 1
            else:
                break
        del offset_x[left: right]
        del offset_y[left: right]
        while True:
            num = len(offset_x) - 1
            if num <= 0:
                msg_box = QMessageBox()
                msg_box.setWindowTitle("过切警告")
                msg_box.setText("刀具半径过大造成过切，请减小刀具半径")
                msg_box.exec()
                break
            if offset_x[num] > 0 or offset_y[num] <= offset_y[0]:
                del offset_x[num]
                del offset_y[num]
            else:
                break
        return offset_x, offset_y

