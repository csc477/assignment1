# CSC477 Assignment 1: Wall Following (ROS 2 Humble)

Starter code for Assignment 1 of CSC477, Introduction to Mobile Robotics. You
will write a PID controller that drives a simulated Clearpath Husky A200 along a
wall at a fixed distance, using its 2D laser scanner, in C++ or Python.

The assignment handout (PDF) on Quercus is the authoritative description of
what to hand in. This repository contains the code and the environment setup.

## Layout

| Path | What it is |
|---|---|
| `wall_following_assignment/` | The ROS 2 package you edit and submit. See its [README](wall_following_assignment/README.md) for topics, launch files and tips. |
| `docker/` | Dockerfile and `run.sh` for the recommended development environment. |
| `scripts/` | Helper scripts: clean teardown of a simulation run, a lap checker, a bag-to-CSV converter for the submission. |
| `docs/docker.md` | Setting up the Docker environment (recommended). |
| `docs/remote_lab.md` | Using the MCS lab machines remotely, if you cannot run Docker. |

## Choose your development environment

1. **Docker on your own computer (recommended).** One command builds an image
   with Ubuntu 22.04, ROS 2 Humble, Gazebo Fortress and the Clearpath simulator,
   at the same package versions as the lab machines. GUI windows appear on your
   desktop and you edit the code with your normal editor. Linux and Windows
   (WSL2) hosts. Follow [docs/docker.md](docs/docker.md).
2. **Remote lab machines (fallback).** If you cannot set up Docker (for example
   you are on a Mac, have too little disk, or the simulator is too slow on your machine), use one of
   the lab machines `mn3110pc01.utm.utoronto.ca` to `mn3110pc16.utm.utoronto.ca`
   over remote desktop and SSH. Everything is preinstalled there, and your home
   directory is the same on all of them. Follow
   [docs/remote_lab.md](docs/remote_lab.md).
3. **Native Ubuntu 22.04.** Install ROS 2 Humble and the simulator directly on
   your own Ubuntu 22.04 machine. Fastest option if you have the hardware, but
   your setup will differ from ours, so environment problems are harder for the
   course staff to help with. Follow [docs/native.md](docs/native.md).

Whichever you pick, the ROS 2 commands are the same once you have a shell with
the workspace sourced.

## Quick start

In every environment the clone lives at `~/csc477_ws/src/assignment1` and the
helper scripts at `~/csc477_ws/src/assignment1/scripts/`.

```bash
cd ~/csc477_ws
colcon build --symlink-install
source install/setup.bash

# terminal 1: simulation
ros2 launch wall_following_assignment gazebo_world.launch.py world:=walls_one_sided

# terminal 2: your controller
ros2 launch wall_following_assignment wall_follower_cpp.launch.py      # C++
ros2 launch wall_following_assignment wall_follower_python.launch.py   # Python
```

Worlds: `walls_one_sided`, `walls_two_sided`, `walls_two_sided_tight`.

## Getting help


Post on the course discussion board (Piazza). When reporting a
problem, include the exact command you ran, the full error output, and which
environment you are using (Docker, lab machine, native).
