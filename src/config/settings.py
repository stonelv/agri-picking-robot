CAMERA_SETTINGS = {
    "resolution": (640, 480),
    "frame_rate": 30,
    "depth_mode": "high",
}

ROBOT_SETTINGS = {
    "arm_length": 1.0,  # in meters
    "base_speed": 0.5,  # in meters per second
    "turning_radius": 0.5,  # in meters
}

MODEL_SETTINGS = {
    "api_endpoint": "http://localhost:5000/predict",
    "timeout": 5,  # in seconds
}

LOGGING_SETTINGS = {
    "log_file": "robot_log.txt",
    "log_level": "DEBUG",
}