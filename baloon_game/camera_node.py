import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from rclpy.qos import qos_profile_sensor_data

class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')

        self.declare_parameter('source', '0')
        self.declare_parameter('fps', 30.0)
        self.declare_parameter('width', 640)
        self.declare_parameter('height', 480)

        source = str(self.get_parameter('source').value)
        fps = self.get_parameter('fps').value
        self.width = self.get_parameter('width').value
        self.height = self.get_parameter('height').value

        if source.isdigit():
            self.cap = cv2.VideoCapture(int(source))
            self.is_video = False
        else:
            self.cap = cv2.VideoCapture(source)
            self.is_video = True

        if not self.cap.isOpened():
            self.get_logger().error(f'Could not open video source: {source}')
            raise RuntimeError(f'Cannot open video source: {source}')

        self.bridge = CvBridge()
        self.pub = self.create_publisher(
            Image, '/camera/image_raw', qos_profile_sensor_data)
        self.timer = self.create_timer(1.0 / fps, self.timer_callback)

    def timer_callback(self):
        ret, frame = self.cap.read()

        if not ret and self.is_video:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        if not ret:
            self.get_logger().warn(
                'Failed to read frame', throttle_duration_sec=2.0)
            return

        frame = cv2.resize(frame, (self.width, self.height))
        #flip camera bcs easier for player
        frame = cv2.resize(frame, (self.width, self.height))
        frame = cv2.flip(frame, 1) #the mirror part

        
        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera'
        self.pub.publish(msg)

    def destroy_node(self):
        self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
