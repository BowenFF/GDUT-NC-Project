import numpy as np
import matplotlib.pyplot as plt
import cv2
from PyQt6.QtWidgets import QMessageBox

# 根据刀具半径和方向偏移曲线
def offset_curve(x_values, y_values, tool_radius, direction='left'):
    offsets = []
    overcut_detected = False

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

    # if overcut_detected:
    #     print("Warning: Overcut detected. Please reduce the tool radius.")

    return zip(*offsets)  # 返回X和Y的偏移坐标


# 使用OpenCV检测过切
def contour_contains(outer_contour, inner_contour):
    polygon_pts = np.array(outer_contour, np.float32)
    # 遍历内部轮廓的每个点
    for pt in inner_contour:
        pt.shape = (1, len(pt))
        # 使用pointPolygonTest判断点是否在多边形内
        # 如果点在多边形内，返回正值；在多边形上，返回0；在多边形外，返回负值
        if cv2.pointPolygonTest(polygon_pts, tuple(pt[0]), False) < 0:
            # 如果内部轮廓的任何一个点不在外部轮廓内，则外部轮廓不包含内部轮廓
            return False

            # 所有内部轮廓的点都在外部轮廓内，所以外部轮廓包含内部轮廓
    return True


# 绘制心脏线和刀具中心轨迹
def plot_heart_curve_with_tool_path(x_values, y_values, tool_radius, direction):
    offset_x, offset_y = offset_curve(x_values, y_values, tool_radius, direction)
    offset_x = list(offset_x)
    offset_y = list(offset_y)
    ori_points_x = np.array([x_values])
    ori_points_y = np.array([y_values])

    ori_points = np.concatenate((ori_points_x, ori_points_y), axis=0)
    ori_points = ori_points.T
    outer_contour = np.array([])
    inner_contour = np.array([])
    if direction == 'left':
        while True:
            if offset_x[0] < 0:
                del offset_x[0]
                del offset_y[0]
            else:
                break
        while True:
            num = len(offset_x) - 1
            if offset_x[num] > 0:
                del offset_x[num]
                del offset_y[num]
            else:
                break
        inner_contour = ori_points
        offset_x_array = np.array([offset_x])
        offset_y_array = np.array([offset_y])
        outer_contour = np.concatenate((offset_x_array, offset_y_array), axis=0)
        outer_contour = outer_contour.T
        if not contour_contains(outer_contour, inner_contour):
            msg_box = QMessageBox()
            msg_box.setWindowTitle("过切警告")
            msg_box.setText("刀具半径过大造成过切，请减小刀具半径")
            msg_box.exec()
        else:
            return offset_x_array.flatten(), offset_y_array.flatten()

    elif direction == 'right':
        offset_x.append(0)
        offset_y.append(y_values[0] - tool_radius)
        offset_x.append(offset_x[0])
        offset_y.append(offset_y[0])
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
        outer_contour = ori_points
        offset_x_array = np.array([offset_x])
        offset_y_array = np.array([offset_y])
        inner_contour = np.concatenate((offset_x_array, offset_y_array), axis=0)
        inner_contour = inner_contour.T
        if not contour_contains(outer_contour, inner_contour):
            msg_box = QMessageBox()
            msg_box.setWindowTitle("过切警告")
            msg_box.setText("刀具半径过大造成过切，请减小刀具半径")
            msg_box.exec()
        else:
            return offset_x_array.flatten(), offset_y_array.flatten()

