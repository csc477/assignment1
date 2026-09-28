import filecmp
import os
import shutil
import tempfile
from pathlib import Path

from ament_index_python.packages import get_package_prefix, get_package_share_directory
from clearpath_config.clearpath_config import ClearpathConfig
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction,
                            SetEnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

SPAWN_X, SPAWN_Y, SPAWN_Z = '-3.0', '2.0', '0.3'
SPAWN_YAW = '0.0'

# NOTE on world resolution: this file reproduces clearpath_gz's
# gz_sim.launch.py (see below), including how it builds
# IGN_GAZEBO_RESOURCE_PATH: `<clearpath_gz share>/worlds` plus `<prefix>/share`
# for every entry in AMENT_PREFIX_PATH. Gazebo resolves the `world` argument
# (with .sdf appended) as a bare filename against that path, which is why
# CMakeLists.txt installs the world .sdf files a second time directly under
# this package's bare share/ prefix (in addition to the canonical
# share/wall_following_assignment/worlds/ copy used elsewhere).

# NOTE on setup_path: clearpath_gz reads the robot description from
# `<setup_path>/robot.yaml` and writes its generated URDF/launch/config
# files into the same directory, so setup_path is Clearpath's scratch
# directory, not part of this package. This package's config/robot.yaml is
# the source of truth for the course robot; seed_setup_path() below copies
# it into setup_path on every launch (creating the directory if needed), so
# students never have to set anything up by hand.
DEFAULT_SETUP_PATH = Path.home() / 'clearpath'

# NOTE on the Gazebo GUI: clearpath_gz's simulation.launch.py includes its own
# gz_sim.launch.py, which starts Gazebo with a hard-coded `--gui-config`
# (clearpath_gz/config/gui.config, with the Teleop topic patched in). Gazebo
# ignores the world file's <gui> block when a config file is given, so the
# only way to add the "Reset pose to start" button below the Teleop panel is
# to hand Gazebo our own config. We therefore do what gz_sim.launch.py does
# (resource path, `ign gazebo` via ros_gz_sim, clock bridge) with one
# addition: build_gui_config() appends this package's ResetPose GUI plugin
# after Teleop, and IGN_GUI_PLUGIN_PATH is pointed at where CMake installs it.
# robot_spawn.launch.py is still clearpath's, included unchanged.
TELEOP_MARKER = '<plugin filename="Teleop">'

RESET_POSE_PLUGIN = """\
<plugin filename="ResetPose" name="Reset pose">
    <ignition-gui>
        <title>Reset pose</title>
        <property key="state" type="string">docked</property>
        <property key="showCloseButton" type="bool">false</property>
        <property key="showDockButton" type="bool">false</property>
        <property key="cardMinimumWidth" type="int">400</property>
        <property key="cardMinimumHeight" type="int">90</property>
    </ignition-gui>
    <world>{world}</world>
    <model>{model}</model>
    <pose>{x} {y} {z} 0 0 {yaw}</pose>
</plugin>
"""


def build_gui_config(template, teleop_topic, world, model, pose):
    """Return a Gazebo GUI config: clearpath's template plus the ResetPose button.

    `template` is the text of clearpath_gz/config/gui.config. The Teleop topic
    is injected exactly the way clearpath's gz_sim.launch.py does it, and a
    ResetPose plugin block is appended last so that Gazebo docks it directly
    below the Teleop panel. `pose` is (x, y, z, yaw) in metres/radians.
    """
    if TELEOP_MARKER not in template:
        raise ValueError('GUI config template has no Teleop plugin to anchor the '
                         'ResetPose button under; clearpath_gz layout changed?')
    x, y, z, yaw = pose
    out = template.replace(TELEOP_MARKER, f'{TELEOP_MARKER}\n    <topic>{teleop_topic}</topic>', 1)
    return out.rstrip() + '\n' + RESET_POSE_PLUGIN.format(world=world, model=model,
                                                           x=x, y=y, z=z, yaw=yaw)


