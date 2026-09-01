import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


NAVIGATION_NODES = [
    "controller_server",
    "smoother_server",
    "planner_server",
    "behavior_server",
    "bt_navigator",
    "waypoint_follower",
    "velocity_smoother",
]


def nav2_node(package, executable, params, log_level, use_respawn, remappings):
    return Node(
        package=package,
        executable=executable,
        name=executable,
        output="screen",
        respawn=use_respawn,
        respawn_delay=2.0,
        parameters=params,
        arguments=["--ros-args", "--log-level", log_level],
        remappings=remappings,
    )


def generate_launch_description():
    navigation_share = get_package_share_directory("inspection_robot_navigation")
    default_params_file = os.path.join(
        navigation_share,
        "config",
        "nav2.yaml",
    )
    behavior_tree_dir = os.path.join(navigation_share, "behavior_trees")
    bt_parameters = {
        "default_nav_to_pose_bt_xml": os.path.join(
            behavior_tree_dir, "navigate_to_pose_forward_only.xml"
        ),
        "default_nav_through_poses_bt_xml": os.path.join(
            behavior_tree_dir, "navigate_through_poses_forward_only.xml"
        ),
    }

    params_file = LaunchConfiguration("params_file")
    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart = LaunchConfiguration("autostart")
    use_respawn = LaunchConfiguration("use_respawn")
    log_level = LaunchConfiguration("log_level")

    parameters = [
        params_file,
        {"use_sim_time": use_sim_time},
    ]

    common_remappings = [
        ("/tf", "tf"),
        ("/tf_static", "tf_static"),
    ]

    # Both normal path following and recovery behaviors feed the smoother.
    raw_cmd_remappings = common_remappings + [
        ("cmd_vel", "/cmd_vel/nav_raw"),
    ]

    # Only the smoothed command is exposed to inspection_robot_velocity_manager.
    velocity_smoother_remappings = common_remappings + [
        ("cmd_vel", "/cmd_vel/nav_raw"),
        ("cmd_vel_smoothed", "/cmd_vel/nav"),
    ]

    return LaunchDescription(
        [
            SetEnvironmentVariable("RCUTILS_LOGGING_BUFFERED_STREAM", "1"),
            DeclareLaunchArgument(
                "params_file",
                default_value=default_params_file,
                description="Full path to the Nav2 parameter file",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Use simulation clock",
            ),
            DeclareLaunchArgument(
                "autostart",
                default_value="true",
                description="Automatically configure and activate Nav2 nodes",
            ),
            DeclareLaunchArgument(
                "use_respawn",
                default_value="false",
                description="Respawn a Nav2 process if it exits unexpectedly",
            ),
            DeclareLaunchArgument(
                "log_level",
                default_value="info",
                description="Nav2 logging level",
            ),
            nav2_node(
                "nav2_controller",
                "controller_server",
                parameters,
                log_level,
                use_respawn,
                raw_cmd_remappings,
            ),
            nav2_node(
                "nav2_smoother",
                "smoother_server",
                parameters,
                log_level,
                use_respawn,
                common_remappings,
            ),
            nav2_node(
                "nav2_planner",
                "planner_server",
                parameters,
                log_level,
                use_respawn,
                common_remappings,
            ),
            nav2_node(
                "nav2_behaviors",
                "behavior_server",
                parameters,
                log_level,
                use_respawn,
                raw_cmd_remappings,
            ),
            nav2_node(
                "nav2_bt_navigator",
                "bt_navigator",
                parameters + [bt_parameters],
                log_level,
                use_respawn,
                common_remappings,
            ),
            nav2_node(
                "nav2_waypoint_follower",
                "waypoint_follower",
                parameters,
                log_level,
                use_respawn,
                common_remappings,
            ),
            nav2_node(
                "nav2_velocity_smoother",
                "velocity_smoother",
                parameters,
                log_level,
                use_respawn,
                velocity_smoother_remappings,
            ),
            Node(
                package="nav2_lifecycle_manager",
                executable="lifecycle_manager",
                name="lifecycle_manager_navigation",
                output="screen",
                parameters=[
                    {
                        "use_sim_time": use_sim_time,
                        "autostart": autostart,
                        "node_names": NAVIGATION_NODES,
                    }
                ],
                arguments=["--ros-args", "--log-level", log_level],
            ),
        ]
    )
