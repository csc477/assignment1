from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='wall_following_assignment',
             executable='wall_follower.py',
             name='wall_follower',
             output='screen',
             parameters=[{'forward_speed': 1.0,
                          'desired_distance_from_wall': 1.0}]),
    ])
