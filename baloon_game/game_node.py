import cv2
from ultralytics import YOLO

import math
import os
import random

import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Int32
from cv_bridge import CvBridge

from rclpy.qos import qos_profile_sensor_data

class Ball:
    def __init__(self, w, h, radius, speed):
        self.radius = radius
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.respawn(w, h, speed)

    def respawn(self, w, h, speed):
        self.x = random.uniform(self.radius, w - self.radius)
        self.y = random.uniform(self.radius, h - self.radius)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.hold = 0.0

    def move(self, dt, w, h):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius > w:
            self.x = w - self.radius
            self.vx = -abs(self.vx)
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius > h:
            self.y = h - self.radius
            self.vy = -abs(self.vy)


class GameNode(Node):
    def __init__(self):
        super().__init__('game_node')
        self.declare_parameter('model_path', '')
        model_path = self.get_parameter('model_path').value
        if not model_path:
            model_path = os.path.join(
                get_package_share_directory('baloon_game'), 'models', 'latest.pt')
        self.model = YOLO(model_path)
        self.bridge = CvBridge()
        self.score = 0
        #baal settings 
        self.declare_parameter('hsv_lower', [35, 100, 100])
        self.declare_parameter('hsv_upper', [85, 255, 255])
        self.declare_parameter('num_balls', 3)
        self.declare_parameter('hold_duration', 2.0)
        self.declare_parameter('ball_radius', 40)
        self.declare_parameter('ball_speed', 150.0)
        self.declare_parameter('min_area', 300)

        self.balls = []
        self.last_time = None

        # Subscribers and Publishers from the table
        self.sub_cam = self.create_subscription(Image, '/camera/image_raw', self.image_callback, qos_profile_sensor_data)
        self.pub_score = self.create_publisher(Int32, '/game/score', 10)
        self.pub_debug = self.create_publisher(Image, '/game/debug_image', 10)

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        num_balls = self.get_parameter('num_balls').value
        hold_duration = self.get_parameter('hold_duration').value
        ball_radius = self.get_parameter('ball_radius').value
        ball_speed = self.get_parameter('ball_speed').value
        min_area = self.get_parameter('min_area').value

        h, w = frame.shape[:2]

        now = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        dt = 0.0 if self.last_time is None else now - self.last_time
        dt = max(0.0, min(dt, 0.5))
        self.last_time = now

        if len(self.balls) != num_balls:
            self.balls = [Ball(w, h, ball_radius, ball_speed) for _ in range(num_balls)]

        # Run YOLO
        results = self.model.predict(frame, conf=0.5, verbose=False)
        frame = results[0].plot()

        # Every detection can touch balls, not just the biggest one
        centroid = None
        best_area = 0
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            area = (x2 - x1) * (y2 - y1)
            if area >= min_area and area > best_area:
                best_area = area
                centroid = ((x1 + x2) // 2, (y1 + y2) // 2)

        if centroid is not None:
            cv2.circle(frame, centroid, 6, (0, 255, 0), -1)

        touched = None
        nearest = None
        if centroid is not None:
            for b in self.balls:
                d = math.hypot(centroid[0] - b.x, centroid[1] - b.y)
                if d <= b.radius and (nearest is None or d < nearest):
                    nearest = d
                    touched = b

        score_changed = False
        remaining = None
        for b in self.balls:
            b.move(dt, w, h)
            if b is touched:
                b.hold += dt
                if b.hold >= hold_duration:
                    self.score += 1
                    score_changed = True
                    b.respawn(w, h, ball_speed)
                else:
                    remaining = hold_duration - b.hold
            else:
                b.hold = 0.0
            cv2.circle(frame, (int(b.x), int(b.y)), b.radius, b.color, -1)

        if remaining is not None:
            cv2.putText(frame, f"Pops in: {remaining:.1f}s", (w - 280, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

        if score_changed:
            score_msg = Int32()
            score_msg.data = self.score
            self.pub_score.publish(score_msg)

        cv2.putText(frame, f"Score: {self.score}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        debug_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        debug_msg.header = msg.header
        self.pub_debug.publish(debug_msg)

        cv2.imshow("Pop ze ball", frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = GameNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
