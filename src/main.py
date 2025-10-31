import time
import cv2
from camera.gemini335 import Gemini335
from robot.arm_controller import ArmController
from robot.base_controller import BaseController
from analysis.model_interface import ModelInterface
from config.settings import Settings


def main():
    # Load settings
    settings = Settings()
    
    # Initialize camera
    camera = Gemini335(
        color_width=settings.camera.color_width,
        color_height=settings.camera.color_height,
        color_fps=settings.camera.color_fps,
        depth_width=settings.camera.depth_width,
        depth_height=settings.camera.depth_height,
        depth_fps=settings.camera.depth_fps
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
    arm_controller.connect()
    arm_controller.enable()
    
    base_controller = BaseController(
        wheel_radius=settings.robot.base_wheel_radius,
        wheel_separation=settings.robot.base_wheel_separation,
        base_speed=settings.robot.base_speed
    )

    # Initialize model interface
    model_interface = ModelInterface(model_api_endpoint=settings.model.api_endpoint)

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
            detected_objects = model_interface.analyze_frame(color_frame)
            
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
        arm_controller.disable()
        arm_controller.disconnect()
        base_controller.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()