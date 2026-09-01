#!/usr/bin/env python3
"""Republish single-ray ultrasonic LaserScan as sensor_msgs/Range.

gazebo_ros (Humble) does not provide a Range sensor plugin, so the sim URDF
models each ultrasonic as a one-sample LaserScan on /ultrasonic/scan/<key>.
This node converts those scans back to sensor_msgs/Range on /ultrasonic/<key>,
the topics inspection_robot_safety already subscribes to, mirroring the output
of the real inspection_robot_base driver.
"""
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan, Range


class UltrasonicRangeBridge(Node):
    KEYS = "abcdef"

    def __init__(self):
        super().__init__("simulation_ultrasonic_bridge")
        self.declare_parameter("keys", list(self.KEYS))
        self.declare_parameter("field_of_view", 0.52)
        keys = self.get_parameter("keys").value
        self.fov = float(self.get_parameter("field_of_view").value)

        qos = qos_profile_sensor_data
        self.pubs = {}
        for key in keys:
            self.create_subscription(
                LaserScan,
                f"/ultrasonic/scan/{key}",
                lambda msg, k=key: self.on_scan(k, msg),
                qos,
            )
            self.pubs[key] = self.create_publisher(
                Range, f"/ultrasonic/{key}", qos
            )
        self.get_logger().info(
            f"Bridging {len(keys)} ultrasonic scans to /ultrasonic/<key> Range"
        )

    def on_scan(self, key, scan):
        best = float("inf")
        for value in scan.ranges:
            if math.isfinite(value) and scan.range_min <= value <= scan.range_max:
                best = min(best, value)

        r = Range()
        r.header = scan.header
        r.radiation_type = Range.ULTRASOUND
        r.field_of_view = self.fov
        r.min_range = scan.range_min
        r.max_range = scan.range_max
        # No return within range is reported as +inf, matching the real base
        # driver's "no obstacle" convention the safety node expects.
        r.range = best if math.isfinite(best) else float("inf")
        self.pubs[key].publish(r)


def main(args=None):
    rclpy.init(args=args)
    node = UltrasonicRangeBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
