import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def include(package, filename, arguments, condition=None):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory(package), "launch", filename)
        ),
        launch_arguments=arguments.items(),
        condition=condition,
    )


def generate_launch_description():
    simulation_share = get_package_share_directory("inspection_robot_simulation")
    map_file = LaunchConfiguration("map")
    gui = LaunchConfiguration("gui")
    rviz = LaunchConfiguration("rviz")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "map",
                default_value=os.path.join(simulation_share, "maps", "empty_room.yaml"),
            ),
            DeclareLaunchArgument("gui", default_value="true"),
            DeclareLaunchArgument("rviz", default_value="true"),
            include(
                "inspection_robot_simulation",
                "simulation.launch.py",
                {"gui": gui},
            ),
            include(
                "inspection_robot_localization",
                "amcl.launch.py",
                {
                    "map": map_file,
                    "params_file": os.path.join(
                        simulation_share, "config", "amcl_sim.yaml"
                    ),
                    "use_sim_time": "true",
                },
            ),
            include(
                "inspection_robot_simulation",
                "navigation_sim.launch.py",
                {
                    "params_file": os.path.join(
                        simulation_share, "config", "nav2_sim.yaml"
                    ),
                    "use_sim_time": "true",
                },
            ),
            include(
                "inspection_robot_navigation",
                "rviz.launch.py",
                {"use_sim_time": "true"},
                condition=IfCondition(rviz),
            ),
        ]
    )
