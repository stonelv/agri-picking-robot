import requests
import cv2
import base64
import json
import time

# 添加项目根目录到Python路径
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config.settings import settings
from dashscope import Generation


class ModelInterface:
    """模型接口类，用于与目标检测模型进行交互"""
    
    def __init__(self):
        """初始化模型接口"""
        self.model_api_endpoint = settings.model.api_endpoint
        self.confidence_threshold = settings.model.confidence_threshold
        self.target_classes = settings.model.target_classes
        self._last_result = None
        
        # 初始化阿里通义API客户端
        Generation.api_key = settings.model.api_key
        
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
            
            # 构造阿里通义API请求
            messages = [
                {
                    'role': 'user',
                    'content': [
                        {
                            'text': f"请分析这张农业采摘场景的景深图像，识别出{','.join(self.target_classes)}的位置，并返回它们的坐标。"
                        },
                        {
                            'image': img_base64
                        }
                    ]
                }
            ]
            
            # 发送请求
            response = Generation.call(
                model=Generation.Models.qwen_plus,
                messages=messages,
                result_format='message',
                timeout=settings.model.timeout
            )
            
            if response.status_code == 200:
                # 解析响应
                if hasattr(response.output, 'choices') and len(response.output.choices) > 0:
                    choice = response.output.choices[0]
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        result = choice.message.content
                        # 尝试解析JSON格式的结果
                        try:
                            result_json = json.loads(result)
                            self._last_result = result_json
                            return result_json
                        except json.JSONDecodeError:
                            # 如果结果不是JSON格式，尝试提取其中的JSON部分
                            import re
                            json_match = re.search(r'\{.*\}', result, re.DOTALL)
                            if json_match:
                                try:
                                    result_json = json.loads(json_match.group())
                                    self._last_result = result_json
                                    return result_json
                                except json.JSONDecodeError:
                                    print(f"无法解析模型返回的JSON部分: {json_match.group()}")
                                    self._last_result = None
                                    return None
                            else:
                                print(f"无法解析模型返回的结果: {result}")
                                self._last_result = None
                                return None
                    else:
                        print(f"模型API返回结果格式不正确，缺少message或content字段: {choice}")
                        self._last_result = None
                        return None
                else:
                    print(f"模型API返回结果格式不正确: {response.output}")
                    self._last_result = None
                    return None
            else:
                print(f"模型API请求失败: {response.status_code}, {response.message}")
                self._last_result = None
                return None
                
        except Exception as e:
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
        
        if not result:
            return []
            
        coords = []
        
        # 处理不同格式的返回结果
        if 'detections' in result:
            detections = result['detections']
        elif 'results' in result:
            detections = result['results']
        else:
            print(f"模型返回结果格式不正确，缺少'detections'或'results'字段: {result}")
            return []
            
        for obj in detections:
            # 检查目标类别和置信度
            class_name = obj.get('class') or obj.get('name')
            confidence = obj.get('score', 0)
            
            if class_name in self.target_classes and confidence > self.confidence_threshold:
                # 取检测框中心点
                bbox = obj.get('bbox', [0, 0, 0, 0])
                x = (bbox[0] + bbox[2]) / 2
                y = (bbox[1] + bbox[3]) / 2
                z = obj.get('depth', 0.0)
                
                # 如果没有深度信息，尝试从其他字段获取
                if z == 0.0:
                    z = obj.get('distance', 0.0)
                
                # 如果仍然没有深度信息，使用默认值
                if z == 0.0:
                    z = 0.5  # 默认深度为0.5米
                    print(f"目标{class_name}缺少深度信息，使用默认值{z}米")
                
                # 将坐标转换为原始图像尺寸
                scale_x = frame.shape[1] / settings.model.input_width
                scale_y = frame.shape[0] / settings.model.input_height
                x *= scale_x
                y *= scale_y
                
                coords.append({
                    'x': x,
                    'y': y,
                    'z': z,
                    'bbox': [bbox[0] * scale_x, bbox[1] * scale_y, bbox[2] * scale_x, bbox[3] * scale_y],
                    'score': confidence,
                    'class': class_name
                })
                
        return coords


# 测试代码
if __name__ == "__main__":
    import numpy as np
    
    # 创建一个示例图像（模拟景深图像）
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # 在图像中添加几个模拟的水果
    cv2.rectangle(frame, (100, 100), (200, 200), (0, 255, 0), 2)  # 绿色表示苹果
    cv2.circle(frame, (320, 240), 50, (0, 0, 255), -1)  # 红色表示番茄
    cv2.ellipse(frame, (500, 300), (40, 60), 0, 0, 360, (0, 165, 255), -1)  # 橙色表示橙子
    
    # 初始化模型接口
    model_interface = ModelInterface()
    
    # 分析图像
    results = model_interface.analyze_frame(frame)
    
    # 打印结果
    print(f"检测到 {len(results)} 个目标")
    for i, result in enumerate(results):
        print(f"目标 {i+1}: 类别={result['class']}, 置信度={result['score']:.2f}, 坐标=({result['x']:.2f}, {result['y']:.2f}, {result['z']:.2f}米)")
        print(f"  边界框: ({result['bbox'][0]:.2f}, {result['bbox'][1]:.2f}, {result['bbox'][2]:.2f}, {result['bbox'][3]:.2f})")