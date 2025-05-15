class ArmController:
    def __init__(self):
        self.position = (0, 0, 0)  # Initial position of the arm

    def move_to(self, coordinates):
        # Logic to move the arm to the specified coordinates
        self.position = coordinates
        print(f"Moving arm to coordinates: {self.position}")

    def calibrate(self):
        # Logic to calibrate the arm's position
        self.position = (0, 0, 0)
        print("Arm calibrated to initial position.")