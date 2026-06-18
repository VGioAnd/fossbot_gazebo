#!/usr/bin/env python3

import subprocess
import time
import os
import sys
import shutil

def run_command(cmd, ignore_errors=False):
    """Εκτελεί μια εντολή στο σύστημα"""
    try:
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

def main():
    print("=" * 50)
    print("RESET - Starting ROS2 cleanup")
    print("=" * 50)
    
    # 1. Εκκίνηση ROS2 daemon
    print("\n[1/7] Starting ROS2 daemon...")
    run_command("ros2 daemon start", ignore_errors=True)
    
    # 2. Τερματισμός διαδικασιών (χωρίς το "ros2" για να μην σκοτώσει τον εαυτό του)
    print("\n[2/7] Killing ROS2 processes...")
    processes_to_kill = [
        "rviz2", "slam_toolbox", "nav2", 
        "robot_state_publisher", "rtabmap", "rgbd_odometry", "ekf"
    ]
    
    for proc in processes_to_kill:
        print(f"  - Killing: {proc}")
        run_command(f"pkill -f '{proc}'", ignore_errors=True)
    
    # 3. Για Ignition (αν τρέχει)
    print("\n[3/7] Killing Ignition/Gazebo processes...")
    run_command("pkill -f 'ignition'", ignore_errors=True)
    run_command("pkill -f 'ign gazebo'", ignore_errors=True)
    
    # 4. Για bridge
    print("\n[4/7] Killing bridges...")
    run_command("pkill -f 'parameter_bridge'", ignore_errors=True)
    
    # 5. ROS2 daemon reset
    print("\n[5/7] Resetting ROS2 daemon...")
    run_command("ros2 daemon stop", ignore_errors=True)
    time.sleep(2)
    
    # 6. Καθαρισμός υπολειμμάτων (διορθωμένο)
    print("\n[6/7] Cleaning cache files...")
    ros_cache = os.path.expanduser("~/.ros/rosdep/sources.cache")
    if os.path.exists(ros_cache):
        try:
            if os.path.isdir(ros_cache):
                shutil.rmtree(ros_cache)
                print(f"  - Removed cache directory: {ros_cache}")
            else:
                os.remove(ros_cache)
                print(f"  - Removed cache file: {ros_cache}")
        except Exception as e:
            print(f"  - Error removing cache: {e}")
    else:
        print("  - No cache found")
    
    # 7. Επανεκκίνηση daemon και τερματισμός nodes
    print("\n[7/7] Restarting daemon and killing nodes...")
    run_command("ros2 daemon start", ignore_errors=True)
    time.sleep(1)
    
    # Τερματισμός nodes αν υπάρχουν (εξαίρεση του εαυτού μας)
    result = run_command("ros2 node list", ignore_errors=True)
    if result and result.stdout:
        nodes = result.stdout.strip().split('\n')
        for node in nodes:
            if node.strip():
                print(f"  - Killing node: {node}")
                run_command(f"ros2 node kill '{node}'", ignore_errors=True)
    else:
        print("  - No active nodes found")
    
    time.sleep(1)
    
    print("\n" + "=" * 50)
    print("✓ RESET OK - Cleanup completed successfully")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nReset interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
