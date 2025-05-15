from fairino import Robot
import time

class ArmController:
    def __init__(self, ip="192.168.58.2"):
        self.ip = ip
        self.robot = None
        self.connected = False
        self.position = None  # 机械臂当前位置

    def connect(self):
        self.robot = Robot.RPC(self.ip)
        self.connected = True
        print(f"Connected to robot at {self.ip}")

    def disconnect(self):
        if self.robot:
            self.robot.CloseRPC()
            self.connected = False
            print("Disconnected from robot.")

    def enable(self):
        if self.robot:
            ret = self.robot.RobotEnable(1)
            print(f"Robot enable: {ret}")

    def disable(self):
        if self.robot:
            ret = self.robot.RobotEnable(0)
            print(f"Robot disable: {ret}")

    def move_to(self, desc_pos, tool=0, user=0, vel=20.0):
        """
        desc_pos: 目标笛卡尔位姿 [x, y, z, rx, ry, rz] 单位mm, °
        tool: 工具号
        user: 工件号
        vel: 速度百分比
        """
        if self.robot:
            ret = self.robot.MoveL(desc_pos, tool, user, vel=vel)
            print(f"MoveL to {desc_pos}, ret={ret}")
            self.position = desc_pos

    def calibrate(self):
        """
        回零操作，假设回零点为[0,0,0,0,0,0]
        """
        if self.robot:
            zero_pos = [0, 0, 0, 0, 0, 0]
            tool = 0
            user = 0
            ret = self.robot.MoveL(zero_pos, tool, user, vel=20.0)
            print(f"Calibrate (MoveL to zero), ret={ret}")
            self.position = zero_pos

    def get_position(self):
        if self.robot:
            ret, pos = self.robot.GetActualTCPPose()
            if ret == 0:
                self.position = pos
                print(f"Current TCP position: {pos}")
                return pos
            else:
                print(f"Get position failed, ret={ret}")
                return None

    def stop(self):
        if self.robot:
            ret = self.robot.StopMotion()
            print(f"Stop motion, ret={ret}")

    def pause(self):
        if self.robot:
            ret = self.robot.PauseMotion()
            print(f"Pause motion, ret={ret}")

    def resume(self):
        if self.robot:
            ret = self.robot.ResumeMotion()
            print(f"Resume motion, ret={ret}")

    def pick(self, pick_pos, place_pos, tool=0, user=0, vel=20.0):
        """
        执行摘取操作：
        1. 移动到pick_pos
        2. 打开夹爪
        3. 下移到目标
        4. 关闭夹爪夹取
        5. 抬起
        6. 移动到place_pos
        7. 打开夹爪放下
        8. 抬起回避
        """
        if not self.robot:
            print("Robot not connected.")
            return
        # 1. 移动到pick_pos上方
        approach_offset = [0, 0, 50, 0, 0, 0]  # 上方50mm
        approach_pos = [pick_pos[i] + approach_offset[i] for i in range(6)]
        self.robot.MoveL(approach_pos, tool, user, vel=vel)
        time.sleep(0.5)
        # 2. 打开夹爪
        if hasattr(self.robot, 'ActivateGripper'):
            self.robot.ActivateGripper()
        if hasattr(self.robot, 'ControlGripper'):
            self.robot.ControlGripper(open=True)
        time.sleep(0.5)
        # 3. 下移到pick_pos
        self.robot.MoveL(pick_pos, tool, user, vel=vel)
        time.sleep(0.5)
        # 4. 关闭夹爪夹取
        if hasattr(self.robot, 'ControlGripper'):
            self.robot.ControlGripper(open=False)
        time.sleep(0.5)
        # 5. 抬起
        self.robot.MoveL(approach_pos, tool, user, vel=vel)
        time.sleep(0.5)
        # 6. 移动到place_pos上方
        place_approach_pos = [place_pos[i] + approach_offset[i] for i in range(6)]
        self.robot.MoveL(place_approach_pos, tool, user, vel=vel)
        time.sleep(0.5)
        # 7. 下移到place_pos
        self.robot.MoveL(place_pos, tool, user, vel=vel)
        time.sleep(0.5)
        # 8. 打开夹爪放下
        if hasattr(self.robot, 'ControlGripper'):
            self.robot.ControlGripper(open=True)
        time.sleep(0.5)
        # 9. 抬起回避
        self.robot.MoveL(place_approach_pos, tool, user, vel=vel)
        print("Pick and place finished.")