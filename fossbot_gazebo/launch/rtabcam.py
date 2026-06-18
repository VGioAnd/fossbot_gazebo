from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
import sys
from pathlib import Path

def get_package_path():
    return str(Path(__file__).resolve().parent.parent.parent)
    
def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    localization = LaunchConfiguration('localization')
    
    package_path = get_package_path()
    inner_path = os.path.join(package_path, "fossbot_gazebo")
    maps_dir = os.path.join(inner_path, "maps")
    database_path = os.path.join(maps_dir, 'rtabcam.db')

    parameters={
          'frame_id':'fossbot/base_footprint',
          'map_frame_id': 'map',
          'use_sim_time':use_sim_time,
          'subscribe_depth':True,
          'subscribe_scan':False,
          'use_action_for_goal':False,
          'Reg/Force3DoF':'true',
          'Grid/RayTracing':'true',
          'Grid/3D':'false',
          'Grid/RangeMax':'4.0',
          'Grid/FromDepth':'true',
          'Grid/CellSize': '0.05',
          'Grid/NormalsSegmentation':'true',
          'Grid/MaxGroundHeight':'0.20',
          'proj_max_ground_angle': '45',
          'Grid/MaxObstacleHeight':'2.0', 
          'Optimizer/GravitySigma':'0',
          'Grid/NoiseFilteringRadius': '0.2',
          'Grid/NoiseFilteringMinNeighbors': '2',
          'Grid/FlatObstacleDetectedMaxGroundAngle': '15',
          'Grid/ProjMaxGroundAngle': '15',
          'Rtabmap/DetectionRate': '2.0',      
   
          'RGBD/LinearUpdate': '0.05',         
          'RGBD/AngularUpdate': '0.02',      
    
          'Rtabmap/TimeThr': '700',             
          'Rtabmap/ImageBufferSize': '1',      
          'database_path': database_path
    }

    remappings=[
          ('rgb/image', '/color_image'),
          ('rgb/camera_info', '/camera_info'),
          ('depth/image', '/depth_image'),
          ('odom','/odom')]

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use simulation (Gazebo) clock if true'),
        
        DeclareLaunchArgument(
            'localization', default_value='false',
            description='Launch in localization mode.'),

        Node(
            condition=UnlessCondition(localization),
            package='rtabmap_slam', executable='rtabmap', output='screen',
            parameters=[parameters],
            remappings=remappings,
            arguments=['-d']),
            
        Node(
            condition=IfCondition(localization),
            package='rtabmap_slam', executable='rtabmap', output='screen',
            parameters=[parameters,
              {'Mem/IncrementalMemory':'False',
               'Mem/InitWMWithAllNodes':'True'}],
            remappings=remappings),

        Node(
            package='rtabmap_viz', executable='rtabmap_viz', output='screen',
            parameters=[parameters],
            remappings=remappings)
        
    ])
