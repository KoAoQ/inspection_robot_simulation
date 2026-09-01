#!/usr/bin/env python3
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class CmdVelWatchdog(Node):
    def __init__(self):
        super().__init__("simulation_cmd_vel_watchdog")
        self.declare_parameter("input_topic", "/cmd_vel")
        self.declare_parameter("output_topic", "/simulation/cmd_vel")
        self.declare_parameter("timeout", 0.3)
        self.declare_parameter("publish_rate", 20.0)

        input_topic = self.get_parameter("input_topic").value
        output_topic = self.get_parameter("output_topic").value
        self.timeout = float(self.get_parameter("timeout").value)
        publish_rate = float(self.get_parameter("publish_rate").value)

        self.command = Twist()
        self.last_command_time = None
        self.publisher = self.create_publisher(Twist, output_topic, 10)
        self.subscription = self.create_subscription(
            Twist, input_topic, self.on_command, 10
        )
        self.timer = self.create_timer(1.0 / publish_rate, self.on_timer)
        self.get_logger().info(
            f"Relaying {input_topic} to {output_topic} with {self.timeout:.2f}s timeout"
        )

    def on_command(self, message):
        self.command = message
        self.last_command_time = time.monotonic()

    def on_timer(self):
        command_is_fresh = (
            self.last_command_time is not None
            and time.monotonic() - self.last_command_time <= self.timeout
        )
        self.publisher.publish(self.command if command_is_fresh else Twist())


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelWatchdog()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.publisher.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
