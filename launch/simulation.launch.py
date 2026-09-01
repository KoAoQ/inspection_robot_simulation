import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    simulation_share = get_package_share_directory("inspection_robot_simulation")
    core_share = get_package_share_directory("inspection_robot_core")
    safety_share = get_package_share_directory("inspection_robot_safety")
    gazebo_share = get_package_share_directory("gazebo_ros")

    world = LaunchConfiguration("world")
    gui = LaunchConfiguration("gui")
    paused = LaunchConfiguration("paused")
    initial_mode = LaunchConfiguration("initial_mode")
    x = LaunchConfiguration("x")
    y = LaunchConfiguration("y")
    yaw = LaunchConfiguration("yaw")

    xacro_file = os.path.join(
        simulation_share, "urdf", "inspection_robot_s200_sim.urdf.xacro"
    )
    robot_description = {
        "robot_description": Command(["xacro ", xacro_file]),
        "use_sim_time": True,
    }

    core_params = os.path.join(core_share, "config", "core.yaml")
    safety_params = os.path.join(safety_share, "config", "safety.yaml")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "world",
                default_value=os.path.join(simulation_share, "worlds", "empty_room.world"),
            ),
            DeclareLaunchArgument("gui", default_value="true"),
            DeclareLaunchArgument("paused", default_value="false"),
            DeclareLaunchArgument(
                "initial_mode",
                default_value="NAVIGATION",
                description="Velocity manager mode (STOP MANUAL NAVIGATION FOLLOW)",
            ),
            DeclareLaunchArgument("x", default_value="0.0"),
            DeclareLaunchArgument("y", default_value="0.0"),
            DeclareLaunchArgument("yaw", default_value="0.0"),
            # The simulation uses only local resources. Disabling the online
            # model database prevents gzclient from waiting when offline.
            SetEnvironmentVariable("GAZEBO_MODEL_DATABASE_URI", ""),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(gazebo_share, "launch", "gazebo.launch.py")
                ),
                launch_arguments={
                    "world": world,
                    "gui": gui,
                    "pause": paused,
                    "verbose": "false",
                }.items(),
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[robot_description],
                output="screen",
            ),
            # The simulated chassis replaces the real base driver, so it reuses
            # the same safety chain: nav -> core -> /control/cmd_vel -> safety
            # -> /base/safe_cmd_vel. The watchdog emulates the base layer's
            # command-timeout fail-safe (zero on stale command).
            Node(
                package="inspection_robot_core",
                executable="velocity_manager_node",
                name="inspection_robot_velocity_manager",
                parameters=[core_params, {"initial_mode": initial_mode}],
                output="screen",
            ),
            Node(
                package="inspection_robot_safety",
                executable="safety_node",
                name="inspection_robot_safety",
                parameters=[safety_params],
                output="screen",
            ),
            Node(
                package="inspection_robot_simulation",
                executable="ultrasonic_range_bridge.py",
                output="screen",
            ),
            Node(
                package="inspection_robot_simulation",
                executable="cmd_vel_watchdog.py",
                parameters=[
                    {
                        "input_topic": "/base/safe_cmd_vel",
                        "output_topic": "/simulation/cmd_vel",
                        "timeout": 0.3,
                        "use_sim_time": True,
                    }
                ],
                output="screen",
            ),
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=[
                    "-entity", "inspection_robot_s200", "-topic", "robot_description",
                    "-x", x, "-y", y, "-z", "0.01", "-Y", yaw,
                ],
                output="screen",
            ),
        ]
    )
