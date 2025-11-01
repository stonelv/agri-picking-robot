import cv2
import numpy as np

# Mock the Orbbec camera SDK for testing purposes
class MockDevice:
    def __init__(self, device_id=None):
        self.device_id = device_id
        self.started = False
        
    def start(self):
        self.started = True
        print("Mock camera started")
        
    def get_stream_profiles(self, profile_type):
        class MockStreamProfile:
            def __init__(self, width, height, fps):
                self.width = width
                self.height = height
                self.fps = fps
                self.format = "RGB"
                
        return [MockStreamProfile(640, 480, 30)]
        
    def start_stream(self, profile):
        print(f"Mock stream started with {profile.width}x{profile.height}@{profile.fps}")
        return "mock_stream"
        
    def create_align(self, align_to):
        class MockAlignHandle:
            def process(self, frameset):
                return frameset
                
        return MockAlignHandle()
        
    def stop(self):
        self.started = False
        print("Mock camera stopped")
        
    def wait_for_frames(self, timeout_ms):
        class MockFrame:
            def __init__(self, width, height, is_depth=False):
                self.width = width
                self.height = height
                self.is_depth = is_depth
                
            def get_data(self):
                # Create a mock image
                if self.is_depth:
                    # Depth image with a gradient
                    return np.linspace(0, 1000, self.width * self.height, dtype=np.uint16).reshape(self.height, self.width)
                else:
                    # Color image with a blue background
                    return np.zeros((self.height, self.width, 3), dtype=np.uint8) + [255, 0, 0]
                    
            def get_timestamp(self):
                return time.time() * 1000  # Current time in milliseconds
                
        frameset = MockFrameSet()
        frameset.color_frame = MockFrame(640, 480, is_depth=False)
        frameset.depth_frame = MockFrame(640, 480, is_depth=True)
        return frameset
        
    def get_intrinsics(self, profile_type):
        class MockIntrinsics:
            def __init__(self):
                self.fx = 500.0
                self.fy = 500.0
                self.cx = 320.0
                self.cy = 240.0
                self.width = 640
                self.height = 480
                
        return MockIntrinsics()
        
    def set_exposure_time(self, exposure_time_us):
        print(f"Mock exposure time set to {exposure_time_us} us")
        
    def set_gain(self, gain):
        print(f"Mock gain set to {gain}")
        
    def stop_stream(self, stream):
        print(f"Mock stream stopped: {stream}")
        
    def destroy(self):
        print("Mock device destroyed")

class MockFrameSet:
    def __init__(self):
        self.color_frame = None
        self.depth_frame = None
        
    def get_color_frame(self):
        return self.color_frame
        
    def get_depth_frame(self):
        return self.depth_frame

# Use mock classes instead of real Orbbec SDK
Device = MockDevice
StreamProfile = type('MockStreamProfile', (), {})
FrameSet = MockFrameSet

