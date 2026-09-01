# Inspection Robot Simulation

Gazebo Classic simulation for the WheelTec S200 inspection robot on ROS 2
Humble. This repository contains simulation-only launch files, Gazebo plugins,
virtual sensors, worlds, maps, and Nav2 parameter overrides.

The real-robot repository remains the source of shared interfaces, meshes,
localization, navigation, safety, and velocity-management packages:

```text
git@github.com:KoAoQ/inspection_robot_ws.git
```

## Isolation boundary

- No real serial, lidar, camera, or device nodes are launched.
- Gazebo-specific collision, friction, and sensor plugins live here.
- Simulation uses `use_sim_time: true`.
- Simulation Nav2 uses its own `config/nav2_sim.yaml`.
- Real-robot launch files and parameters are not modified by this repository.

## Use in a local simulation-validation clone

The real-robot repository may be cloned locally as a simulation-validation
workspace while both Git histories remain independent:

```bash
git clone git@github.com:KoAoQ/inspection_robot_ws.git \
  ~/inspection_robot_ws_sim
git clone <simulation-repository-url> ~/inspection_robot_simulation

ln -s ~/inspection_robot_simulation \
  ~/inspection_robot_ws_sim/src/inspection_robot_simulation

cd ~/inspection_robot_ws_sim
source /opt/ros/humble/setup.bash
colcon build --symlink-install --allow-overriding nav2_smac_planner
source install/setup.bash
```

Add `/src/inspection_robot_simulation` to the base clone's local
`.git/info/exclude` so the link cannot be accidentally committed there.

## Build as a separate overlay

Build and source the real-robot workspace first, then build this repository in
a separate overlay workspace:

```bash
source /opt/ros/humble/setup.bash
source /path/to/inspection_robot_ws/install/setup.bash

mkdir -p ~/inspection_robot_sim_ws/src
git clone <simulation-repository-url> \
  ~/inspection_robot_sim_ws/src/inspection_robot_simulation
cd ~/inspection_robot_sim_ws

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

The pinned real-robot source revision is recorded in
`inspection_robot_simulation.repos`.

## Run

```bash
export ROS_LOCALHOST_ONLY=1
export GAZEBO_IP=127.0.0.1
ros2 launch inspection_robot_simulation simulation_navigation.launch.py
```

For headless validation:

```bash
ros2 launch inspection_robot_simulation \
  simulation_navigation.launch.py gui:=false rviz:=false
```
