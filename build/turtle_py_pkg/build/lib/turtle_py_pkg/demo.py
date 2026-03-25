import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn
import math


class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')

        # Publisher and subscriber
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )

        # Waypoints (square path)
        self.waypoints = [(2, 2), (8, 2), (8, 8), (2, 8)]
        self.index = 0
        self.pose = None
        self.obstacle_pose = None
        self.finished = False   # 🔑 NEW FLAG

        # Parameters
        self.goal_tolerance = 0.1
        self.safe_distance = 1.5
        self.linear_speed = 2.0
        self.angular_gain = 4.0

        # Timer
        self.timer = self.create_timer(0.1, self.control_loop)

        # Spawn obstacle
        self.spawn_obstacle()

    def pose_callback(self, msg):
        self.pose = msg

    def obstacle_callback(self, msg):
        self.obstacle_pose = msg

    def normalize_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def spawn_obstacle(self):
        client = self.create_client(Spawn, '/spawn')
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for /spawn service...")

        request = Spawn.Request()
        request.x = 7.0
        request.y = 2.5
        request.theta = 0.0
        request.name = 'turtle2'

        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info("Obstacle turtle2 spawned!")

        self.create_subscription(
            Pose, '/turtle2/pose', self.obstacle_callback, 10
        )

    def control_loop(self):
        if self.pose is None or self.finished:
            return

        # 🛑 Stop permanently after last waypoint
        if self.index >= len(self.waypoints):
            self.get_logger().info("✅ Final waypoint reached. Stopping.")
            self.stop_robot()
            self.finished = True
            return

        # Current waypoint
        goal_x, goal_y = self.waypoints[self.index]

        dx_goal = goal_x - self.pose.x
        dy_goal = goal_y - self.pose.y
        distance_to_goal = math.sqrt(dx_goal ** 2 + dy_goal ** 2)
        angle_to_goal = math.atan2(dy_goal, dx_goal)

        # Smooth motion
        linear = min(self.linear_speed, distance_to_goal)
        angular = self.angular_gain * self.normalize_angle(
            angle_to_goal - self.pose.theta
        )

        # 🚧 Obstacle avoidance
        if self.obstacle_pose is not None:
            dist_obs = self.distance(
                self.pose.x,
                self.pose.y,
                self.obstacle_pose.x,
                self.obstacle_pose.y,
            )

            if dist_obs < self.safe_distance:
                dx_obs = self.pose.x - self.obstacle_pose.x
                dy_obs = self.pose.y - self.obstacle_pose.y
                angle_away = math.atan2(dy_obs, dx_obs)
                avoid_angle = self.normalize_angle(
                    angle_away - self.pose.theta
                )

                angular += 2.0 * avoid_angle
                linear *= 0.7

        # ✅ Waypoint reached
        if distance_to_goal < self.goal_tolerance:
            self.get_logger().info(
                f"Reached waypoint {self.index + 1}"
            )
            self.stop_robot()
            self.index += 1
            return

        # Publish command
        cmd = Twist()
        cmd.linear.x = linear
        cmd.angular.z = angular
        self.cmd_pub.publish(cmd)

    def stop_robot(self):
        self.cmd_pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = WaypointNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()