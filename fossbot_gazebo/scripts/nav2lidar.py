#!/usr/bin/env python3

import subprocess
import time
import os
import sys
from pathlib import Path

def get_package_path():
    return str(Path(__file__).resolve().parent.parent.parent)

def run_command(cmd, ignore_errors=False, background=False, show_output=True):
    try:
        if background:
            if isinstance(cmd, str):
                if show_output:
                    process = subprocess.Popen(cmd, shell=True)
                else:
                    process = subprocess.Popen(cmd, shell=True, 
                                               stdout=subprocess.DEVNULL, 
                                               stderr=subprocess.DEVNULL)
            else:
                if show_output:
                    process = subprocess.Popen(cmd)
                else:
                    process = subprocess.Popen(cmd, 
                                               stdout=subprocess.DEVNULL, 
                                               stderr=subprocess.DEVNULL)
            return process
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if not ignore_errors and result.returncode != 0:
                print(f"Warning: Command failed: {cmd}")
                if result.stderr:
                    print(f"  Error: {result.stderr.strip()}")
            return result
    except Exception as e:
        if not ignore_errors:
            print(f"Error executing command: {e}")
        return None

def check_reset_warning():
    print("=" * 60)
    print("WARNING: Reset is recommended before starting!")
    print("=" * 60)
    print("\nIt is highly recommended to run the reset option first")
    print("to avoid conflicts with existing ROS2 processes.\n")
    print("You can run reset by:")
    print("  • Option 1 from the main menu")
    print("  • Or execute: ros2 run fossbot_gazebo reset\n")
    print("-" * 60)
    print("Press Enter to continue without reset, or Ctrl+C to cancel...")
    input()
    print("Continuing without reset...\n")

def fix_map_path_in_yaml(yaml_file_path, map_path):

    import re
    
    print(f"  Fixing map path in: {yaml_file_path}")
    print(f"  New map path: {map_path}")
    
    with open(yaml_file_path, 'r') as f:
        content = f.read()

    pattern = r'(    yaml_filename:\s*).*$'
    replacement = r'\1"{}"'.format(map_path)
    
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if new_content == content:
        pattern = r'(yaml_filename:\s*).*$'
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    with open(yaml_file_path, 'w') as f:
        f.write(new_content)
    
    print("  ✓ Map path fixed in YAML file")
    return True

    
