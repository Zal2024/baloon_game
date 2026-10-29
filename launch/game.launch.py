import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    params = os.path.join(
        get_package_share_directory('baloon_game'), 'config', 'params.yaml')

    return LaunchDescription([
        Node(
            package='baloon_game',
            executable='camera_node',
            name='camera_node',
            parameters=[params],
            output='screen',
        ),
        Node(
            package='baloon_game',
            executable='game_node',
            name='game_node',
            parameters=[params],
            output='screen',
        ),
    ])

