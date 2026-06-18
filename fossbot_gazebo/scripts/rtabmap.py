#!/usr/bin/env python3

import subprocess
import time
import os
import sys
from pathlib import Path
from datetime import datetime

def get_package_path():
    return str(Path(__file__).resolve().parent.parent.parent)

def run_command(cmd, ignore_errors=False, background=False):
    try:
        if background:
            if isinstance(cmd, str):
                process = subprocess.Popen(cmd, shell=True, 
                                           stdout=subprocess.DEVNULL, 
                                           stderr=subprocess.DEVNULL)
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

def main():
    print("=" * 60)
    print("STARTING FOSSBOT SIMULATION WITH RTAB-MAP (LIDAR)")
    print("=" * 60)
    
    package_path = get_package_path()
    inner_path = os.path.join(package_path, "fossbot_gazebo")
    model_path = os.path.join(inner_path, "models", "fossbot")
    world_path = os.path.join(inner_path, "worlds", "obstacles.world")
    urdf_path = os.path.join(model_path, "model.urdf")
    sdf_path = os.path.join(model_path, "model.sdf")
    
    rtabmap_launch = os.path.join(inner_path, "launch", "rtabmap.py")
    rviz_config = os.path.join(inner_path, "config", "sim.rviz")
    rtabmap_rviz_config = os.path.join(inner_path, "config", "rtabmap.rviz")
    maps_dir = os.path.join(inner_path, "maps")
    
    os.makedirs(maps_dir, exist_ok=True)

    if not os.path.exists(world_path):
        print(f"ERROR: World file not found: {world_path}")
        sys.exit(1)
    if not os.path.exists(sdf_path):
        print(f"ERROR: SDF file not found: {sdf_path}")
        sys.exit(1)
    if not os.path.exists(urdf_path):
        print(f"ERROR: URDF file not found: {urdf_path}")
        sys.exit(1)
    if not os.path.exists(rtabmap_launch):
        print(f"ERROR: RTAB-Map launch file not found: {rtabmap_launch}")
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
        background=True
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
        ignore_errors=True
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
        background=True
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
        
        rsp_process = subprocess.Popen(cmd, 
                                       stdout=subprocess.DEVNULL, 
                                       stderr=subprocess.DEVNULL)
        print("  - Robot State Publisher started successfully")
    except Exception as e:
        print(f"  - Error starting Robot State Publisher: {e}")
        rsp_process = None
    
    # 7. RTAB-Map
    print("\n>>> Step 7: Starting RTAB-Map with LiDAR...")
    rtabmap_process = run_command(
        f'ros2 launch {rtabmap_launch} use_sim_time:=true localization:=false',
        background=True
    )
    print(f"  - RTAB-Map started with launch file: {rtabmap_launch}")
    time.sleep(15)
    
    # 8. RVIZ2
    print("\n>>> Step 8: Starting RVIZ2...")
    if os.path.exists(rviz_config):
        rviz_process = run_command(f"rviz2 -d {rviz_config}", background=True)
        print(f"  - RVIZ2 started with sim.rviz")
    else:
        rviz_process = run_command("rviz2", background=True)
        print("  - RVIZ2 started with default config")
    
    # 9. Εμφάνιση οδηγιών
    print("\n" + "=" * 60)
    print("✓ SIMULATION WITH RTAB-MAP (LIDAR) STARTED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nPackage: fossbot_gazebo")
    print(f"World: {world_path}")
    print(f"RTAB-Map Launch: {rtabmap_launch}")
    print(f"Maps Directory: {maps_dir}")
    
    print("\n" + "-" * 60)
    print("TELEOPERATION COMMANDS:")
    print("-" * 60)
    print("\nΓια τηλεχειρισμό χρησιμοποίησε το χειριστήριο του Gazebo")
    print("\nή εκτέλεσε την εντολή:")
    print("  ros2 run teleop_twist_keyboard teleop_twist_keyboard")
    print("\nή δώσε τιμές στο x για κίνηση και στο z για στροφή:")
    print('  ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.5}}"')
    
    print("\n" + "-" * 60)
    print("RTAB-MAP COMMANDS:")
    print("-" * 60)
    print("\nΓια backup του χάρτη:")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"  cp {maps_dir}/rtabmap.db {maps_dir}/rtabmap_map_{timestamp}.db")
    
    print("\nΓια μετατροπή του χάρτη για NAV2:")
    print(f"Μετά την ολοκλήρωση της χαρτογράφησης και το κλείσιμο εκτέλειτε την εντολή")
    print(f"  rtabmap-databaseViewer {maps_dir}/rtabmap.db")
    print(f"Και στον Viewer FILE->EXPORT OPTIMIZED 2D MAP")
    print(f"Αποθήκευση του χάρτη με το όνομα rtabmap.pgm")
    print(f"ώστε να υπάρχει συμβατότητα με το πρόγραμμα nav2rtab")
    
    print("\n" + "-" * 60)
    print("📌 INSTRUCTIONS FOR RTAB-MAP VISUALIZATION:")
    print("-" * 60)
    print(f"\n1. In RVIZ2, go to: File -> Open Config")
    print(f"2. Navigate to: {rtabmap_rviz_config}")
    print("3. Select rtabmap.rviz and click Open")
    print("4. Move the robot in Gazebo and the created map will appear")
    
    print("Για διακοπή πατήστε Ctrl+C")
    
    
    # 10. Διατήρηση processes
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down simulation...")
        processes = [ign_process, bridge_process, rtabmap_process, rviz_process]
        if rsp_process:
            processes.append(rsp_process)
        
        for proc in processes:
            if proc:
                proc.terminate()
                time.sleep(0.5)
                if proc.poll() is None:
                    proc.kill()
        
        print("✓ Simulation stopped")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)