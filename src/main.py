import time
import cv2
import numpy as np
from camera.gemini335 import Gemini335
from robot.arm_controller import ArmController
from robot.base_controller import BaseController
from analysis.model_interface import ModelInterface
from config.settings import Settings

class MockCamera:
    """模拟相机类，用于在没有实际相机设备的情况下测试项目"""
    def __init__(self, color_width=640, color_height=480, depth_width=640, depth_height=480):
        self.color_width = color_width
        self.color_height = color_height
        self.depth_width = depth_width
        self.depth_height = depth_height
        self.frame_count = 0
        
    def initialize_camera(self):
        """初始化模拟相机"""
        print("初始化模拟相机成功")
        return True
        
    def capture_frame(self, align=True):
        """捕捉模拟帧"""
        self.frame_count += 1
        
        # 创建模拟彩色图像（蓝色背景，中间有一个绿色方块）
        color_image = np.zeros((self.color_height, self.color_width, 3), dtype=np.uint8)
        color_image[:] = (255, 0, 0)  # 蓝色背景
        cv2.rectangle(color_image, (200, 150), (440, 330), (0, 255, 0), -1)  # 绿色方块
        
        # 创建模拟深度图像（中间深度值较小，周围深度值较大）
        depth_image = np.ones((self.depth_height, self.depth_width), dtype=np.uint16) * 1000
        cv2.rectangle(depth_image, (200, 150), (440, 330), 500, -1)
        
        return {
            'color': color_image,
            'depth': depth_image,
            'color_timestamp': time.time(),
            'depth_timestamp': time.time()
        }
        
    def get_camera_intrinsics(self):
        """获取模拟相机内参"""
        return {
            'color': {
                'fx': 600.0,
                'fy': 600.0,
                'cx': self.color_width / 2,
                'cy': self.color_height / 2,
                'width': self.color_width,
                'height': self.color_height
            },
            'depth': {
                'fx': 600.0,
                'fy': 600.0,
                'cx': self.depth_width / 2,
                'cy': self.depth_height / 2,
                'width': self.depth_width,
                'height': self.depth_height
            }
        }
        
    def release_camera(self):
        """释放模拟相机资源"""
        print("释放模拟相机资源")
        return True


def main():
    # Load settings
    settings = Settings()
    
    # Initialize camera
    camera = None
    try:
        camera = Gemini335(
            color_width=settings.camera.color_width,
            color_height=settings.camera.color_height,
            color_fps=settings.camera.color_fps,
            depth_width=settings.camera.depth_width,
            depth_height=settings.camera.depth_height,
            depth_fps=settings.camera.depth_fps
        )
        camera.initialize_camera()
        print("使用实际相机设备")
    except Exception as e:
        print(f"实际相机初始化失败: {str(e)}")
        print("切换到模拟相机模式")
        camera = MockCamera(
            color_width=settings.camera.color_width,
            color_height=settings.camera.color_height,
            depth_width=settings.camera.depth_width,
            depth_height=settings.camera.depth_height
        )
        camera.initialize_camera()

    # Initialize robot controllers
    arm_controller = ArmController(
        ip=settings.robot.arm_ip,
        default_vel=settings.robot.arm_default_velocity,
        default_acc=settings.robot.arm_default_acceleration,
        gripper_open_time=settings.robot.arm_gripper_open_time,
        gripper_close_time=settings.robot.arm_gripper_close_time,
        approach_offset=settings.robot.arm_approach_offset
    )
    
    try:
        arm_controller.connect()
        arm_controller.enable()
        print("机械臂初始化成功")
    except Exception as e:
        print(f"机械臂初始化失败: {str(e)}")
        arm_controller = None
    
    base_controller = BaseController(
        wheel_radius=settings.robot.base_wheel_radius,
        wheel_separation=settings.robot.base_wheel_separation,
        base_speed=settings.robot.base_speed
    )
    print("基础车辆初始化成功")

    # Initialize model interface
    model_interface = ModelInterface()

    try:
        while True:
            # Capture video frame
            frame = camera.capture_frame()
            
            if not frame:
                print("未获取到有效帧，跳过本次循环")
                time.sleep(0.1)
                continue
                
            # 获取彩色图像用于分析
            color_frame = frame['color']

            # Process frame and get detected objects
            try:
                detected_objects = model_interface.analyze_frame(color_frame)
            except Exception as e:
                print(f"模型分析失败: {str(e)}")
                detected_objects = None
            
            # 如果检测到目标，执行采摘操作
            if detected_objects:
                # 假设取第一个检测到的目标
                target = detected_objects[0]
                
                # 将图像坐标转换为世界坐标
                # 这里需要根据相机内参和深度信息进行转换
                # 简化处理，假设已经有转换后的坐标
                world_x = target['x']
                world_y = target['y']
                world_z = frame['depth'][int(target['y']), int(target['x'])] / 1000.0  # 转换为米
                
                # 移动机械臂到目标位置
                if arm_controller:
                    try:
                        arm_controller.move_to([world_x, world_y, world_z, 0, 0, 0])
                        
                        # 执行采摘操作
                        # 这里需要根据实际的夹爪控制逻辑进行调整
                        # 假设pick_pos是目标位置，place_pos是放置位置
                        arm_controller.pick(
                            pick_pos=[world_x, world_y, world_z, 0, 0, 0],
                            place_pos=[0.5, 0, 0.5, 0, 0, 0]  # 示例放置位置
                        )
                        
                        # 重置机械臂到初始位置
                        arm_controller.calibrate()
                    except Exception as e:
                        print(f"机械臂操作失败: {str(e)}")
                else:
                    print("机械臂未初始化，无法执行采摘操作")
                
                # 移动基础车辆
                base_controller.move_forward(0.1)  # 移动0.1米
            else:
                # 如果没有检测到目标，移动基础车辆继续搜索
                base_controller.move_forward(0.1)
            
            # Sleep to control the loop rate
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Shutting down the robot control program.")

    finally:
        # 释放资源
        camera.release_camera()
        if arm_controller:
            try:
                arm_controller.disable()
                arm_controller.disconnect()
            except Exception as e:
                print(f"释放机械臂资源失败: {str(e)}")
        base_controller.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()