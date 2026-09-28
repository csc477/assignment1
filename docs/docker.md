# Development environment: Docker (recommended)

The Docker image reproduces the lab machines' software stack: Ubuntu 22.04,
ROS 2 Humble, Gazebo Fortress and the Clearpath Husky simulator, pinned to the
same package versions. The container shows its windows (Gazebo, rviz2,
rqt_reconfigure) on your own desktop, and the assignment package is
bind-mounted from your clone, so you edit with whatever editor you like on the
host and the container sees the changes immediately.

## Requirements

- **Linux**: an X11 or Wayland desktop (XWayland is fine), Docker Engine from
  <https://docs.docker.com/engine/install/> working from your normal user
  account (`docker run hello-world` succeeds without `sudo`: add yourself to
  the `docker` group, or use rootless Docker), and `xauth` (usually present).
  Use `run.sh`.
- **Windows 11**: WSL2 with Ubuntu, Docker Desktop with the WSL2 backend (or
  Docker Engine inside the WSL distribution). WSLg provides the display. Run
  `run.sh` from the WSL shell.
- **macOS is not supported.** Gazebo's 3D view needs OpenGL 3.3, which
  XQuartz cannot provide to a container, so the Gazebo window fails to start
  (`Failed to create OpenGL context`). Mac users should use the
  [lab machines](remote_lab.md) instead.
- About 8 GB of free disk for the image plus the build directory.
- A GPU is not required. Without hardware acceleration the container falls back
  to software rendering, which is fast enough for this assignment.

## Build the image (once)

```bash
git clone https://github.com/csc477/assignment1.git
cd assignment1/docker
./run.sh build        # downloads about 5 GB; takes a while
```

## Daily use

```bash
cd assignment1/docker
./run.sh shell        # starts the container if needed and opens a shell in it
```

Run `./run.sh shell` again in another terminal for a second shell in the same
container (you will need at least two: one for the simulator, one for your
controller). `./run.sh down` stops and removes the container; your files and
build output survive because they live on the host.

Inside the container:

```bash
cd ~/csc477_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch wall_following_assignment gazebo_world.launch.py world:=walls_one_sided
```

The Gazebo window should appear on your desktop within a minute or so on the
first launch.

## What is mounted where

| Host | Container |
|---|---|
| `assignment1` (your clone) | `~/csc477_ws/src/assignment1` |
| `assignment1/docker/ws` | `~/csc477_ws` (colcon's `build/`, `install/`, `log/`) |

This is the same layout as on the lab machines, so every command in the
handout works unchanged in both environments.

Edit the package on the host. Build inside the container. After editing C++
files you must re-run `colcon build` (and `source install/setup.bash` in any
terminal opened before the build). Python edits are live immediately thanks to
`--symlink-install`.

If you run rootful Docker (the default `apt` installation), files the container
writes into `docker/ws` are owned by root on the host. That is harmless, but you
will need `sudo rm -rf docker/ws` if you ever want to delete the build output.
Under rootless Docker they are owned by you.

If you use Docker Desktop (Windows), give it enough resources under
*Settings, Resources*: at least 6 GB of memory and 4 CPUs.

## Troubleshooting

- **No window appears / `could not connect to display`.** Make sure `DISPLAY`
  is set in the shell you ran `./run.sh` from and that `xauth list` prints at
  least one entry. On Wayland desktops the container talks to XWayland, which
  works as long as `DISPLAY` is set. Run `./run.sh down` and then
  `./run.sh shell` again after fixing the host environment; the X cookie is
  copied when the container is created.
- **`libGL error: MESA-LOADER: failed to open ...`** in the Gazebo output is
  expected on some GPUs. Gazebo then renders with the CPU (`llvmpipe`) and
  everything still works.
- **Two publishers on the scan topic, or the scan rate is double what it should
  be.** A bridge process from a previous run survived. Run
  `bash ~/csc477_ws/src/assignment1/scripts/teardown.sh` (inside the container)
  until it reports no survivors, then relaunch.
- **The robot behaves strangely after a crash into a wall.** Click "Reset pose
  to start" in the Gazebo window, or tear down and relaunch. See the package
  README.