def seed_setup_path(setup_path):
    """Ensure <setup_path>/robot.yaml is this package's config/robot.yaml.

    Creates the directory if missing and (re)copies the file whenever it is
    absent or differs from the package copy. Returns the destination path.
    """
    setup_path = Path(setup_path).expanduser()
    src = Path(get_package_share_directory('wall_following_assignment')) / 'config' / 'robot.yaml'
    dst = setup_path / 'robot.yaml'
    setup_path.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or not filecmp.cmp(src, dst, shallow=False):
        shutil.copyfile(src, dst)
    return dst


def _simulation_actions(context):
    setup_path = LaunchConfiguration('setup_path').perform(context)
    world = LaunchConfiguration('world').perform(context)
    robot_yaml = seed_setup_path(setup_path)

    # Same naming rules as clearpath_gz's gz_sim/robot_spawn launch files.
    namespace = ClearpathConfig(str(robot_yaml)).system.namespace
    if namespace in ('', '/'):
        teleop_topic, robot_name = '/cmd_vel', 'robot'
    else:
        teleop_topic, robot_name = f'/{namespace}/cmd_vel', f'{namespace}/robot'

    clearpath_gz = get_package_share_directory('clearpath_gz')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')
    own_prefix = get_package_prefix('wall_following_assignment')

    template = (Path(clearpath_gz) / 'config' / 'gui.config').read_text()
    gui_config = build_gui_config(template, teleop_topic, world, robot_name,
                                  (SPAWN_X, SPAWN_Y, SPAWN_Z, SPAWN_YAW))
    with tempfile.NamedTemporaryFile('w', prefix='csc477_gui_', suffix='.config',
                                     delete=False) as tmp:
        tmp.write(gui_config)
    gui_config_path = tmp.name

    packages_paths = [os.path.join(p, 'share')
                      for p in os.environ.get('AMENT_PREFIX_PATH', '').split(':') if p]
    resource_path = ':'.join([os.path.join(clearpath_gz, 'worlds'), *packages_paths])

    plugin_dir = os.path.join(own_prefix, 'lib', 'wall_following_assignment', 'gui_plugins')
    gui_plugin_path = ':'.join(p for p in [plugin_dir, os.environ.get('IGN_GUI_PLUGIN_PATH')] if p)

    return [
        SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', resource_path),
        SetEnvironmentVariable('IGN_GUI_PLUGIN_PATH', gui_plugin_path),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(Path(ros_gz_sim) / 'launch' / 'gz_sim.launch.py')),
            launch_arguments={
                'gz_args': f'{world}.sdf -r -v 4 --gui-config {gui_config_path}',
            }.items()),
        Node(package='ros_gz_bridge', executable='parameter_bridge', name='clock_bridge',
             output='screen',
             arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock']),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(Path(clearpath_gz) / 'launch' / 'robot_spawn.launch.py')),
            launch_arguments={
                'use_sim_time': 'true',
                'setup_path': setup_path,
                'world': world,
                'rviz': LaunchConfiguration('rviz'),
                'x': SPAWN_X, 'y': SPAWN_Y, 'z': SPAWN_Z, 'yaw': SPAWN_YAW,
            }.items()),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='walls_one_sided',
                              description='walls_one_sided | walls_two_sided | walls_two_sided_tight'),
        DeclareLaunchArgument('rviz', default_value='false'),
        DeclareLaunchArgument('setup_path', default_value=str(DEFAULT_SETUP_PATH),
                              description="Clearpath scratch dir; robot.yaml is seeded into it "
                                          "from this package's config/ on every launch"),
        OpaqueFunction(function=_simulation_actions),
        Node(package='tf2_ros', executable='static_transform_publisher',
             name='map_to_odom', output='screen',
             arguments=['--x', SPAWN_X, '--y', SPAWN_Y, '--z', '0.0',
                        '--frame-id', 'map', '--child-frame-id', 'odom']),
    ])