def main():
    print("=" * 60)
    print("STARTING FOSSBOT SIMULATION WITH NAV2 (LIDAR)")
    print("=" * 60)
    
    package_path = get_package_path()
    inner_path = os.path.join(package_path, "fossbot_gazebo")
    model_path = os.path.join(inner_path, "models", "fossbot")
    world_path = os.path.join(inner_path, "worlds", "obstacles.world")
    urdf_path = os.path.join(model_path, "model.urdf")
    sdf_path = os.path.join(model_path, "model.sdf")
    
    sim_rviz_config = os.path.join(inner_path, "config", "sim.rviz")
    rviz_config = os.path.join(inner_path, "config", "nav2lidar.rviz")
    map_path = os.path.join(inner_path, "maps", "lidarmap.yaml")
    nav2_params = os.path.join(inner_path, "params", "nav2lidar.yaml")
    
    if not os.path.exists(world_path):
        print(f"ERROR: World file not found: {world_path}")
        sys.exit(1)
    if not os.path.exists(sdf_path):
        print(f"ERROR: SDF file not found: {sdf_path}")
        sys.exit(1)
    if not os.path.exists(urdf_path):
        print(f"ERROR: URDF file not found: {urdf_path}")
        sys.exit(1)
    if not os.path.exists(map_path):
        print(f"ERROR: Map file not found: {map_path}")
        sys.exit(1)
    if not os.path.exists(nav2_params):
        print(f"ERROR: NAV2 params file not found: {nav2_params}")
        sys.exit(1)

    
    # 1. Προειδοποίηση για reset
    check_reset_warning()
    
    # 2. Export ROS parameters
    print("\n>>> Step 2: Setting environment variables...")
    os.environ['ROS_PARAM_USE_SIM_TIME'] = 'true'
    os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'
    print("  - ROS_PARAM_USE_SIM_TIME=true")
    print("  - LIBGL_ALWAYS_SOFTWARE=1")
    
    # 3. Εκκίνηση Ignition Gazebo
    print("\n>>> Step 3: Starting Ignition Gazebo...")
    ign_process = run_command(
        f"ign gazebo -r {world_path}",
        background=True,
        show_output=True
    )
    print(f"  - Ignition Gazebo started with world: {world_path}")
    time.sleep(5)
    
    # 4. Create model in world
    print("\n>>> Step 4: Creating Fossbot model in world...")
    run_command(
        f'ign service -s /world/default/create '
        f'--reqtype ignition.msgs.EntityFactory '
        f'--reptype ignition.msgs.Boolean '
        f'--timeout 5000 '
        f'--req \'sdf_filename: "{sdf_path}"\'',
        ignore_errors=True,
        show_output=False
    )
    print(f"  - Fossbot model created from: {sdf_path}")
    
    # 5. ROS-GZ Bridge
    print("\n>>> Step 5: Starting ROS-GZ Bridge...")
    bridge_process = run_command(
        'ros2 run ros_gz_bridge parameter_bridge '
        '/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU '
        '/ultrasonic@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan '
        '/color_image@sensor_msgs/msg/Image[ignition.msgs.Image '
        '/depth_image@sensor_msgs/msg/Image[ignition.msgs.Image '
        '/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo '
        '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist '
        '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan '
        '/model/fossbot/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry '
        '/model/fossbot/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V '
        '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock '
        '--ros-args '
        '-r /model/fossbot/tf:=/tf '
        '-r /model/fossbot/odometry:=/odom '
        '-p use_sim_time:=true',
        background=True,
        show_output=True
    )
    print("  - ROS-GZ Bridge started")
    
    # 6. Robot State Publisher
    print("\n>>> Step 6: Starting Robot State Publisher...")
    rsp_process = None
    try:
        with open(urdf_path, 'r') as f:
            robot_description = f.read()
        
        cmd = [
            'ros2', 'run', 'robot_state_publisher', 'robot_state_publisher',
            '--ros-args',
            '-p', f'robot_description:={robot_description}',
            '-p', 'use_sim_time:=true',
            '-p', 'publish_frequency:=30.0',
            '-p', 'frame_prefix:=fossbot/'
        ]
        
        rsp_process = subprocess.Popen(cmd)
        print("  - Robot State Publisher started successfully")
    except Exception as e:
        print(f"  - Error starting Robot State Publisher: {e}")
        rsp_process = None
    
    # 6.5 Static Transform Publisher (map → odom) - Προσωρινό μέχρι το initial pose
    print("\n>>> Step 6.1: Starting Static Transform Publisher (map → fossbot/odom)...")
    static_tf_cmd = [
        'ros2', 'run', 'tf2_ros', 'static_transform_publisher',
        '0', '0', '0', '0', '0', '0',
        'map', 'fossbot/odom'
    ]
    static_tf_process = subprocess.Popen(static_tf_cmd,
                                          stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL)
    print("  - Static Transform Publisher started (will be overridden by AMCL after initial pose)")
    time.sleep(1)
    
    # 7. Εκκίνηση Navigation2
    print("\n>>> Step 7: Starting Navigation2...")
    print("\n>>> Step: Updating map path in YAML...")
    fix_map_path_in_yaml(nav2_params, map_path)
    time.sleep(10)
    print(f"  - Using map: {map_path}")
    print(f"  - Using params: {nav2_params}")
    
    nav2_process = run_command(
        f'ros2 launch nav2_bringup bringup_launch.py '
        f'use_sim_time:=true '
        f'localization:=true '
        f'map:={map_path} '
        f'params_file:={nav2_params}',
        background=True,
        show_output=True
    )
    print("  - Navigation2 started")
    time.sleep(5)
    
    # 8. Εκκίνηση RVIZ2 για NAV2
    print("\n>>> Step 8: Starting RVIZ2 for NAV2...")

    if os.path.exists(rviz_config):
        rviz_process = run_command(f"rviz2 -d {rviz_config}", background=True)
        print(f"  - RVIZ2 for NAV2 started with config: {rviz_config}")
    else:
        rviz_process = run_command("rviz2", background=True, show_output=True)
        print("  - RVIZ2 for NAV2 started with default config")
        print(f"    (Expected config at: {rviz_config})")
    
    time.sleep(5)
    
    # 9. Τελικές οδηγίες
    print("\n" + "=" * 60)
    print("SIMULATION WITH NAV2 (LIDAR) STARTED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nPackage: fossbot_gazebo")
    print(f"World: {world_path}")
    print(f"Map: {map_path}")
    print(f"NAV2 Params: {nav2_params}")
    print(f"RViz Config: {rviz_config if os.path.exists(rviz_config) else 'Default'}")
    
    print("\n" + "=" * 60)
    print("IMPORTANT: INITIAL POSE REQUIRED FOR NAVIGATION!")
    print("=" * 60)
    print("\nYou MUST set the robot's initial position on the map:")
    print("")
    print("  1. In the RVIZ2 window, locate the toolbar at the top")
    print("  2. Click the '2D Pose Estimate' button (arrow with green circle)")
    print("  3. Click on the map where the robot is located")
    print("  4. Drag to set the initial orientation (direction the robot is facing)")
    
    print("\n" + "-" * 60)
    print("NAVIGATION COMMANDS :")
    print("-" * 60)
    print("\n1. Click '2D Goal Pose' in RVIZ2 toolbar")
    print("2. Click on the map where you want the robot to go")
    print("3. Drag to set the desired orientation at the goal")
    
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the simulation when done")
    print("=" * 60)
    
    # 10. Διατήρηση processes
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down simulation...")
        processes = [ign_process, bridge_process, nav2_process, rviz_process, static_tf_process]
        if rsp_process:
            processes.append(rsp_process)
        
        for proc in processes:
            if proc:
                proc.terminate()
                time.sleep(0.5)
                if proc.poll() is None:
                    proc.kill()
        
        print("Simulation stopped")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)