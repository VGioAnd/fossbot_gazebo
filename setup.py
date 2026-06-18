from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'fossbot_gazebo'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(include=['fossbot_gazebo', 'fossbot_gazebo.*']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Config files (RViz)
        (os.path.join('share', package_name, 'config'), 
         glob('fossbot_gazebo/config/*.rviz')),
        (os.path.join('share', package_name, 'config'), 
         glob('fossbot_gazebo/config/*.yaml')),
        # Params files
        (os.path.join('share', package_name, 'params'), 
         glob('fossbot_gazebo/params/*.yaml')),
        # Launch files
        (os.path.join('share', package_name, 'launch'), 
         glob('fossbot_gazebo/launch/*.py')),
        # World files
        (os.path.join('share', package_name, 'worlds'), 
         glob('fossbot_gazebo/worlds/*.world')),
        # Model files (URDF, SDF)
        (os.path.join('share', package_name, 'models', 'fossbot'), 
         glob('fossbot_gazebo/models/fossbot/*.urdf')),
        (os.path.join('share', package_name, 'models', 'fossbot'), 
         glob('fossbot_gazebo/models/fossbot/*.sdf')),
        # Mesh files
        (os.path.join('share', package_name, 'models', 'fossbot', 'meshes'), 
         glob('fossbot_gazebo/models/fossbot/meshes/*.stl')),
        (os.path.join('share', package_name, 'models', 'fossbot', 'meshes'), 
         glob('fossbot_gazebo/models/fossbot/meshes/*.dae')),
        # Maps directory
        (os.path.join('share', package_name, 'maps'), 
         glob('fossbot_gazebo/maps/*.yaml')),
        (os.path.join('share', package_name, 'maps'), 
         glob('fossbot_gazebo/maps/*.pgm')),
        (os.path.join('share', package_name, 'maps'), 
         glob('fossbot_gazebo/maps/*.db')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='VGioAnd',
    maintainer_email='andreadakisgiorgos@yahoo.com',
    description='Fossbot ROS2 Gazebo simulation with SLAM, NAV2, and RTAB-Map',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fossbot = fossbot_gazebo.scripts.fossbot_gazebo:main',
            'reset = fossbot_gazebo.scripts.reset:main',
            'sim = fossbot_gazebo.scripts.sim:main',
            'rtabmap = fossbot_gazebo.scripts.rtabmap:main',
            'rtabcam = fossbot_gazebo.scripts.rtabcam:main',
            'nav2uss = fossbot_gazebo.scripts.nav2uss:main',
            'nav2rtab = fossbot_gazebo.scripts.nav2rtab:main',
            'nav2lidar = fossbot_gazebo.scripts.nav2lidar:main',
            'nav2cam = fossbot_gazebo.scripts.nav2cam:main',
            'lidarmap = fossbot_gazebo.scripts.lidarmap:main',
        ],
    },
)