class Gemini335:
    """Gemini335深度相机的Python实现，基于Orbbec SDK v2
    
    该类提供了Gemini335相机的基本控制功能，包括：
    - 相机初始化和关闭
    - 彩色图像和深度图像的捕捉
    - 相机参数配置
    - 错误处理和异常情况处理
    """
    
    def __init__(self, device_id=None, color_width=640, color_height=480, color_fps=30,
                 depth_width=640, depth_height=480, depth_fps=30):
        """初始化相机参数
        
        参数:
            device_id: 设备ID，如果有多个相机连接，可以指定特定相机
            color_width: 彩色图像宽度，默认640
            color_height: 彩色图像高度，默认480
            color_fps: 彩色图像帧率，默认30
            depth_width: 深度图像宽度，默认640
            depth_height: 深度图像高度，默认480
            depth_fps: 深度图像帧率，默认30
        """
        self.device_id = device_id
        self.color_width = color_width
        self.color_height = color_height
        self.color_fps = color_fps
        self.depth_width = depth_width
        self.depth_height = depth_height
        self.depth_fps = depth_fps
        
        self.device = None
        self.color_stream = None
        self.depth_stream = None
        self.align_handle = None
        
    def initialize_camera(self):
        """初始化相机设备和流
        
        尝试连接到相机设备，并配置彩色和深度流。如果连接失败，将抛出异常。
        """
        try:
            # 创建设备实例
            if self.device_id:
                self.device = Device(self.device_id)
            else:
                self.device = Device()
            
            # 启动设备
            self.device.start()
            
            # 配置彩色流
            color_profiles = self.device.get_stream_profiles(StreamProfile.Type.COLOR)
            color_profile = None
            for profile in color_profiles:
                if (profile.width == self.color_width and 
                    profile.height == self.color_height and 
                    profile.fps == self.color_fps):
                    color_profile = profile
                    break
            
            if not color_profile:
                # 如果找不到指定参数的配置，使用第一个可用配置
                color_profile = color_profiles[0]
                print(f"警告：找不到指定的彩色流配置，使用默认配置: {color_profile.width}x{color_profile.height}@{color_profile.fps}")
            
            # 配置深度流
            depth_profiles = self.device.get_stream_profiles(StreamProfile.Type.DEPTH)
            depth_profile = None
            for profile in depth_profiles:
                if (profile.width == self.depth_width and 
                    profile.height == self.depth_height and 
                    profile.fps == self.depth_fps):
                    depth_profile = profile
                    break
            
            if not depth_profile:
                # 如果找不到指定参数的配置，使用第一个可用配置
                depth_profile = depth_profiles[0]
                print(f"警告：找不到指定的深度流配置，使用默认配置: {depth_profile.width}x{depth_profile.height}@{depth_profile.fps}")
            
            # 启动彩色和深度流
            self.color_stream = self.device.start_stream(color_profile)
            self.depth_stream = self.device.start_stream(depth_profile)
            
            # 创建对齐句柄，将深度图像与彩色图像对齐
            self.align_handle = self.device.create_align(StreamProfile.Type.COLOR)
            
            print("相机初始化成功")
            
        except Exception as e:
            print(f"相机初始化失败: {str(e)}")
            raise
    
    def capture_frame(self, align=True):
        """捕捉一帧图像
        
        参数:
            align: 是否将深度图像与彩色图像对齐，默认True
            
        返回:
            如果成功，返回包含彩色图像和深度图像的字典；否则返回None
        """
        try:
            if not self.device or not self.color_stream or not self.depth_stream:
                print("相机未初始化")
                return None
            
            # 等待帧
            frame_set = self.device.wait_for_frames(1000)
            if not frame_set:
                print("超时未获取到帧")
                return None
            
            # 获取彩色帧和深度帧
            color_frame = frame_set.get_color_frame()
            depth_frame = frame_set.get_depth_frame()
            
            if not color_frame or not depth_frame:
                print("未获取到完整的帧数据")
                return None
            
            # 将帧数据转换为numpy数组
            color_image = np.asarray(color_frame.get_data())
            depth_image = np.asarray(depth_frame.get_data())
            
            if align and self.align_handle:
                # 对齐深度图像与彩色图像
                aligned_depth_frame = self.align_handle.process(frame_set)
                depth_image = np.asarray(aligned_depth_frame.get_data())
            
            # 确保彩色图像格式正确
            if color_image.shape[2] == 3:
                color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            
            return {
                'color': color_image,
                'depth': depth_image,
                'color_timestamp': color_frame.get_timestamp(),
                'depth_timestamp': depth_frame.get_timestamp()
            }
            
        except Exception as e:
            print(f"捕捉帧失败: {str(e)}")
            return None
    
    def get_camera_intrinsics(self):
        """获取相机内参
        
        返回:
            包含彩色相机和深度相机内参的字典
        """
        if not self.device:
            print("相机未初始化")
            return None
            
        try:
            color_intrinsics = self.device.get_intrinsics(StreamProfile.Type.COLOR)
            depth_intrinsics = self.device.get_intrinsics(StreamProfile.Type.DEPTH)
            
            return {
                'color': {
                    'fx': color_intrinsics.fx,
                    'fy': color_intrinsics.fy,
                    'cx': color_intrinsics.cx,
                    'cy': color_intrinsics.cy,
                    'width': color_intrinsics.width,
                    'height': color_intrinsics.height
                },
                'depth': {
                    'fx': depth_intrinsics.fx,
                    'fy': depth_intrinsics.fy,
                    'cx': depth_intrinsics.cx,
                    'cy': depth_intrinsics.cy,
                    'width': depth_intrinsics.width,
                    'height': depth_intrinsics.height
                }
            }
            
        except Exception as e:
            print(f"获取相机内参失败: {str(e)}")
            return None
    
    def set_exposure(self, exposure_time_us):
        """设置相机曝光时间
        
        参数:
            exposure_time_us: 曝光时间，单位微秒
        """
        if not self.device:
            print("相机未初始化")
            return False
            
        try:
            self.device.set_exposure_time(exposure_time_us)
            return True
        except Exception as e:
            print(f"设置曝光时间失败: {str(e)}")
            return False
    
    def set_gain(self, gain):
        """设置相机增益
        
        参数:
            gain: 增益值，范围通常为1.0到16.0
        """
        if not self.device:
            print("相机未初始化")
            return False
            
        try:
            self.device.set_gain(gain)
            return True
        except Exception as e:
            print(f"设置增益失败: {str(e)}")
            return False
    
    def release_camera(self):
        """释放相机资源
        
        关闭相机流和设备，释放相关资源
        """
        try:
            if self.align_handle:
                self.align_handle.destroy()
                self.align_handle = None
                
            if self.color_stream:
                self.device.stop_stream(self.color_stream)
                self.color_stream = None
                
            if self.depth_stream:
                self.device.stop_stream(self.depth_stream)
                self.depth_stream = None
                
            if self.device:
                self.device.stop()
                self.device.destroy()
                self.device = None
                
            print("相机资源已释放")
            
        except Exception as e:
            print(f"释放相机资源失败: {str(e)}")
            
    def process_frame(self, frame):
        """帧处理示例
        
        参数:
            frame: 包含彩色图像和深度图像的字典
            
        返回:
            处理后的帧
        """
        if not frame:
            return None
            
        color_image = frame['color']
        depth_image = frame['depth']
        
        # 示例：将深度图像转换为伪彩色图像
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        
        # 示例：将彩色图像和深度图像拼接在一起
        combined_image = np.hstack((color_image, depth_colormap))
        
        return {
            'color': color_image,
            'depth': depth_image,
            'combined': combined_image,
            'color_timestamp': frame['color_timestamp'],
            'depth_timestamp': frame['depth_timestamp']
        }

# 测试代码
if __name__ == "__main__":
    camera = Gemini335()
    
    try:
        camera.initialize_camera()
        
        # 获取相机内参
        intrinsics = camera.get_camera_intrinsics()
        if intrinsics:
            print(f"彩色相机内参: fx={intrinsics['color']['fx']}, fy={intrinsics['color']['fy']}, cx={intrinsics['color']['cx']}, cy={intrinsics['color']['cy']}")
            print(f"深度相机内参: fx={intrinsics['depth']['fx']}, fy={intrinsics['depth']['fy']}, cx={intrinsics['depth']['cx']}, cy={intrinsics['depth']['cy']}")
        
        # 测试设置曝光时间和增益
        camera.set_exposure(10000)
        camera.set_gain(1.5)
        
        # 循环捕捉和显示帧
        while True:
            frame = camera.capture_frame()
            if frame:
                # 处理帧
                processed_frame = camera.process_frame(frame)
                
                # 显示图像
                cv2.imshow("Combined Image", processed_frame['combined'])
                
            # 按q键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"发生错误: {str(e)}")
        
    finally:
        camera.release_camera()
        cv2.destroyAllWindows()