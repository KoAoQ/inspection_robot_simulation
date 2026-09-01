# Inspection Robot Simulation

Independent ROS 2 Humble and Gazebo Classic workspace for simulation and
algorithm validation of the WheelTec S200 inspection robot.

This repository is self-contained: simulation source, the robot model,
simulation-safe control and safety packages, localization/navigation packages,
and the locally rebuilt Smac planner are all under `src/`. It does not require
a clone or an installed overlay of the real-robot repository.

## Repository boundary

- This repository is the only destination for local simulation development.
- It never launches the real chassis serial, lidar, Astra camera, or hardware
  bringup nodes.
- Gazebo-specific collision, friction, sensor, world, and launch files live in
  `src/inspection_robot_simulation`.
- Simulation uses its own Nav2 parameters and `use_sim_time: true`.
- The real-robot repository and workspace remain separate and unchanged.

## Layout

```text
inspection_robot_simulation/
├── src/
│   ├── inspection_robot_simulation/
│   ├── inspection_robot_description/
│   ├── inspection_robot_interfaces/
│   ├── inspection_robot_core/
│   ├── inspection_robot_safety/
│   ├── inspection_robot_maps/
│   ├── inspection_robot_localization/
│   ├── inspection_robot_navigation/
│   └── third_party/nav2_smac_planner/
├── build/                         # generated, ignored
├── install/                       # generated, ignored
└── log/                           # generated, ignored
```

## Install dependencies

```bash
cd ~/inspection_robot_simulation
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
```

The host uses its own ROS Humble and OMPL installation. Do not copy `build/` or
`install/` artifacts from the ARM64 robot workspace.

## Build

```bash
cd ~/inspection_robot_simulation
source /opt/ros/humble/setup.bash
colcon build --symlink-install --allow-overriding nav2_smac_planner
source install/setup.bash
```

## Run

```bash
cd ~/inspection_robot_simulation
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=1
export GAZEBO_IP=127.0.0.1
ros2 launch inspection_robot_simulation simulation_navigation.launch.py
```

Headless validation:

```bash
ros2 launch inspection_robot_simulation \
  simulation_navigation.launch.py gui:=false rviz:=false
```

## Commit simulation changes

Run all simulation Git operations from this repository root:

```bash
cd ~/inspection_robot_simulation
git add src README.md .gitignore
git commit -m "feat: describe the simulation change"
git push origin main
```

Do not commit simulation work from `~/inspection_robot_ws_sim`; that directory
is an old integration clone of the real-robot repository and is no longer the
simulation development workspace.
