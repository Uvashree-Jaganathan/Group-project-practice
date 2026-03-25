import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math


class TurtleNavigator(Node):
    def __init__(self):
        super().__init__('turtle_navigator')

        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)

        self.pose = None

        # Define checkpoints
        self.checkpoints = [
            {"name": "School", "coords": (8.0, 8.0)},
            {"name": "Park", "coords": (2.0, 8.0)},
            {"name": "Ground", "coords": (9.0, 3.0)},
            {"name": "Playground", "coords": (3.0, 3.0)}
        ]

        # Home position
        self.start = {"name": "Home", "coords": (5.5, 5.5)}

        # 🔥 Sort checkpoints circularly around Home
        home_x, home_y = self.start["coords"]

        def angle_from_home(point):
            px, py = point["coords"]
            return math.atan2(py - home_y, px - home_x)

        self.checkpoints.sort(key=angle_from_home)

        # Add home at end
        self.checkpoints.append(self.start)

        self.current_index = 0

        self.timer = self.create_timer(0.05, self.navigate)

    def pose_callback(self, msg):
        self.pose = msg

    def navigate(self):
        if self.pose is None:
            return

        if self.current_index >= len(self.checkpoints):
            return

        target = self.checkpoints[self.current_index]
        tx, ty = target["coords"]

        dx = tx - self.pose.x
        dy = ty - self.pose.y
        distance = math.sqrt(dx**2 + dy**2)

        angle_to_target = math.atan2(dy, dx)
        angle_diff = angle_to_target - self.pose.theta
        angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

        msg = Twist()

        # Rotate first smoothly
        if abs(angle_diff) > 0.05:
            msg.angular.z = 2.0 * angle_diff
            msg.linear.x = 0.0
        elif distance > 0.15:
            msg.linear.x = min(1.5, distance)
            msg.angular.z = 1.5 * angle_diff
        else:
            # Reached checkpoint
            self.get_logger().info(
                f"Reached {target['name']} at coordinates {target['coords']}")
            self.current_index += 1

            # If Home reached → stop completely
            if target["name"] == "Home":
                self.get_logger().info("Returned Home. Stopping completely.")
                self.stop()
                self.timer.cancel()
                return

        self.pub.publish(msg)

    def stop(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    navigator = TurtleNavigator()

    try:
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        pass
    finally:
        navigator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()