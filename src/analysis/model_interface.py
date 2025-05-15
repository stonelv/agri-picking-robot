class ModelInterface:
    def __init__(self, model_api_endpoint):
        self.model_api_endpoint = model_api_endpoint

    def send_frame(self, frame):
        """
        将图像帧发送到百度EasyDL/飞桨目标检测API，返回检测结果。
        """
        import requests
        import cv2
        import base64
        import json
        # 1. 将frame编码为jpg并转base64
        _, buffer = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        # 2. 构造API请求
        headers = {'Content-Type': 'application/json'}
        data = {
            'image': img_base64
        }
        # 3. 发送POST请求
        response = requests.post(self.model_api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            self._last_result = result
            return result
        else:
            print(f"Model API request failed: {response.status_code}, {response.text}")
            self._last_result = None
            return None

    def analyze_frame(self, frame):
        """
        发送图像帧并返回检测到的坐标信息。
        假设API返回格式为{'results': [{'name': 'tomato', 'score': 0.98, 'bbox': [x1, y1, x2, y2]}]}
        """
        result = self.send_frame(frame)
        if not result or 'results' not in result:
            return []
        coords = []
        for obj in result['results']:
            if obj.get('name') == 'tomato' and obj.get('score', 0) > 0.7:
                # 取检测框中心点
                bbox = obj['bbox']
                x = (bbox[0] + bbox[2]) / 2
                y = (bbox[1] + bbox[3]) / 2
                coords.append({'x': x, 'y': y, 'bbox': bbox, 'score': obj['score']})
        return coords