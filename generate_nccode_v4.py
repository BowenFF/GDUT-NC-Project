def generate_nc_code(t_values, x_values, y_values, tool_radius, feed_rate, spindle_speed,
                     safety_height, cut_depth, start_point, compensation_direction,
                     use_relative_coordinates):
    nc_code = []

    # 初始化NC代码
    nc_code.append("%0001")

    # 设置坐标系和起刀点
    if use_relative_coordinates:
        # nc_code.append("G91")  # 使用相对坐标
        nc_code.append(f"N1 G91 G21 G40 M03 S{spindle_speed} F{feed_rate}")  # 在相对坐标下移动到起刀点（需要确保是相对于初始位置的偏移）
        nc_code.append(f"N2 G00 Z{safety_height}")
        start_x, start_y = start_point
        nc_code.append(f"N3 G91 G00 X{start_x} Y{start_y}")
        nc_code.append(f"N4 G01 Z-{cut_depth + safety_height}")  # 下刀到加工深度

        # 设置刀具补偿方向
        if compensation_direction == 'left':
            nc_code.append("N5 G41 D1")  # 左刀补
        elif compensation_direction == 'right':
            nc_code.append("N6 G42 D1")  # 右刀补
        # 遍历离散点并生成直线插补指令
        for i in range(len(t_values) - 1):
            xi, yi = x_values[i], y_values[i]
            xi_next, yi_next = x_values[i + 1], y_values[i + 1]

            if use_relative_coordinates:
                dx = xi_next - xi
                dy = yi_next - yi
                nc_code.append(f"N{i + 5} G01 X{dx:.4f} Y{dy:.4f}")  # 使用相对坐标进行直线插补
            else:
                nc_code.append(f"N{i + 5} G01 X{xi_next:.4f} Y{yi_next:.4f}")  # 使用绝对坐标进行直线插补
        if use_relative_coordinates:
            nc_code.append(f"N{len(t_values) + 5} G40 G00 Z{cut_depth + safety_height}")
        else:
            nc_code.append(f"N{len(t_values) + 5} G40 G00 Z{safety_height}")  # 快速定位到安全高度
        nc_code.append(f"N{len(t_values) + 6} M30")  # 程序结束
        return nc_code
    else:
        # nc_code.append("G90")  # 使用绝对坐标
        nc_code.append(f"N1 G92 X0 Y0")
        nc_code.append(f"N2 G90 G21 G40 M03 S{spindle_speed} F{feed_rate}")  # 在相对坐标下移动到起刀点（需要确保是相对于初始位置的偏移）
        nc_code.append(f"N3 G00 Z{safety_height}")
        start_x, start_y = start_point
        nc_code.append(f"N4 G90 G00 X{start_x} Y{start_y}")
        nc_code.append(f"N5 G01 Z-{cut_depth}")  # 下刀到加工深度

        # 设置刀具补偿方向
        if compensation_direction == 'left':
            nc_code.append("N6 G41 D1")  # 左刀补
        elif compensation_direction == 'right':
            nc_code.append("N7 G42 D1")  # 右刀补

        # 遍历离散点并生成直线插补指令
        for i in range(len(t_values) - 1):
            xi, yi = x_values[i], y_values[i]
            xi_next, yi_next = x_values[i + 1], y_values[i + 1]

            if use_relative_coordinates:
                dx = xi_next - xi
                dy = yi_next - yi
                nc_code.append(f"N{i + 7} G01 X{dx:.4f} Y{dy:.4f}")  # 使用相对坐标进行直线插补
            else:
                nc_code.append(f"N{i + 7} G01 X{xi_next:.4f} Y{yi_next:.4f}")  # 使用绝对坐标进行直线插补
        if use_relative_coordinates:
            nc_code.append(f"N{len(t_values) + 6} G40 G00 Z{cut_depth + safety_height}")
        else:
            nc_code.append(f"N{len(t_values) + 6} G40 G00 Z{safety_height}")  # 快速定位到安全高度
        nc_code.append(f"N{len(t_values) + 7} M30")  # 程序结束
        return nc_code

