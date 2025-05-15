import time
from camera.gemini335 import Gemini335
from robot.arm_controller import ArmController
from robot.base_controller import BaseController
from analysis.model_interface import ModelInterface

def main():
    # Initialize camera
    camera = Gemini335()
    camera.initialize()

    # Initialize robot controllers
    arm_controller = ArmController()
    base_controller = BaseController()

    # Initialize model interface
    model_interface = ModelInterface()

    try:
        while True:
            # Capture video frame
            frame = camera.capture_frame()

            # Process frame and get movement coordinates
            movement_coordinates = model_interface.analyze_frame(frame)

            # Move the robotic arm and base vehicle
            arm_controller.move_to(movement_coordinates['arm'])
            base_controller.move_to(movement_coordinates['base'])

            # Sleep to control the loop rate
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Shutting down the robot control program.")

    finally:
        camera.release()
        base_controller.stop()

if __name__ == "__main__":
    main()