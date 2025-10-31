class BaseController:
    def __init__(self, wheel_radius=0.1, wheel_separation=0.5, base_speed=0.5):
        self.wheel_radius = wheel_radius  # 车轮半径，单位米
        self.wheel_separation = wheel_separation  # 车轮间距，单位米
        self.base_speed = base_speed  # 基础速度，单位米/秒
        self.current_speed = 0.0  # 当前速度，单位米/秒
        self.current_angular_speed = 0.0  # 当前角速度，单位弧度/秒
        
    def move_forward(self, distance, speed=None):
        """
        控制基础车辆向前移动指定距离
        distance: 移动距离，单位米
        speed: 移动速度，单位米/秒，默认使用基础速度
        """
        speed = speed if speed is not None else self.base_speed
        # 确保速度不超过基础速度
        speed = min(speed, self.base_speed)
        
        # 计算移动所需时间
        if speed == 0:
            print("速度为0，无法移动")
            return
        
        time = distance / speed
        print(f"向前移动{distance}米，速度{speed}米/秒，预计耗时{time:.2f}秒")
        
        # 这里应该添加实际的移动控制代码
        # 例如：发送命令到硬件控制器
        self.current_speed = speed
        # 模拟移动过程
        import time as t
        t.sleep(time)
        self.current_speed = 0.0
        
    def move_backward(self, distance, speed=None):
        """
        控制基础车辆向后移动指定距离
        distance: 移动距离，单位米
        speed: 移动速度，单位米/秒，默认使用基础速度
        """
        speed = speed if speed is not None else self.base_speed
        # 确保速度不超过基础速度
        speed = min(speed, self.base_speed)
        
        # 计算移动所需时间
        if speed == 0:
            print("速度为0，无法移动")
            return
        
        time = distance / speed
        print(f"向后移动{distance}米，速度{speed}米/秒，预计耗时{time:.2f}秒")
        
        # 这里应该添加实际的移动控制代码
        # 例如：发送命令到硬件控制器
        self.current_speed = -speed
        # 模拟移动过程
        import time as t
        t.sleep(time)
        self.current_speed = 0.0
        
    def turn_left(self, angle, angular_speed=None):
        """
        控制基础车辆向左转指定角度
        angle: 转动角度，单位度
        angular_speed: 角速度，单位度/秒，默认使用最大角速度
        """
        # 转换角度为弧度
        angle_rad = angle * 3.1415926535 / 180
        
        # 计算最大角速度
        max_angular_speed = (2 * self.base_speed) / self.wheel_separation  # 弧度/秒
        max_angular_speed_deg = max_angular_speed * 180 / 3.1415926535  # 转换为度/秒
        
        angular_speed = angular_speed if angular_speed is not None else max_angular_speed_deg
        # 确保角速度不超过最大值
        angular_speed = min(angular_speed, max_angular_speed_deg)
        
        # 转换角速度为弧度/秒
        angular_speed_rad = angular_speed * 3.1415926535 / 180
        
        # 计算转动所需时间
        if angular_speed_rad == 0:
            print("角速度为0，无法转动")
            return
        
        time = angle_rad / angular_speed_rad
        print(f"向左转{angle}度，角速度{angular_speed}度/秒，预计耗时{time:.2f}秒")
        
        # 这里应该添加实际的转动控制代码
        # 例如：发送命令到硬件控制器
        self.current_angular_speed = angular_speed_rad
        # 模拟转动过程
        import time as t
        t.sleep(time)
        self.current_angular_speed = 0.0
        
    def turn_right(self, angle, angular_speed=None):
        """
        控制基础车辆向右转指定角度
        angle: 转动角度，单位度
        angular_speed: 角速度，单位度/秒，默认使用最大角速度
        """
        # 转换角度为弧度
        angle_rad = angle * 3.1415926535 / 180
        
        # 计算最大角速度
        max_angular_speed = (2 * self.base_speed) / self.wheel_separation  # 弧度/秒
        max_angular_speed_deg = max_angular_speed * 180 / 3.1415926535  # 转换为度/秒
        
        angular_speed = angular_speed if angular_speed is not None else max_angular_speed_deg
        # 确保角速度不超过最大值
        angular_speed = min(angular_speed, max_angular_speed_deg)
        
        # 转换角速度为弧度/秒
        angular_speed_rad = angular_speed * 3.1415926535 / 180
        
        # 计算转动所需时间
        if angular_speed_rad == 0:
            print("角速度为0，无法转动")
            return
        
        time = angle_rad / angular_speed_rad
        print(f"向右转{angle}度，角速度{angular_speed}度/秒，预计耗时{time:.2f}秒")
        
        # 这里应该添加实际的转动控制代码
        # 例如：发送命令到硬件控制器
        self.current_angular_speed = -angular_speed_rad
        # 模拟转动过程
        import time as t
        t.sleep(time)
        self.current_angular_speed = 0.0
        
    def stop(self):
        """
        停止基础车辆
        """
        print("停止基础车辆")
        # 这里应该添加实际的停止控制代码
        # 例如：发送命令到硬件控制器
        self.current_speed = 0.0
        self.current_angular_speed = 0.0