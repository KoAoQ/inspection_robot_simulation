cmake_minimum_required(VERSION 3.8)
project(inspection_robot_simulation)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY config launch maps urdf worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/cmd_vel_watchdog.py
    scripts/ultrasonic_range_bridge.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
