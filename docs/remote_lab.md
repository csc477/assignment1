# Development environment: MCS lab machines (fallback)

Use this if you cannot set up the Docker environment on your own computer,
including if you use a Mac (the Docker environment does not support macOS). The
lab machines have ROS 2 Humble, Gazebo Fortress and the Clearpath simulator
installed, an NVIDIA GPU for rendering, and a remote desktop server, so you can
work from anywhere with a network connection.

The machines are

```
mn3110pc01.utm.utoronto.ca
mn3110pc02.utm.utoronto.ca
...
mn3110pc16.utm.utoronto.ca
```

Your home directory is network-mounted and identical on all of them, so it
does not matter which one you use, and you can switch machines at any time
(for example when the one you are on is busy). Only running programs and
remote desktop sessions are tied to a particular machine.

You log in with your UTORid and UTORid password. There is no separate lab
password. From off campus you need to use UTorVPN.

## Two ways in

Most people use both at the same time.

### Remote desktop (for Gazebo, rviz2 and other windows)

1. Install an RDP client:
   - Windows: built in. Start menu, "Remote Desktop Connection" (`mstsc`).
   - macOS: "Windows App" (formerly Microsoft Remote Desktop) from the App Store.
   - Linux: `remmina`, or `xfreerdp /v:mn3110pc01.utm.utoronto.ca /u:<utorid> /dynamic-resolution`.
2. Connect to the machine's full hostname, e.g. `mn3110pc05.utm.utoronto.ca`. Accept the certificate warning the first
   time (the server uses a self-signed certificate).
3. At the login screen leave the session type as `Xorg`, enter your UTORid and
   password. You get your own Xfce desktop.
4. Open a terminal (right-click the desktop, "Open Terminal Here"). ROS 2 is
   already sourced in every shell.

**Screen size.** The server adopts whatever size the client asks for. In
Remmina set *Resolution* to "Use client resolution" and turn on *Dynamic
resolution update*; in Windows Remote Desktop use *Show Options, Display* and
drag the slider to full screen; in the macOS app edit the PC and set *Display*.

**Disconnecting keeps your session running.** Close the client and everything
(Gazebo, your terminals) keeps going; reconnect later and it is all still there.
Only "Log Out" from the Xfce menu ends the session. Do not lock the screen
inside the remote session.

### SSH and VS Code (for editing and terminals)

```bash
ssh <utorid>@mn3110pc01.utm.utoronto.ca
```

or, in VS Code, install the "Remote - SSH" extension, connect to
`<utorid>@mn3110pc01.utm.utoronto.ca`, and open the folder `~/csc477_ws`. The integrated
terminal runs on the lab machine with ROS 2 already sourced. Anything that opens
a window (Gazebo, rviz2) shows up in your remote desktop session if you have one
open.

## One-time setup in your account

```bash
rosdep update                                   # per-user rosdep cache
mkdir -p ~/csc477_ws/src && cd ~/csc477_ws/src
git clone https://github.com/csc477/assignment1.git
cd ~/csc477_ws && colcon build --symlink-install && source install/setup.bash
```

(`colcon` finds the package inside the clone on its own; there is no need to
move or link anything.)

New shells pick up the workspace automatically after this. The first
`ros2 launch wall_following_assignment gazebo_world.launch.py` creates
`~/clearpath/`, the simulator's scratch directory, and copies the robot
description into it. You never need to edit anything there.

Nothing is shared between students. Your workspace is your own copy, and your
ROS 2 nodes and topics are invisible to other students on the same machine
(each account gets its own `ROS_DOMAIN_ID` automatically).

## Running

Exactly as in the package README:

```bash
# remote desktop terminal 1
ros2 launch wall_following_assignment gazebo_world.launch.py world:=walls_one_sided
# terminal 2
ros2 launch wall_following_assignment wall_follower_cpp.launch.py
```

The Gazebo 3D view renders on the machine's GPU; how smooth it looks over
remote desktop depends on your network connection. If Gazebo shows a black 3D
view, try `\ros2 launch ...` (with a leading backslash) once, which bypasses the
GPU wrapper and renders in software, and tell the course staff.

## Recording the video for the submission

Record the remote desktop window on your own computer with any screen recorder
(OBS Studio, the built-in recorders in Windows and macOS, SimpleScreenRecorder
on Linux). Keep the file under the size limit given in the handout.

## Troubleshooting

- **Cannot log in over RDP, "login failed for display 0".** Your previous
  session is stuck. Log in over SSH and run `pkill -u $USER xfce4-session`, then
  try RDP again. If that does not help, contact the course staff.
- **Scan topic has two publishers or the simulation stalls.** Run
  `bash ~/csc477_ws/src/assignment1/scripts/teardown.sh` until it reports no
  survivors, then relaunch.
- **Everything is slow.** Check `top`; if several other students are simulating
  on the same machine, log in to a different one. Your files are already there.
