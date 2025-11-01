import sys
import os
import time

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print('Starting component test...')

# Test Settings
try:
    from config.settings import Settings
    settings = Settings()
    print('✓ Settings initialized successfully')
except Exception as e:
    print(f'✗ Failed to initialize Settings: {e}')
    sys.exit(1)

# Test Camera
try:
    from camera.gemini335 import Gemini335
    camera = Gemini335(
        color_width=settings.camera.color_width,
        color_height=settings.camera.color_height,
        color_fps=settings.camera.color_fps,
        depth_width=settings.camera.depth_width,
        depth_height=settings.camera.depth_height,
        depth_fps=settings.camera.depth_fps
    )
    print('✓ Camera initialized successfully')
except Exception as e:
    print(f'✗ Failed to initialize Camera: {e}')
    sys.exit(1)

# Test Arm Controller
try:
    from robot.arm_controller import ArmController
    arm_controller = ArmController(
        ip=settings.robot.arm_ip,
        default_vel=settings.robot.arm_default_velocity,
        default_acc=settings.robot.arm_default_acceleration,
        gripper_open_time=settings.robot.arm_gripper_open_time,
        gripper_close_time=settings.robot.arm_gripper_close_time,
        approach_offset=settings.robot.arm_approach_offset
    )
    print('✓ Arm Controller initialized successfully')
except Exception as e:
    print(f'✗ Failed to initialize Arm Controller: {e}')
    sys.exit(1)

# Test Base Controller
try:
    from robot.base_controller import BaseController
    base_controller = BaseController(
        wheel_radius=settings.robot.base_wheel_radius,
        wheel_separation=settings.robot.base_wheel_separation,
        base_speed=settings.robot.base_speed
    )
    print('✓ Base Controller initialized successfully')
except Exception as e:
    print(f'✗ Failed to initialize Base Controller: {e}')
    sys.exit(1)

# Test Model Interface
try:
    from analysis.model_interface import ModelInterface
    model_interface = ModelInterface(model_api_endpoint=settings.model.api_endpoint)
    print('✓ Model Interface initialized successfully')
except Exception as e:
    print(f'✗ Failed to initialize Model Interface: {e}')
    sys.exit(1)

print('\nAll components initialized successfully!')
print('\nTest completed.')