import requests
import cv2
import base64
import json
from config.settings import settings


class ModelInterface:
    """模型接口类，用于与目标检测模型进行交互"""
    
    def __init__(self):
        """初始化模型接口"""
        self.model_api_endpoint = settings.model.api_endpoint
        self.confidence_threshold = settings.model.confidence_threshold
        self.target_classes = settings.model.target_classes
        self._last_result = None
        
    def send_frame(self, frame):
        """将图像帧发送到目标检测API，返回检测结果
        
        参数:
            frame: 输入的图像帧，BGR格式的numpy数组
            
        返回:
            如果成功，返回包含检测结果的字典；否则返回None
        """
        try:
            # 将frame编码为jpg并转base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # 构造API请求
            headers = {'Content-Type': 'application/json'}
            data = {
                'image': img_base64
            }
            
            # 发送POST请求
            response = requests.post(self.model_api_endpoint, headers=headers, data=json.dumps(data),
                                  timeout=settings.model.timeout)
            
            if response.status_code == 200:
                result = response.json()
                self._last_result = result
                return result
            else:
                print(f"模型API请求失败: {response.status_code}, {response.text}")
                self._last_result = None
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"模型API请求异常: {str(e)}")
            self._last_result = None
            return None
    
    def preprocess_frame(self, frame):
        """对输入的图像帧进行预处理，以满足模型输入要求
        
        参数:
            frame: 输入的图像帧，BGR格式的numpy数组
            
        返回:
            预处理后的图像帧
        """
        # 调整图像大小
        preprocessed_frame = cv2.resize(frame, (settings.model.input_width, settings.model.input_height))
        
        # 归一化处理
        preprocessed_frame = preprocessed_frame.astype('float32') / 255.0
        preprocessed_frame -= settings.model.normalization_mean
        preprocessed_frame /= settings.model.normalization_std
        
        return preprocessed_frame
    
    def analyze_frame(self, frame):
        """分析图像帧，检测目标并返回坐标信息
        
        参数:
            frame: 输入的图像帧，BGR格式的numpy数组
            
        返回:
            包含检测到的目标信息的列表，每个目标信息包括坐标、边界框和置信度
        """
        # 对图像帧进行预处理
        preprocessed_frame = self.preprocess_frame(frame)
        
        # 发送图像帧到模型API
        result = self.send_frame(preprocessed_frame)
        
        if not result or 'results' not in result:
            return []
            
        coords = []
        for obj in result['results']:
            # 检查目标类别和置信度
            if obj.get('name') in self.target_classes and obj.get('score', 0) > self.confidence_threshold:
                # 取检测框中心点
                bbox = obj['bbox']
                x = (bbox[0] + bbox[2]) / 2
                y = (bbox[1] + bbox[3]) / 2
                
                # 将坐标转换为原始图像尺寸
                scale_x = frame.shape[1] / settings.model.input_width
                scale_y = frame.shape[0] / settings.model.input_height
                x *= scale_x
                y *= scale_y
                
                coords.append({
                    'x': x,
                    'y': y,
                    'bbox': [bbox[0] * scale_x, bbox[1] * scale_y, bbox[2] * scale_x, bbox[3] * scale_y],
                    'score': obj['score'],
                    'class': obj['name']
                })
                
        return coords


# 测试代码
if __name__ == "__main__":
    import numpy as np
    
    # 创建一个示例图像
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(frame, (100, 100), (200, 200), (0, 255, 0), 2)
    
    # 初始化模型接口
    model_interface = ModelInterface()
    
    # 分析图像
    results = model_interface.analyze_frame(frame)
    
    # 打印结果
    print(f"检测到 {len(results)} 个目标")
    for i, result in enumerate(results):
        print(f"目标 {i+1}: 类别={result['class']}, 置信度={result['score']:.2f}, 坐标=({result['x']:.2f}, {result['y']:.2f})")