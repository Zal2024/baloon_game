from setuptools import find_packages, setup

package_name = 'baloon_game'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/game.launch.py']),
        ('share/' + package_name + '/config', ['config/params.yaml']),
        ('share/' + package_name + '/models', ['models/latest.pt']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='fazal',
    maintainer_email='fazal@example.com',
    description='Balloon game with camera_node and game_node',
    license='MIT',
    entry_points={
        'console_scripts': [
            'camera_node = baloon_game.camera_node:main',
            'game_node = baloon_game.game_node:main',
        ],
    },
)

