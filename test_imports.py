import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Try to import all the modules
try:
    from camera.gemini335 import Gemini335
    print('✓ Imported Gemini335')
except Exception as e:
    print(f'✗ Failed to import Gemini335: {e}')


try:
    from robot.arm_controller import ArmController
    print('✓ Imported ArmController')
except Exception as e:
    print(f'✗ Failed to import ArmController: {e}')


try:
    from robot.base_controller import BaseController
    print('✓ Imported BaseController')
except Exception as e:
    print(f'✗ Failed to import BaseController: {e}')


try:
    from analysis.model_interface import ModelInterface
    print('✓ Imported ModelInterface')
except Exception as e:
    print(f'✗ Failed to import ModelInterface: {e}')


try:
    from config.settings import Settings
    print('✓ Imported Settings')
except Exception as e:
    print(f'✗ Failed to import Settings: {e}')


print('\nAll import tests completed!')