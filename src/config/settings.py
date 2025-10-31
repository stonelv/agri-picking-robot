class CameraSettings:
    """相机设置类"""
    def __init__(self):
        self.resolution = (640, 480)
        self.frame_rate = 30
        self.depth_mode = "high"
        
        # 新增详细参数
        self.color_width = 640
        self.color_height = 480
        self.color_fps = 30
        self.depth_width = 640
        self.depth_height = 480
        self.depth_fps = 30
        
        # 相机内参（示例值，需要根据实际校准结果修改）
        self.color_intrinsics = {
            'fx': 615.0,
            'fy': 615.0,
            'cx': 320.0,
            'cy': 240.0
        }
        
        self.depth_intrinsics = {
            'fx': 615.0,
            'fy': 615.0,
            'cx': 320.0,
            'cy': 240.0
        }


class RobotSettings:
    """机器人设置类"""
    def __init__(self):
        self.arm_length = 1.0  # in meters
        self.base_speed = 0.5  # in meters per second
        self.turning_radius = 0.5  # in meters
        
        # 机械臂相关设置
        self.arm_ip = "192.168.58.2"
        self.arm_default_velocity = 20.0  # 速度百分比
        self.arm_default_acceleration = 50.0  # 加速度百分比
        self.arm_gripper_open_time = 0.5  # 夹爪打开时间，单位秒
        self.arm_gripper_close_time = 0.5  # 夹爪关闭时间，单位秒
        self.arm_approach_offset = 50  # 接近目标时的偏移量，单位毫米
        
        # 基础车辆相关设置
        self.base_wheel_radius = 0.1  # 车轮半径，单位米
        self.base_wheel_separation = 0.5  # 车轮间距，单位米


class ModelSettings:
    """模型设置类"""
    def __init__(self):
        self.api_endpoint = "http://localhost:5000/predict"
        self.timeout = 5  # in seconds
        
        # 目标检测相关设置
        self.confidence_threshold = 0.7  # 置信度阈值
        self.target_classes = ["tomato", "apple", "orange"]  # 目标类别
        
        # 模型输入设置
        self.input_width = 640
        self.input_height = 640
        self.normalization_mean = [0.485, 0.456, 0.406]
        self.normalization_std = [0.229, 0.224, 0.225]


class LoggingSettings:
    """日志设置类"""
    def __init__(self):
        self.log_file = "robot_log.txt"
        self.log_level = "DEBUG"
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5  # 保留5个备份文件


class Settings:
    """总设置类"""
    def __init__(self):
        self.camera = CameraSettings()
        self.robot = RobotSettings()
        self.model = ModelSettings()
        self.logging = LoggingSettings()


# 全局设置实例
settings = Settings()