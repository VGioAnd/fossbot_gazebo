#!/usr/bin/env python3

import subprocess
import sys
import os
from pathlib import Path

def get_package_path():
    
    return str(Path(__file__).parent.parent.parent)

def clear_screen():
    
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    
    print("=" * 70)
    print(" " * 20 + "FOSSBOT GAZEBO SIMULATION")
    print("=" * 70)
    print(" " * 25 + "ROS2 Humble + Ignition Gazebo")
    print("=" * 70)

def print_menu():
    
    print("\n" + "-" * 70)
    print("ΜΕΝΟΥ ΕΠΙΛΟΓΩΝ:")
    print("-" * 70)
    print("""
  ╔══════════════════════════════════════════════════════════════════╗
  ║                         ΒΑΣΙΚΕΣ ΕΚΚΙΝΗΣΕΙΣ                       ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║  1.  reset            - Reset ROS2 processes                     ║
  ║  2.  sim              - Απλή προσομοίωση                         ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║                    SLAM Toolbox                                  ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║  3.  lidarmap         - SLAM Toolbox mapping με LiDAR            ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║                    RTAB-Map SLAM                                 ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║  4.  rtabmap          - RTAB-Map SLAM με LiDAR                   ║
  ║  5.  rtabcam          - RTAB-Map SLAM με κάμερα και LiDAR        ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║                     ΠΛΟΗΓΗΣΗ NAV2                                ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║  6.  nav2lidar        - πλοήγηση με LiDAR                        ║
  ║  7.  nav2uss          - πλοήγηση με ultrasonic και LiDAR         ║
  ║  8.  nav2rtab         - πλοήγηση με RTAB-Map με LiDAR            ║
  ║  9.  nav2cam          - πλοήγηση με RTAB-Map με κάμερα και LiDAR ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║                              ΕΞΟΔΟΣ                              ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║  0.  exit             - Έξοδος                                   ║
  ╚══════════════════════════════════════════════════════════════════╝
""")

def print_footer():
    
    print("-" * 70)
    print("Επιλέξτε έναν αριθμό (0-9) και πατήστε Enter")
    print("=" * 70)

def run_script(script_name):
    
    print("\n" + "=" * 70)
    print(f"Εκκίνηση: {script_name}")
    print("=" * 70)
    print("\nΠατήστε Ctrl+C για διακοπή...\n")
    
    try:
        cmd = ["ros2", "run", "fossbot_gazebo", script_name]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(f"\n\n[{script_name}] Διακόπηκε από τον χρήστη")
    except Exception as e:
        print(f"\nΣφάλμα κατά την εκτέλεση του {script_name}: {e}")
    
    input("\nΠατήστε Enter για επιστροφή στο μενού...")

def main():
    
    while True:
        clear_screen()
        print_header()
        print_menu()
        print_footer()
        
        choice = input("\nΕπιλογή: ").strip()
        
        
        scripts = {
            '1': 'reset',
            '2': 'sim',
            '3': 'lidarmap',     
            '4': 'rtabmap',      
            '5': 'rtabcam',      
            '6': 'nav2lidar',
            '7': 'nav2uss',
            '8': 'nav2rtab',
            '9': 'nav2cam',
        }
        
        if choice == '0' or choice.lower() == 'exit':
            print("\nΤερματισμός... Καλή συνέχεια! 🚀")
            break
        elif choice in scripts:
            run_script(scripts[choice])
        else:
            print("\n❌ Μη έγκυρη επιλογή! Παρακαλώ επιλέξτε 0-9")
            input("\nΠατήστε Enter για συνέχεια...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nΤερματισμός... Καλή συνέχεια! 🚀")
        sys.exit(0)