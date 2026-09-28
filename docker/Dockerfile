# CSC477 Assignment 1 development environment: Ubuntu 22.04 (jammy), ROS 2
# Humble, Gazebo Fortress and the Clearpath simulator, at the same pinned
# package versions as the MCS lab machines. See docs/docker.md.
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
      software-properties-common curl gnupg lsb-release xvfb ca-certificates \
      locales sudo \
    && locale-gen en_US.UTF-8 \
    && add-apt-repository -y universe \
    && rm -rf /var/lib/apt/lists/*

# ROS 2 apt source
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
      -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" \
      > /etc/apt/sources.list.d/ros2.list

# Clearpath apt source
RUN curl -sSL https://packages.clearpathrobotics.com/public.key \
      | gpg --dearmor --yes -o /usr/share/keyrings/clearpath-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/clearpath-archive-keyring.gpg] https://packages.clearpathrobotics.com/stable/ubuntu jammy main" \
      > /etc/apt/sources.list.d/clearpath-latest.list

# Pin the Clearpath upstream versions (the lab machines run 1.3.3 / 1.2.1).
# The Debian revision after the '*' carries a per-architecture build stamp
# that differs between amd64 and arm64, so it is globbed.
ARG CLEARPATH_SIM_VERSION='1.3.3-*'
ARG CLEARPATH_DESKTOP_VERSION='1.2.1-*'

RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-humble-desktop \
      ros-dev-tools \
      "ros-humble-clearpath-simulator=${CLEARPATH_SIM_VERSION}" \
      "ros-humble-clearpath-desktop=${CLEARPATH_DESKTOP_VERSION}" \
      ros-humble-rqt-reconfigure \
      ros-humble-teleop-twist-keyboard \
      ignition-fortress \
      python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Mesa userspace for the host's AMD/Intel GPU via /dev/dri, plus the X client
# libs Gazebo's and rviz2's Qt GUIs need.
RUN apt-get update && apt-get install -y --no-install-recommends \
      libgl1-mesa-dri libgl1-mesa-glx libglu1-mesa mesa-utils \
      libxkbcommon-x11-0 libxcb-xinerama0 libxcb-cursor0 x11-utils x11-xserver-utils \
    && rm -rf /var/lib/apt/lists/*

RUN rosdep init || true
RUN rosdep update --rosdistro humble

# Container root maps to the invoking host user under rootless Docker, so bind
# mounts stay writable without a uid-matched account.
RUN echo 'source /opt/ros/humble/setup.bash' >> /root/.bashrc \
    && echo '[ -f ~/csc477_ws/install/setup.bash ] && source ~/csc477_ws/install/setup.bash' >> /root/.bashrc

RUN mkdir -p /root/clearpath /root/csc477_ws/src

WORKDIR /root/csc477_ws
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]
