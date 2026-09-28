# wall_following_assignment (ROS 2 Humble)

The package you edit and submit. Implement a PID controller that drives the
simulated Clearpath Husky A200 parallel to a wall at a desired distance, in
C++ or Python.

## Build

```bash
cd ~/csc477_ws
colcon build --symlink-install
source install/setup.bash
```

After editing C++ files, run `colcon build` again and re-source
`install/setup.bash` in any terminal that was open before the build.
`--symlink-install` makes Python edits live immediately, but C++ changes still
need a rebuild.

## Run the simulation

```bash
ros2 launch wall_following_assignment gazebo_world.launch.py world:=walls_one_sided
```

Worlds: `walls_one_sided`, `walls_two_sided`, `walls_two_sided_tight`. The
robot spawns at x = -3, y = 2 facing +x, with the first wall on its left.

To see the laser scan and the TF tree, run rviz2 with the course config in a
second terminal:

```bash
rviz2 -d $(ros2 pkg prefix wall_following_assignment)/share/wall_following_assignment/config/csc477.rviz \
  --ros-args -p use_sim_time:=true -r /tf:=/a200_0000/tf -r /tf_static:=/a200_0000/tf_static
```

The remappings and `use_sim_time` are required. The Clearpath stack publishes
the robot's transforms inside the robot namespace (`/a200_0000/tf`), and rviz2
listens on the global `/tf`; without the remap it cannot place the scan in the
`odom` frame and logs a stream of `Message Filter dropping message` warnings
while the LaserScan display stays empty. A few dropped messages right after
startup are normal.

## Drive manually (sanity check)

Either use the Teleop panel in the Gazebo window (it is already set to
`/a200_0000/cmd_vel`), or in a terminal:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/a200_0000/cmd_vel
```

## Put the robot back at the start

The Gazebo window has a **Reset pose to start** button directly below the
Teleop panel. It teleports the robot back to its spawn pose without restarting
the simulation. Two things it does not do: it does not stop a controller that
is still publishing on `cmd_vel` (the robot drives off again immediately), and
it does not reset wheel odometry, so the `odom` frame in rviz2 keeps counting
from where the robot was. The laser scan and Gazebo's own pose are correct
straight away.

## Implement your controller

Pick one language.

- **C++**: fill in the TODOs in `src/wall_follower_node.cpp` and
  `include/wall_following_assignment/pid.h`.
- **Python**: `scripts/wall_follower.py` already contains a minimal working
  controller of the simplest kind (method (1) below). Start from it and
  improve it.

Topics your node uses (all under the robot namespace `a200_0000`):

| Topic | Type | Direction |
|---|---|---|
| `/a200_0000/sensors/lidar2d_0/scan` | `sensor_msgs/msg/LaserScan` | subscribe |
| `/a200_0000/cmd_vel` | `geometry_msgs/msg/Twist` | publish |
| `/a200_0000/cte` | `std_msgs/msg/Float32` | publish (cross-track error) |

The skeleton's comment offers two ways to compute the steering command:

1. from the distance to the closest wall only;
2. from that distance and the orientation of the wall relative to the robot.

They are not equally good. The distance to the closest point of a 360 degree
scan carries no direction, so think about what such a controller does when the
wall ahead gets closer than the wall beside the robot, for instance at the
corners of the course. Gain tuning does not change what information the error
signal contains.

Then, with the simulation running, in a second terminal:

```bash
ros2 launch wall_following_assignment wall_follower_cpp.launch.py
# or
ros2 launch wall_following_assignment wall_follower_python.launch.py
```

The launch files set `forward_speed` (1.0 m/s) and `desired_distance_from_wall`
(1.0 m). We will test your controller with other values in that neighbourhood,
so do not hard-code them.

## Tune PID gains live

`Kp`, `Td` and `Ti` are ROS 2 parameters of the `/wall_follower` node and can
be changed while it runs:

```bash
ros2 run rqt_reconfigure rqt_reconfigure
# or
ros2 param set /wall_follower Kp 0.3
```

Once you are happy with a set of gains, make them the defaults in your code.

## Record the cross-track error

```bash
ros2 bag record -o my_cte /a200_0000/cte
```

Convert the bag to a CSV file for submission with the script in the
repository's `scripts/` directory:

```bash
python3 ~/csc477_ws/src/assignment1/scripts/bag_to_csv.py my_cte my_cte.csv
```

To plot it, `ros2 bag play my_cte` in one terminal and
`ros2 run rqt_plot rqt_plot /a200_0000/cte/data` in another, or read the CSV
with your favourite plotting tool.

## Reset between runs

A robot wedged against a wall reads a constant short range off the wall at a
constant bearing and will happily track that as a "wall" forever. Click "Reset
pose to start" or relaunch the simulation between runs. To check whether a run
went all the way around the course,
`~/csc477_ws/src/assignment1/scripts/trace_ground_truth.py` reads the robot's
pose from Gazebo and reports which sides of the course were reached.

## Clean teardown

Gazebo's bridge processes do not always die with `ros2 launch`. An orphaned
bridge re-attaches to the next simulation you start and delivers every scan
twice, which halves your derivative term and makes a good controller
oversteer. Symptom: `ros2 topic info /a200_0000/sensors/lidar2d_0/scan` reports
`Publisher count: 2`. Fix:

```bash
bash ~/csc477_ws/src/assignment1/scripts/teardown.sh     # repeat until "no survivors"
```

## Unit tests

```bash
cd ~/csc477_ws && colcon test --packages-select wall_following_assignment && colcon test-result --verbose
```

`test/test_pid.py` checks the Python PID class; `test/test_gui_config.py`
checks the generated Gazebo GUI config. The C++ PID is not covered; test it in
simulation.
