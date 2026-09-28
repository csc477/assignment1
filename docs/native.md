# Development environment: native Ubuntu 22.04

You can install the same software the Docker image and the lab machines use
directly on an Ubuntu 22.04 (Jammy) machine. This gives you the best
performance, especially with a GPU. The trade-off is that your installation is
not identical to ours, so the course staff may have a harder time helping you
with environment problems. If you get stuck, switching to Docker or the lab
machines is always possible; the workspace layout is the same.

ROS 2 Humble only exists for Ubuntu 22.04. On 24.04 or later, use Docker.

## Install

```bash
sudo apt update
sudo apt install -y software-properties-common curl gnupg lsb-release
sudo add-apt-repository -y universe

# ROS 2 apt source
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Clearpath apt source (Husky simulator)
curl -sSL https://packages.clearpathrobotics.com/public.key \
  | sudo gpg --dearmor --yes -o /usr/share/keyrings/clearpath-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/clearpath-archive-keyring.gpg] https://packages.clearpathrobotics.com/stable/ubuntu jammy main" \
  | sudo tee /etc/apt/sources.list.d/clearpath-latest.list > /dev/null

sudo apt update
sudo apt install -y ros-humble-desktop ros-dev-tools \
  ros-humble-clearpath-simulator ros-humble-clearpath-desktop \
  ros-humble-rqt-reconfigure ros-humble-teleop-twist-keyboard \
  ignition-fortress python3-pytest

sudo rosdep init || true      # already done on some machines; harmless
rosdep update

echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
echo '[ -f ~/csc477_ws/install/setup.bash ] && source ~/csc477_ws/install/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

This is the same package list as `docker/Dockerfile`. The image pins the
Clearpath packages to versions 1.3.3 (simulator) and 1.2.1 (desktop); a newer
release on your machine should still work, but if the simulation behaves
differently from the handout, compare with `apt-cache policy
ros-humble-clearpath-simulator`.

## Workspace

Same as on the lab machines:

```bash
mkdir -p ~/csc477_ws/src && cd ~/csc477_ws/src
git clone https://github.com/csc477/assignment1.git
cd ~/csc477_ws && colcon build --symlink-install && source install/setup.bash
```

From here on everything in the package [README](../wall_following_assignment/README.md)
applies unchanged. Helper scripts are in `~/csc477_ws/src/assignment1/scripts/`.

## Notes

- **NVIDIA GPU**: install the driver Ubuntu recommends (`ubuntu-drivers
  install`) and reboot; Gazebo then renders on the GPU. Without a GPU, or with
  a driver problem, Gazebo falls back to software rendering, which is slower
  but fine for this assignment.
- **Wayland desktops** work; Gazebo and rviz2 run through XWayland.
- **Several ROS 2 machines on one network** (a lab, a shared flat) see each
  other's topics by default. Put `export ROS_LOCALHOST_ONLY=1` in your
  `~/.bashrc` to keep your simulation to yourself.
