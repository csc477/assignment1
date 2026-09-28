#!/usr/bin/env bash
set -e

source /opt/ros/humble/setup.bash

# ~/clearpath/robot.yaml is seeded automatically by gazebo_world.launch.py
# from the package's config/robot.yaml on every launch; nothing to do here.

if [ -f /root/csc477_ws/install/setup.bash ]; then
  source /root/csc477_ws/install/setup.bash
fi

exec "$@"
